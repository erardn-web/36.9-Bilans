import streamlit as st
from datetime import date
import pandas as pd

from utils.db import (
    get_all_patients, create_patient,
    get_patient_bilans_bpco, save_bilan_bpco, delete_bilan_bpco,
)
from utils.muscle_widget import render_muscle_tab
from utils.bpco_data import (
    MMRC_GRADES, CAT_ITEMS, CAT_KEYS, compute_cat,
    compute_bode, interpret_6mwt,
)

st.set_page_config(page_title="Bilan BPCO", page_icon="🫁", layout="wide")

st.markdown("""
<style>
.page-title{font-size:1.8rem;font-weight:700;color:#2B57A7;margin-bottom:.2rem;}
.patient-badge{background:#E8EEF9;border-left:4px solid #2B57A7;
    padding:.5rem 1rem;border-radius:6px;font-weight:600;margin-bottom:1rem;}
.section-title{font-size:1.1rem;font-weight:700;color:#C4603A;
    border-bottom:2px solid #C4603A;padding-bottom:.3rem;margin-bottom:.8rem;}
.score-box{background:#2B57A7;color:white;padding:.6rem 1rem;
    border-radius:8px;font-weight:600;margin:.5rem 0;}
.info-box{background:#E8EEF9;border-left:3px solid #2B57A7;
    padding:.5rem .8rem;border-radius:4px;font-size:.9rem;margin:.3rem 0;}
</style>
""", unsafe_allow_html=True)

for k, v in {
    "bp_mode": "accueil", "bp_patient_id": None, "bp_patient_info": None,
    "bp_bilan_id": None, "bp_bilan_data": {}, "bp_unsaved": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def lv(key, default=None):
    v = st.session_state.bp_bilan_data.get(key)
    return default if (v is None or str(v).strip() in ("","None")) else v
def lv_int(key, d=0):
    try: return int(float(lv(key, d)))
    except: return d
def lv_float_or_none(key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=float(v); return r if r!=0.0 else None
    except: return None
def lv_int_or_none(key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=int(float(v)); return r if r!=0 else None
    except: return None

# ─── Accueil ──────────────────────────────────────────────────────────────────
def render_accueil():
    st.markdown('<div class="page-title">🫁 Bilan BPCO</div>', unsafe_allow_html=True)

    # Bouton questionnaires vierges
    col_print, _ = st.columns([2, 5])
    with col_print:
        if st.button("🖨️ Imprimer questionnaires", key="bp_print_accueil"):
            st.session_state["bp_show_print_accueil"] = True

    if st.session_state.get("bp_show_print_accueil", False):
        with st.container():
            st.markdown("""<div style="background:#E8EEF9;border:2px solid #2B57A7;
                border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:1rem;">
                <span style="font-size:1.1rem;font-weight:700;color:#2B57A7;">
                🖨️ Questionnaires à imprimer (vierges)</span></div>""",
                unsafe_allow_html=True)
            bp1, bp2, bp3, bp4 = st.columns(4)
            with bp1: ba_mmrc = st.checkbox("😮‍💨 mMRC",         value=True, key="bp_acc_mmrc")
            with bp2: ba_cat  = st.checkbox("📋 CAT",            value=True, key="bp_acc_cat")
            with bp3: ba_6mwt = st.checkbox("🏃 6MWT",           value=True, key="bp_acc_6mwt")
            with bp4: ba_sts  = st.checkbox("🪑 STS",            value=True, key="bp_acc_sts")
            bp5, bp6, _ = st.columns([1, 1, 2])
            with bp5: ba_musc = st.checkbox("💪 Testing MI",     value=True, key="bp_acc_musc")
            with bp6: ba_lp   = st.checkbox("🏋️ 1RM Leg Press",  value=True, key="bp_acc_lp")
            sel_bp = (
                (["mmrc"]      if ba_mmrc else []) +
                (["cat"]       if ba_cat  else []) +
                (["6mwt"]      if ba_6mwt else []) +
                (["sts"]       if ba_sts  else []) +
                (["muscle"]    if ba_musc else []) +
                (["leg_press"] if ba_lp   else [])
            )
            ga, gb, _ = st.columns([1.5, 1, 4])
            with ga:
                if sel_bp:
                    from utils.bpco_pdf import generate_questionnaires_pdf as _gqb
                    with st.spinner("Génération…"):
                        q_pdf = _gqb(sel_bp, None)
                    st.download_button("📥 Télécharger", data=q_pdf,
                        file_name=f"questionnaires_bpco_vierges_{date.today()}.pdf",
                        mime="application/pdf", type="primary", key="bp_acc_dl")
                else:
                    st.warning("Sélectionnez au moins un questionnaire.")
            with gb:
                if st.button("✖ Fermer", key="bp_acc_close"):
                    st.session_state["bp_show_print_accueil"] = False; st.rerun()
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🔍 Rechercher un patient")
        df = get_all_patients()
        if df.empty: st.info("Aucun patient.")
        else:
            s = st.text_input("Nom ou prénom…", key="bp_search")
            filt = df
            if s:
                filt = df[df["nom"].str.contains(s.upper(),na=False)|
                          df["prenom"].str.contains(s.capitalize(),na=False)]
            if filt.empty: st.warning("Aucun résultat.")
            else:
                for _, row in filt.iterrows():
                    c1,c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**{row['nom']} {row['prenom']}** | "
                                    f"{row.get('date_naissance','—')} — `{row['patient_id']}`")
                    with c2:
                        if st.button("Sélectionner", key=f"bpsel_{row['patient_id']}"):
                            st.session_state.bp_patient_id   = row["patient_id"]
                            st.session_state.bp_patient_info = row.to_dict()
                            st.session_state.bp_mode         = "bilan"
                            st.rerun()
    with col_b:
        st.markdown("#### ➕ Nouveau patient")
        with st.form("bp_new_pat", clear_on_submit=True):
            nom=st.text_input("Nom *"); prenom=st.text_input("Prénom *")
            ddn=st.date_input("Date naissance *",min_value=date(1900,1,1),max_value=date.today())
            sexe=st.selectbox("Sexe",["Féminin","Masculin","Autre"])
            sub=st.form_submit_button("➕ Créer",type="primary")
        if sub:
            if not nom or not prenom: st.error("Nom et prénom obligatoires.")
            else:
                pid=create_patient(nom,prenom,ddn,sexe,"")
                df2=get_all_patients()
                row=df2[df2["patient_id"]==pid].iloc[0]
                st.session_state.bp_patient_id=pid
                st.session_state.bp_patient_info=row.to_dict()
                st.session_state.bp_mode="bilan"; st.rerun()

# ─── Sélection bilan ──────────────────────────────────────────────────────────
def render_bilan_selection():
    info=st.session_state.bp_patient_info
    bilans_df=get_patient_bilans_bpco(st.session_state.bp_patient_id)
    st.markdown(f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
                f'— {info.get("date_naissance","—")} — ID : {info["patient_id"]}</div>',
                unsafe_allow_html=True)
    sel_ids=st.session_state.get("bp_selected_ids",list(bilans_df["bilan_id"]) if not bilans_df.empty else [])
    st.session_state["bp_selected_ids"]=sel_ids

    def get_sel(df):
        f=df[df["bilan_id"].isin(sel_ids)] if sel_ids else df
        return f if not f.empty else df

    col_back,col_evol,col_pdf,col_print,_=st.columns([1,1,1.2,1.5,2])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            for k in ["bp_patient_id","bp_patient_info","bp_bilan_id"]: st.session_state[k]=None
            st.session_state.bp_bilan_data={}; st.session_state.pop("bp_selected_ids",None)
            st.session_state.bp_mode="accueil"; st.rerun()
    with col_evol:
        if not bilans_df.empty:
            if st.button("📈 Voir l'évolution",type="primary"):
                st.session_state.bp_mode="evolution"; st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            from utils.bpco_pdf import generate_pdf_bpco
            sel_df=get_sel(bilans_df)
            with st.spinner("PDF…"):
                pdf=generate_pdf_bpco(sel_df,info)
            st.download_button(f"📄 Exporter PDF ({len(sel_df)})",data=pdf,
                file_name=f"bpco_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf")
    with col_print:
        if st.button("🖨️ Imprimer questionnaires", key="bp_print_btn"):
            st.session_state["bp_show_print"] = True

    if st.session_state.get("bp_show_print", False):
        with st.container():
            st.markdown("""<div style="background:#E8EEF9;border:2px solid #2B57A7;
                border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:1rem;">
                <span style="font-size:1.1rem;font-weight:700;color:#2B57A7;">
                🖨️ Questionnaires à imprimer</span></div>""",
                unsafe_allow_html=True)
            bp1, bp2, bp3, bp4 = st.columns(4)
            with bp1: bpr_mmrc = st.checkbox("😮‍💨 mMRC",        value=True, key="bp_pr_mmrc")
            with bp2: bpr_cat  = st.checkbox("📋 CAT",           value=True, key="bp_pr_cat")
            with bp3: bpr_6mwt = st.checkbox("🏃 6MWT",          value=True, key="bp_pr_6mwt")
            with bp4: bpr_sts  = st.checkbox("🪑 STS",           value=True, key="bp_pr_sts")
            bp5, bp6, _ = st.columns([1, 1, 2])
            with bp5: bpr_musc = st.checkbox("💪 Testing MI",    value=True, key="bp_pr_musc")
            with bp6: bpr_lp   = st.checkbox("🏋️ 1RM Leg Press", value=True, key="bp_pr_lp")
            sel_bp = (
                (["mmrc"]      if bpr_mmrc else []) +
                (["cat"]       if bpr_cat  else []) +
                (["6mwt"]      if bpr_6mwt else []) +
                (["sts"]       if bpr_sts  else []) +
                (["muscle"]    if bpr_musc else []) +
                (["leg_press"] if bpr_lp   else [])
            )
            ga, gb, _ = st.columns([1.5, 1, 4])
            with ga:
                if sel_bp:
                    from utils.bpco_pdf import generate_questionnaires_pdf as _gqb
                    with st.spinner("Génération…"):
                        q_pdf = _gqb(sel_bp, info)
                    st.download_button("📥 Télécharger", data=q_pdf,
                        file_name=f"questionnaires_bpco_{info['nom']}_{date.today()}.pdf",
                        mime="application/pdf", type="primary", key="bp_dl_q")
                else:
                    st.warning("Sélectionnez au moins un questionnaire.")
            with gb:
                if st.button("✖ Fermer", key="bp_close_print"):
                    st.session_state["bp_show_print"] = False; st.rerun()

    st.markdown("---")
    col_left,col_right=st.columns(2)
    with col_left:
        st.markdown("#### 📋 Bilans existants")
        if bilans_df.empty: st.info("Aucun bilan.")
        else:
            new_sel=[]
            for _,row in bilans_df.iterrows():
                bid=row["bilan_id"]
                c_ck,c_info,c_open,c_del=st.columns([0.5,3.5,0.8,0.8])
                with c_ck:
                    if st.checkbox("",value=bid in sel_ids,key=f"bpck_{bid}",
                                   label_visibility="collapsed"): new_sel.append(bid)
                with c_info:
                    st.markdown(f"**{row.get('date_bilan','—')}** — {row.get('type_bilan','—')}"
                                f"  \n<small>`{bid}`</small>",unsafe_allow_html=True)
                with c_open:
                    if st.button("✏️",key=f"bpopen_{bid}",help="Ouvrir ce bilan"):
                        st.session_state.bp_bilan_id=bid
                        st.session_state.bp_bilan_data=row.to_dict()
                        st.session_state.bp_mode="formulaire"
                        st.session_state.bp_unsaved=False; st.rerun()
                with c_del:
                    if st.button("🗑️",key=f"bpdel_{bid}",help="Supprimer"):
                        st.session_state[f"bp_confirm_del_{bid}"]=True
                if st.session_state.get(f"bp_confirm_del_{bid}",False):
                    st.warning("⚠️ Supprimer définitivement ce bilan ?")
                    ca,cb,_=st.columns([1,1,3])
                    with ca:
                        if st.button("✅ Confirmer",key=f"bpdelok_{bid}",type="primary"):
                            delete_bilan_bpco(bid)
                            st.session_state.pop(f"bp_confirm_del_{bid}",None)
                            st.session_state["bp_selected_ids"]=[i for i in sel_ids if i!=bid]
                            st.rerun()
                    with cb:
                        if st.button("✖ Annuler",key=f"bpdelcancel_{bid}"):
                            st.session_state.pop(f"bp_confirm_del_{bid}",None); st.rerun()
            st.session_state["bp_selected_ids"]=new_sel
    with col_right:
        st.markdown("#### ➕ Nouveau bilan")
        with st.form("bp_new_bilan"):
            bilan_date=st.date_input("Date",value=date.today())
            bilan_type=st.selectbox("Type",["Bilan initial","Bilan intermédiaire","Bilan final"])
            praticien=st.text_input("Praticien")
            go=st.form_submit_button("➕ Créer",type="primary")
        if go:
            st.session_state.bp_bilan_id=None
            st.session_state.bp_bilan_data={"patient_id":st.session_state.bp_patient_id,
                "date_bilan":str(bilan_date),"type_bilan":bilan_type,"praticien":praticien}
            st.session_state.bp_mode="formulaire"; st.session_state.bp_unsaved=True; st.rerun()

# ─── Formulaire ───────────────────────────────────────────────────────────────



def highlight_filled_tabs(tab_definitions: list):
    """Fond vert sur les onglets remplis via CSS nth-child."""
    bd = st.session_state.get("bp_bilan_data", {})
    css_rules = []
    for i, (label, keys) in enumerate(tab_definitions):
        filled = any(
            str(bd.get(k, "")).strip() not in ("", "0", "0.0", "None", "nan")
            and bd.get(k) is not None
            for k in keys
        )
        if filled:
            n = i + 1
            css_rules.append(
                "[data-baseweb=\'tab-list\'] button:nth-child("
                + str(n)
                + ") {background-color:#d4edda !important;"
                  "border-bottom:3px solid #388e3c !important;}"
            )
    if css_rules:
        st.markdown(
            "<style>" + " ".join(css_rules) + "</style>",
            unsafe_allow_html=True
        )

def render_formulaire():
    info=st.session_state.bp_patient_info; bd=st.session_state.bp_bilan_data
    st.markdown(f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
                f'— {bd.get("type_bilan","—")} du {bd.get("date_bilan","—")}</div>',
                unsafe_allow_html=True)
    col_back,col_save,_=st.columns([1,1,4])
    with col_back:
        if st.button("⬅️ Retour"):
            if not st.session_state.get("bp_just_saved",False):
                st.session_state["bp_confirm_back"]=True
            else:
                st.session_state.pop("bp_just_saved",None)
                st.session_state.bp_mode="bilan"; st.rerun()
    with col_save:
        save_top=st.button("💾 Sauvegarder",type="primary")
    if st.session_state.get("bp_confirm_back",False):
        st.warning("⚠️ **Modifications non sauvegardées.** Quitter sans sauvegarder ?")
        ca,cb,_=st.columns([1.5,1.5,4])
        with ca:
            if st.button("🚪 Quitter sans sauvegarder",type="primary",key="bp_back_ok"):
                st.session_state["bp_confirm_back"]=False
                st.session_state.bp_mode="bilan"; st.rerun()
        with cb:
            if st.button("✏️ Continuer l'édition",key="bp_back_cancel"):
                st.session_state["bp_confirm_back"]=False; st.rerun()
    st.markdown("---")
    collected=dict(st.session_state.bp_bilan_data)
    highlight_filled_tabs([
        ("📝 Général",        []),
        ("🌬️ Spirométrie",   ["spiro_vems","spiro_vems_pct"]),
        ("🏃 6MWT",          ["mwt_distance"]),
        ("🪑 STS 1min",      ["sts_1min_reps"]),
        ("😮‍💨 mMRC",   ["mmrc_grade"]),
        ("📋 CAT",           ["cat_score"]),
        ("📊 BODE",          ["bode_score"]),
        ("💪 Testing",       ["musc_hip_flex_d","musc_knee_ext_d"]),
        ("🏋️ 1RM Leg Press", ["lp_1rm_estime"]),
    ])

    tab_gen,tab_spiro,tab_mwt,tab_sts,tab_mmrc,tab_cat,tab_bode,tab_musc,tab_lp = st.tabs([
        "📝 Général","🌬️ Spirométrie","🏃 6MWT","🪑 STS 1min",
        "😮‍💨 mMRC","📋 CAT","📊 BODE","💪 Testing","🏋️ 1RM Leg Press",
    ])

    # ── GÉNÉRAL ───────────────────────────────────────────────────────────────
    with tab_gen:
        st.markdown('<div class="section-title">Informations générales</div>',unsafe_allow_html=True)
        g1,g2=st.columns(2)
        with g1:
            bd_date=st.date_input("Date",value=pd.to_datetime(lv("date_bilan",str(date.today()))))
            bd_type=st.selectbox("Type",["Bilan initial","Bilan intermédiaire","Bilan final"],
                index=["Bilan initial","Bilan intermédiaire","Bilan final"].index(
                    lv("type_bilan","Bilan initial")) if lv("type_bilan") else 0)
        with g2:
            prat=st.text_input("Praticien",value=lv("praticien",""),key="bp_prat")
            notes=st.text_area("Notes",value=lv("notes_generales",""),height=80)
        g3,g4=st.columns(2)
        with g3:
            poids=st.number_input("Poids (kg)",0.0,250.0,lv_float_or_none("poids"),0.5,
                                  key="bp_poids",help="0 = non mesuré")
        with g4:
            taille=st.number_input("Taille (cm)",0.0,220.0,lv_float_or_none("taille"),0.5,
                                   key="bp_taille",help="0 = non mesuré")
        bmi=None
        if poids and taille and poids>0 and taille>0:
            bmi=round(poids/(taille/100)**2,1)
            st.metric("IMC",f"{bmi} kg/m²")
        collected.update({"date_bilan":str(bd_date),"type_bilan":bd_type,"praticien":prat,
                          "notes_generales":notes,"poids":poids or "","taille":taille or "",
                          "bmi":bmi or ""})

    # ── SPIROMÉTRIE ───────────────────────────────────────────────────────────
    with tab_spiro:
        st.markdown('<div class="section-title">Spirométrie</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-box">Valeurs post-bronchodilatateur si disponibles.</div>',
                    unsafe_allow_html=True)
        s1,s2=st.columns(2)
        with s1:
            vems=st.number_input("VEMS (L)",0.0,8.0,lv_float_or_none("spiro_vems"),0.01,
                                 key="sp_vems",help="Volume Expiratoire Maximal Seconde")
            cvf=st.number_input("CVF (L)",0.0,10.0,lv_float_or_none("spiro_cvf"),0.01,
                                key="sp_cvf",help="Capacité Vitale Forcée")
            ratio=st.number_input("VEMS/CVF (%)",0.0,100.0,lv_float_or_none("spiro_ratio"),0.1,
                                  key="sp_ratio")
        with s2:
            vems_pct=st.number_input("VEMS % prédit",0.0,200.0,lv_float_or_none("spiro_vems_pct"),0.1,
                                     key="sp_vems_pct")
            cvf_pct=st.number_input("CVF % prédit",0.0,200.0,lv_float_or_none("spiro_cvf_pct"),0.1,
                                    key="sp_cvf_pct")
            gold_opts=["— Non renseigné —","GOLD 1 (léger ≥ 80%)","GOLD 2 (modéré 50–79%)",
                       "GOLD 3 (sévère 30–49%)","GOLD 4 (très sévère < 30%)"]
            stored_gold=lv("spiro_gold","— Non renseigné —")
            gold=st.selectbox("Stade GOLD",gold_opts,
                index=gold_opts.index(stored_gold) if stored_gold in gold_opts else 0)
        if vems_pct and vems_pct>0:
            if vems_pct>=80:   gc,gi="#388e3c","GOLD 1 — Léger"
            elif vems_pct>=50: gc,gi="#f57c00","GOLD 2 — Modéré"
            elif vems_pct>=30: gc,gi="#e64a19","GOLD 3 — Sévère"
            else:              gc,gi="#d32f2f","GOLD 4 — Très sévère"
            st.markdown(f'<div class="score-box" style="background:{gc};">'
                        f'VEMS {vems_pct}% prédit → {gi}</div>',unsafe_allow_html=True)
        spo2_r=st.number_input("SpO₂ repos (%)",0.0,100.0,lv_float_or_none("spo2_repos"),0.1,
                                key="sp_spo2r",help="0 = non mesuré")
        spiro_notes=st.text_area("Notes spirométrie",value=lv("spiro_notes",""),height=60,key="sp_notes")
        collected.update({"spiro_vems":vems or "","spiro_cvf":cvf or "","spiro_ratio":ratio or "",
            "spiro_vems_pct":vems_pct or "","spiro_cvf_pct":cvf_pct or "",
            "spiro_gold":"" if gold=="— Non renseigné —" else gold,
            "spo2_repos":spo2_r or "","spiro_notes":spiro_notes})

    # ── 6MWT ──────────────────────────────────────────────────────────────────
    with tab_mwt:
        st.markdown('<div class="section-title">Test de marche de 6 minutes (6MWT)</div>',
                    unsafe_allow_html=True)
        m1,m2=st.columns(2)
        with m1:
            st.markdown("**Avant**")
            spo2_av=st.number_input("SpO₂ avant (%)",0.0,100.0,lv_float_or_none("mwt_spo2_avant"),0.1,key="mwt_s1")
            fc_av=st.number_input("FC avant (bpm)",0,250,lv_int_or_none("mwt_fc_avant"),1,key="mwt_f1")
            dysp_av=st.select_slider("Dyspnée avant (Borg 0–10)",
                options=[None,0,1,2,3,4,5,6,7,8,9,10],
                value=lv_int_or_none("mwt_dyspnee_avant"),
                format_func=lambda x: "—" if x is None else str(x), key="mwt_d1")
            fat_av=st.select_slider("Fatigue avant (Borg 0–10)",
                options=[None,0,1,2,3,4,5,6,7,8,9,10],
                value=lv_int_or_none("mwt_fatigue_avant"),
                format_func=lambda x: "—" if x is None else str(x), key="mwt_fa1")
        with m2:
            st.markdown("**Après**")
            spo2_ap=st.number_input("SpO₂ après (%)",0.0,100.0,lv_float_or_none("mwt_spo2_apres"),0.1,key="mwt_s2")
            spo2_min=st.number_input("SpO₂ min (%)",0.0,100.0,lv_float_or_none("mwt_spo2_min"),0.1,key="mwt_s3",help="SpO₂ minimale pendant le test")
            fc_ap=st.number_input("FC après (bpm)",0,250,lv_int_or_none("mwt_fc_apres"),1,key="mwt_f2")
            dysp_ap=st.select_slider("Dyspnée après (Borg 0–10)",
                options=[None,0,1,2,3,4,5,6,7,8,9,10],
                value=lv_int_or_none("mwt_dyspnee_apres"),
                format_func=lambda x: "—" if x is None else str(x), key="mwt_d2")
            fat_ap=st.select_slider("Fatigue après (Borg 0–10)",
                options=[None,0,1,2,3,4,5,6,7,8,9,10],
                value=lv_int_or_none("mwt_fatigue_apres"),
                format_func=lambda x: "—" if x is None else str(x), key="mwt_fa2")
        dist=st.number_input("Distance parcourue (mètres)",0,1000,lv_int_or_none("mwt_distance"),1,
                             key="mwt_dist",help="0 = non réalisé")
        aide_opts=["Aucune","Canne","Déambulateur","Oxygène","Autre"]
        # Charger valeurs existantes (stockées comme "Canne|Oxygène")
        stored_aide = lv("mwt_aide_technique","")
        default_aide = [x for x in str(stored_aide).split("|") if x in aide_opts] if stored_aide else []
        mwt_aides = st.multiselect("Aide(s) technique(s)", aide_opts,
                                   default=default_aide, key="mwt_aide_multi")
        mwt_aide_val = "|".join(mwt_aides) if mwt_aides else ""
        mwt_inc=st.text_area("Incidents / arrêts",value=lv("mwt_incidents",""),height=50,key="mwt_inc")
        mwt_interp=""
        if dist and dist>0:
            r6=interpret_6mwt(dist)
            mwt_interp=r6["interpretation"]
            st.markdown(f'<div class="score-box" style="background:{r6["color"]};">'
                        f'6MWT : {dist} m — {mwt_interp}</div>',unsafe_allow_html=True)
        collected.update({"mwt_distance":dist or "","mwt_spo2_avant":spo2_av or "",
            "mwt_spo2_apres":spo2_ap or "","mwt_spo2_min":spo2_min or "",
            "mwt_fc_avant":fc_av or "","mwt_fc_apres":fc_ap or "",
            "mwt_dyspnee_avant":"" if dysp_av is None else dysp_av,
            "mwt_dyspnee_apres":"" if dysp_ap is None else dysp_ap,
            "mwt_fatigue_avant":"" if fat_av is None else fat_av,
            "mwt_fatigue_apres":"" if fat_ap is None else fat_ap,
            "mwt_aide_technique":mwt_aide_val,
            "mwt_incidents":mwt_inc,"mwt_interpretation":mwt_interp,
            "spo2_effort":spo2_ap or "","spo2_min_effort":spo2_min or ""})

    # ── STS 1 MIN ─────────────────────────────────────────────────────────────
    with tab_sts:
        st.markdown('<div class="section-title">STS — Sit to Stand 1 minute</div>',
                    unsafe_allow_html=True)
        sts=st.number_input("Répétitions / minute",0,60,lv_int_or_none("sts_1min_reps"),1,
                            key="bp_sts",help="0 = non réalisé")
        sts_interp=""
        if sts and sts>0:
            if sts>=25:   sc,sts_interp="#388e3c","Bonne capacité (≥ 25)"
            elif sts>=20: sc,sts_interp="#f57c00","Capacité modérée (20–24)"
            elif sts>=15: sc,sts_interp="#e64a19","Capacité limitée (15–19)"
            else:         sc,sts_interp="#d32f2f","Capacité très limitée (< 15)"
            st.markdown(f'<div class="score-box" style="background:{sc};">'
                        f'{sts} rép/min — {sts_interp}</div>',unsafe_allow_html=True)
        collected.update({"sts_1min_reps":sts or "","sts_1min_interpretation":sts_interp})

    # ── mMRC ──────────────────────────────────────────────────────────────────
    with tab_mmrc:
        st.markdown('<div class="section-title">mMRC — Dyspnée</div>',unsafe_allow_html=True)
        mmrc_opts=["— Non renseigné —"] + [f"Grade {g} — {d}" for g,d in MMRC_GRADES]
        stored_mmrc=lv("mmrc_grade","")
        mmrc_idx=0
        if stored_mmrc != "":
            try:
                g=int(float(stored_mmrc))
                mmrc_idx=g+1
            except: pass
        mmrc_chosen=st.radio("Grade mMRC",mmrc_opts,index=mmrc_idx,key="bp_mmrc")
        mmrc_val=""
        if mmrc_chosen!="— Non renseigné —":
            mmrc_val=int(mmrc_chosen.split(" ")[1])
            colors=["#388e3c","#8bc34a","#f57c00","#e64a19","#d32f2f"]
            st.markdown(f'<div class="score-box" style="background:{colors[mmrc_val]};">'
                        f'mMRC Grade {mmrc_val}</div>',unsafe_allow_html=True)
        collected["mmrc_grade"]=mmrc_val

    # ── CAT ───────────────────────────────────────────────────────────────────
    with tab_cat:
        st.markdown('<div class="section-title">CAT — COPD Assessment Test</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">8 questions, chacune de 0 à 5. '
                    'Seuils : 0–10 faible · 11–20 modéré · 21–30 sévère · 31–40 très sévère</div>',
                    unsafe_allow_html=True)
        cat_answers={}
        for key,left,right in CAT_ITEMS:
            num=int(key.split("_")[1])
            stored=lv(key,"")
            opts=[None,0,1,2,3,4,5]
            def fmt(x,l=left,r=right):
                if x is None: return "— Non renseigné —"
                if x==0: return f"0 — {l}"
                if x==5: return f"5 — {r}"
                return str(x)
            default_v=None if stored=="" else int(float(stored))
            # Afficher le texte des deux pôles avant le slider
            st.markdown(
                f"**Question {num}**  \n"
                f"<small style='color:#2B57A7'>0 — {left}</small>"
                f"<small style='color:#888'> &nbsp;···&nbsp; </small>"
                f"<small style='color:#C4603A'>5 — {right}</small>",
                unsafe_allow_html=True)
            chosen=st.select_slider(
                label=f"Q{num}",
                options=opts,
                value=default_v,
                format_func=fmt,
                key=f"cat_{key}",
                label_visibility="collapsed")
            if chosen is not None:
                cat_answers[key]=chosen; collected[key]=chosen
            else:
                collected[key]=""
            st.markdown("")
            if chosen is not None:
                cat_answers[key]=chosen; collected[key]=chosen
            else:
                collected[key]=""
        cat_r=compute_cat(cat_answers)
        if cat_r["score"] is not None:
            st.markdown("---")
            st.markdown(f'<div class="score-box" style="background:{cat_r["color"]};">'
                        f'CAT : {cat_r["score"]}/40 — {cat_r["interpretation"]}</div>',
                        unsafe_allow_html=True)
        collected.update({"cat_score":cat_r["score"] if cat_r["score"] is not None else "",
                          "cat_interpretation":cat_r["interpretation"]})

    # ── BODE ──────────────────────────────────────────────────────────────────
    with tab_bode:
        st.markdown('<div class="section-title">BODE Index (0–10)</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-box">Calculé automatiquement à partir des données saisies '
                    '(VEMS%, mMRC, 6MWT, IMC). Complétez les onglets correspondants d\'abord.</div>',
                    unsafe_allow_html=True)
        bmi_val=lv_float_or_none("bmi") or (collected.get("bmi") if collected.get("bmi") else None)
        fev1_val=lv_float_or_none("spiro_vems_pct") or (float(collected.get("spiro_vems_pct",0)) if collected.get("spiro_vems_pct") else None)
        mmrc_val2=lv_int_or_none("mmrc_grade") or (int(float(collected.get("mmrc_grade",0))) if collected.get("mmrc_grade") else None)
        dist_val=lv_int_or_none("mwt_distance") or (int(float(collected.get("mwt_distance",0))) if collected.get("mwt_distance") else None)

        c1,c2,c3,c4=st.columns(4)
        with c1: st.metric("VEMS % prédit", f"{fev1_val}%" if fev1_val else "—")
        with c2: st.metric("mMRC", str(mmrc_val2) if mmrc_val2 is not None else "—")
        with c3: st.metric("6MWT", f"{dist_val} m" if dist_val else "—")
        with c4: st.metric("IMC", f"{bmi_val}" if bmi_val else "—")

        if any(v is not None for v in [fev1_val,mmrc_val2,dist_val,bmi_val]):
            bode_r=compute_bode(fev1_val,mmrc_val2,dist_val,bmi_val)
            st.markdown(f'<div class="score-box" style="background:{bode_r["color"]};">'
                        f'BODE : {bode_r["score"]}/10 — {bode_r["interpretation"]}'
                        f'  <small>({bode_r["survival"]})</small></div>',unsafe_allow_html=True)
            collected.update({"bode_score":bode_r["score"],"bode_interpretation":bode_r["interpretation"]})

    # ── TESTING MUSCULAIRE ───────────────────────────────────────────────────
    with tab_musc:
        musc_collected = render_muscle_tab(
            lv_fn=lv,
            key_prefix="bp",
            show_leg_press=False,
        )
        collected.update(musc_collected)

    # ── 1RM LEG PRESS ────────────────────────────────────────────────────────
    with tab_lp:
        lp_collected = render_muscle_tab(
            lv_fn=lv,
            key_prefix="bp_lp",
            leg_press_only=True,
            body_weight_key="poids",
            bilan_data=st.session_state.bp_bilan_data,
        )
        for k in ["lp_charge_kg","lp_reps","lp_1rm_estime","lp_interpretation","lp_notes"]:
            if k in lp_collected:
                collected[k] = lp_collected[k]


    # ── SAUVEGARDE ────────────────────────────────────────────────────────────
    if save_top or st.button("💾 Sauvegarder le bilan",type="primary",key="bp_save_bot"):
        final={**st.session_state.bp_bilan_data,**collected,
               "patient_id":st.session_state.bp_patient_id}
        if st.session_state.bp_bilan_id: final["bilan_id"]=st.session_state.bp_bilan_id
        with st.spinner("Enregistrement…"):
            new_id=save_bilan_bpco(final)
        st.session_state.bp_bilan_id=new_id; final["bilan_id"]=new_id
        st.session_state.bp_bilan_data=final
        st.session_state.bp_just_saved=True; st.session_state.bp_unsaved=False
        st.success(f"✅ Bilan sauvegardé ! (ID : {new_id})"); st.balloons()

# ─── Évolution ────────────────────────────────────────────────────────────────
def render_evolution():
    info=st.session_state.bp_patient_info
    all_df=get_patient_bilans_bpco(st.session_state.bp_patient_id)
    sel=st.session_state.get("bp_selected_ids",None)
    bilans_df=all_df[all_df["bilan_id"].isin(sel)] if sel else all_df
    if bilans_df.empty: bilans_df=all_df

    st.markdown(f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
                f'— Évolution BPCO</div>',unsafe_allow_html=True)
    n_sel,n_tot=len(bilans_df),len(all_df)
    if n_sel<n_tot: st.info(f"ℹ️ {n_sel}/{n_tot} bilans sélectionnés.")

    col_back,col_pdf,_=st.columns([1,1.5,4])
    with col_back:
        if st.button("⬅️ Retour"):
            st.session_state.bp_mode="bilan"; st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            from utils.bpco_pdf import generate_pdf_bpco
            with st.spinner("PDF…"):
                pdf=generate_pdf_bpco(bilans_df,info,analyse_text=__import__("utils.db",fromlist=["load_analyse"]).load_analyse(st.session_state.bp_patient_id,"bpco"))
            st.download_button(f"📄 PDF ({n_sel})",data=pdf,
                file_name=f"evolution_bpco_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf",type="primary")
    st.markdown("---")
    if bilans_df.empty: st.info("Aucun bilan."); return

    bilans_df=bilans_df.copy()
    bilans_df["date_bilan"]=pd.to_datetime(bilans_df["date_bilan"],errors="coerce")
    bilans_df=bilans_df.sort_values("date_bilan").reset_index(drop=True)
    labels=[f"{r['date_bilan'].strftime('%d/%m/%y')} – {r.get('type_bilan','')}"
            for _,r in bilans_df.iterrows()]

    def sn(v):
        try: r=float(v); return r if r!=0 else None
        except: return None

    import plotly.graph_objects as go
    tab_ai,tab_scores,tab_spiro_ev,tab_mwt_ev,tab_mmrc_ev,tab_cat_ev,tab_testing_ev,tab_detail = st.tabs([
        "🤖 Synthèse IA","📊 Scores","🌬️ Spirométrie","🏃 6MWT","😮‍💨 mMRC","📋 CAT","💪 Testing MI","📋 Détail"
    ])

    with tab_scores:
        fig=go.Figure()
        for name,key,color,denom in [
            ("6MWT (m)","mwt_distance","#2B57A7","m"),
            ("STS 1min","sts_1min_reps","#C4603A","rép"),
            ("CAT /40","cat_score","#f57c00","/40"),
            ("VEMS % prédit","spiro_vems_pct","#388e3c","%"),
            ("BODE /10","bode_score","#7b1fa2","/10"),
        ]:
            vals=[sn(r.get(key)) for _,r in bilans_df.iterrows()]
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]
            yp=[v for v in vals if v is not None]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=name,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[str(int(v)) for v in yp],textposition="top center"))
        fig.update_layout(height=400,legend=dict(orientation="h",y=-0.2),
                          xaxis_title="Bilan",plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)

        synth={"Bilan":labels}
        for name,key in [("6MWT (m)","mwt_distance"),("STS 1min","sts_1min_reps"),
                         ("mMRC","mmrc_grade"),("CAT /40","cat_score"),
                         ("VEMS %","spiro_vems_pct"),("SpO₂ repos","spo2_repos"),
                         ("BODE","bode_score")]:
            synth[name]=[str(int(float(v))) if sn(r.get(key)) is not None else "—"
                         for _,r in bilans_df.iterrows()
                         for v in [r.get(key,"")]]
        st.dataframe(pd.DataFrame(synth),use_container_width=True,hide_index=True)

    # ── SPIROMÉTRIE ──────────────────────────────────────────────────────────
    with tab_spiro_ev:
        st.markdown('<div class="section-title">🌬️ Évolution — Spirométrie</div>', unsafe_allow_html=True)
        fig_sp = go.Figure()
        for name, key, color in [
            ("VEMS (L)", "spiro_vems", "#2B57A7"),
            ("CVF (L)",  "spiro_cvf",  "#C4603A"),
            ("VEMS % prédit", "spiro_vems_pct", "#388e3c"),
        ]:
            vals = [sn(r.get(key)) for _, r in bilans_df.iterrows()]
            xp = [labels[i] for i,v in enumerate(vals) if v is not None]
            yp = [v for v in vals if v is not None]
            if xp:
                fig_sp.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                    name=name, line=dict(color=color, width=2.5), marker=dict(size=9),
                    text=[f"{v:.1f}" for v in yp], textposition="top center"))
        fig_sp.update_layout(height=350, legend=dict(orientation="h", y=-0.2),
                             plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_sp, use_container_width=True)
        spiro_rows = [{"Bilan": lbl, "VEMS (L)": r.get("spiro_vems","—"),
            "CVF (L)": r.get("spiro_cvf","—"), "VEMS %": r.get("spiro_vems_pct","—"),
            "Ratio": r.get("spiro_ratio","—"), "GOLD": r.get("spiro_gold","—")}
            for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(spiro_rows), use_container_width=True, hide_index=True)

    # ── 6MWT ─────────────────────────────────────────────────────────────────
    with tab_mwt_ev:
        st.markdown('<div class="section-title">🏃 Évolution — 6MWT</div>', unsafe_allow_html=True)
        fig_mwt = go.Figure()
        dist_vals = [sn(r.get("mwt_distance")) for _, r in bilans_df.iterrows()]
        xp = [labels[i] for i,v in enumerate(dist_vals) if v is not None]
        yp = [v for v in dist_vals if v is not None]
        if xp:
            fig_mwt.add_trace(go.Bar(x=xp, y=yp, name="Distance (m)",
                marker_color="#2B57A7", text=[f"{int(v)} m" for v in yp], textposition="outside"))
        fig_mwt.add_hline(y=400, line_dash="dot", line_color="#388e3c",
                          annotation_text="400 m (bon pronostic)")
        fig_mwt.add_hline(y=150, line_dash="dot", line_color="#d32f2f",
                          annotation_text="150 m (très limité)")
        fig_mwt.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white",
                              yaxis_title="Distance (m)")
        st.plotly_chart(fig_mwt, use_container_width=True)
        mwt_rows = [{"Bilan": lbl, "Distance (m)": r.get("mwt_distance","—"),
            "SpO₂ avant": r.get("mwt_spo2_avant","—"), "SpO₂ après": r.get("mwt_spo2_apres","—"),
            "SpO₂ min": r.get("mwt_spo2_min","—"), "FC avant": r.get("mwt_fc_avant","—"),
            "FC après": r.get("mwt_fc_apres","—"), "Aide": r.get("mwt_aide_technique","—")}
            for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(mwt_rows), use_container_width=True, hide_index=True)

    # ── mMRC ─────────────────────────────────────────────────────────────────
    with tab_mmrc_ev:
        st.markdown('<div class="section-title">😮‍💨 Évolution — mMRC</div>', unsafe_allow_html=True)
        from utils.bpco_data import MMRC_GRADES
        mmrc_rows = [{"Bilan": lbl,
            "Grade": r.get("mmrc_grade","—"),
            "Description": next((d for g,d in MMRC_GRADES
                if str(g)==str(r.get("mmrc_grade",""))), "—")}
            for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(mmrc_rows), use_container_width=True, hide_index=True)

    # ── CAT ──────────────────────────────────────────────────────────────────
    with tab_cat_ev:
        st.markdown('<div class="section-title">📋 Évolution — CAT</div>', unsafe_allow_html=True)
        fig_cat = go.Figure()
        cat_vals = [sn(r.get("cat_score")) for _, r in bilans_df.iterrows()]
        xp = [labels[i] for i,v in enumerate(cat_vals) if v is not None]
        yp = [v for v in cat_vals if v is not None]
        if xp:
            fig_cat.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                name="CAT", line=dict(color="#f57c00", width=2.5), marker=dict(size=9),
                text=[f"{int(v)}/40" for v in yp], textposition="top center"))
        for threshold, color, label in [(10,"#388e3c","≤10 faible"),(20,"#f57c00","20 modéré"),(30,"#d32f2f","30 sévère")]:
            fig_cat.add_hline(y=threshold, line_dash="dot", line_color=color, annotation_text=label)
        fig_cat.update_layout(height=350, yaxis=dict(range=[0,42], title="Score CAT /40"),
                              plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_cat, use_container_width=True)

    # ── TESTING MUSCULAIRE ────────────────────────────────────────────────────
    with tab_testing_ev:
        st.markdown('<div class="section-title">💪 Évolution — Testing musculaire MI</div>', unsafe_allow_html=True)
        from utils.muscle_data import MUSCLE_GROUPS, get_muscle_key
        musc_rows = []
        for lbl, (_, row) in zip(labels, bilans_df.iterrows()):
            rd = {"Bilan": lbl}
            for key_sfx, label_m, _ in MUSCLE_GROUPS:
                for side in ["d","g"]:
                    k = get_muscle_key(key_sfx, side)
                    v = row.get(k,"")
                    rd[f"{label_m[:10]} {'D' if side=='d' else 'G'}"] =                         str(int(float(v))) if str(v).strip() not in ("","None") else "—"
            musc_rows.append(rd)
        st.dataframe(pd.DataFrame(musc_rows), use_container_width=True, hide_index=True)

    with tab_detail:
        for i,(_,row) in enumerate(bilans_df.iterrows()):
            with st.expander(f"Bilan {i+1} — {labels[i]}"):
                c1,c2,c3=st.columns(3)
                with c1:
                    st.metric("6MWT",f"{row.get('mwt_distance','—')} m")
                    st.metric("VEMS %",f"{row.get('spiro_vems_pct','—')} %")
                with c2:
                    st.metric("CAT",f"{row.get('cat_score','—')}/40")
                    st.metric("mMRC",f"Grade {row.get('mmrc_grade','—')}")
                with c3:
                    st.metric("BODE",f"{row.get('bode_score','—')}/10")
                    st.metric("STS 1min",f"{row.get('sts_1min_reps','—')} rép")
                if row.get("notes_generales"):
                    st.markdown(f"*{row['notes_generales']}*")
    # ── ANALYSE IA ───────────────────────────────────────────────────────────
    with tab_ai:
        from utils.ai_analyse import render_analyse_section
        render_analyse_section(bilans_df, info, "bpco", st.session_state.bp_patient_id)


# ─── Router ───────────────────────────────────────────────────────────────────
mode=st.session_state.bp_mode
if mode=="accueil":      render_accueil()
elif mode=="bilan":      render_bilan_selection()
elif mode=="formulaire": render_formulaire()
elif mode=="evolution":  render_evolution()
