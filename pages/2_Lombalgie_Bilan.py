"""
Page : Bilan Lombalgie — Formulaire SOAP complet
"""

import streamlit as st
import pandas as pd
from datetime import date
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.google_sheets import (
    get_all_patients, create_patient,
    get_patient_bilans_lombalgie, save_bilan_lombalgie,
)
from utils.lombalgie_data import (
    GROUPES_CLINIQUES, GROUPES_OPTIONS, GROUPES_CODES,
    GROUPES_DESC, GROUPES_COLORS,
    DRAPEAUX_ROUGES, DRAPEAUX_JAUNES,
    DIAG_DIFF, LOCALISATIONS,
    FACTEURS_AGGRAVANTS, FACTEURS_SOULAGEANTS,
    TYPES_DOULEUR, RYTHME_DOULEUR,
    TESTS_CLINIQUES, RESULTATS_TEST,
)
from utils.questionnaires_lombalgie import generate_questionnaires_lombalgie_pdf

st.set_page_config(page_title="Bilan Lombalgie", page_icon="🦴",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .page-title{font-size:2rem;font-weight:700;color:#2e5a1c}
    .section-title{font-size:1.1rem;font-weight:600;color:#2e5a1c;
        border-bottom:2px solid #d0e8c0;padding-bottom:4px;margin-bottom:1rem}
    .score-box{border-radius:10px;padding:0.8rem;text-align:center;color:white;
        font-size:1.2rem;font-weight:700}
    .info-box{background:#f0f8e8;border-left:4px solid #2e5a1c;
        padding:0.8rem 1rem;border-radius:0 8px 8px 0;margin-bottom:1rem}
    .warn-box{background:#fff8e1;border-left:4px solid #f9a825;
        padding:0.8rem 1rem;border-radius:0 8px 8px 0;margin-bottom:1rem}
    .danger-box{background:#ffebee;border-left:4px solid #d32f2f;
        padding:0.8rem 1rem;border-radius:0 8px 8px 0;margin-bottom:1rem}
    .patient-badge{background:#2e5a1c;color:white;border-radius:8px;
        padding:0.4rem 1rem;display:inline-block;font-weight:600}
    .soap-label{font-size:1.3rem;font-weight:800;color:#2e5a1c}
</style>
""", unsafe_allow_html=True)


def init_state():
    for k, v in {"lomb_patient_id":None,"lomb_patient_info":None,
                  "lomb_bilan_id":None,"lomb_bilan_data":{},"lomb_mode":"accueil"}.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def lv(key, default=None):
    v = st.session_state.lomb_bilan_data.get(key)
    return default if (v is None or str(v).strip() in ("","None")) else v

def lv_int(key, default=0):
    try: return int(float(lv(key, default)))
    except: return default

def lv_float(key, default=0.0):
    try: return float(lv(key, default))
    except: return default

def lv_list(key):
    v = lv(key, "")
    return [x for x in str(v).split("|") if x] if v else []


def _render_print_panel(patient_info, key_prefix):
    st.markdown("""<div style="background:#f0f8e8;border:2px solid #2e5a1c;border-radius:10px;
        padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <span style="font-size:1.1rem;font-weight:700;color:#2e5a1c;">
        🖨️ Sélectionner les questionnaires à imprimer</span></div>""",
        unsafe_allow_html=True)
    p1,p2,p3 = st.columns(3)
    with p1: pr_odi   = st.checkbox("📊 Oswestry (ODI)",  value=True, key=f"{key_prefix}_odi")
    with p2: pr_tampa = st.checkbox("😨 Tampa Scale",      value=True, key=f"{key_prefix}_tampa")
    with p3: pr_oreb  = st.checkbox("🧠 Örebro",           value=True, key=f"{key_prefix}_orebro")
    selected = (["odi"] if pr_odi else []) + (["tampa"] if pr_tampa else []) + (["orebro"] if pr_oreb else [])
    ga,gb,_ = st.columns([1.5,1,4])
    with ga:
        if selected:
            with st.spinner("Génération…"):
                q_pdf = generate_questionnaires_lombalgie_pdf(selected, patient_info)
            fname = (f"questionnaires_lomb_{patient_info['nom']}_{patient_info['prenom']}_{date.today()}.pdf"
                     if patient_info else f"questionnaires_lomb_vierges_{date.today()}.pdf")
            st.download_button("📥 Télécharger le PDF", data=q_pdf, file_name=fname,
                               mime="application/pdf", type="primary", key=f"{key_prefix}_dl")
        else:
            st.warning("Sélectionnez au moins un questionnaire.")
    with gb:
        ck = "show_print_lomb_patient" if patient_info else "show_print_lomb_accueil"
        if st.button("✖ Fermer", key=f"{key_prefix}_close"):
            st.session_state[ck] = False
            st.rerun()


def render_accueil():
    st.markdown('<div class="page-title">🦴 Bilan Lombalgie</div>', unsafe_allow_html=True)
    st.markdown("##### Bilan physiothérapeutique — Lombalgie")
    col_t,col_b = st.columns([5,1])
    with col_b:
        if st.button("🖨️ Questionnaires vierges", key="print_lomb_accueil"):
            st.session_state["show_print_lomb_accueil"] = True
    st.markdown("---")
    if st.session_state.get("show_print_lomb_accueil", False):
        _render_print_panel(patient_info=None, key_prefix="acc")
    col_a,col_b2 = st.columns(2)
    with col_a:
        st.markdown("#### 🔍 Rechercher un patient")
        patients_df = get_all_patients()
        if patients_df.empty:
            st.info("Aucun patient enregistré.")
        else:
            search = st.text_input("Nom ou prénom…", key="lomb_search")
            filtered = patients_df
            if search:
                mask = (patients_df["nom"].str.contains(search.upper(), na=False) |
                        patients_df["prenom"].str.contains(search.capitalize(), na=False))
                filtered = patients_df[mask]
            if filtered.empty:
                st.warning("Aucun résultat.")
            else:
                for _, row in filtered.iterrows():
                    c1,c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**{row['nom']} {row['prenom']}** | {row.get('date_naissance','—')} — `{row['patient_id']}`",
                                    unsafe_allow_html=True)
                    with c2:
                        if st.button("Sélectionner", key=f"lsel_{row['patient_id']}"):
                            st.session_state.lomb_patient_id   = row["patient_id"]
                            st.session_state.lomb_patient_info = row.to_dict()
                            st.session_state.lomb_mode         = "bilan"
                            st.rerun()
    with col_b2:
        st.markdown("#### ➕ Nouveau patient")
        with st.form("lomb_new_pat", clear_on_submit=True):
            nom  = st.text_input("Nom *"); prenom = st.text_input("Prénom *")
            ddn  = st.date_input("Date de naissance *", min_value=date(1900,1,1), max_value=date.today())
            sexe = st.selectbox("Sexe", ["Féminin","Masculin","Autre"])
            prof = st.text_input("Profession")
            sub  = st.form_submit_button("Créer", type="primary")
        if sub:
            if not nom or not prenom: st.error("Nom et prénom obligatoires.")
            else:
                pid = create_patient(nom, prenom, ddn, sexe, prof)
                df2 = get_all_patients()
                row = df2[df2["patient_id"]==pid].iloc[0]
                st.session_state.lomb_patient_id   = pid
                st.session_state.lomb_patient_info = row.to_dict()
                st.session_state.lomb_mode         = "bilan"
                st.rerun()


def render_bilan_selection():
    info      = st.session_state.lomb_patient_info
    bilans_df = get_patient_bilans_lombalgie(st.session_state.lomb_patient_id)
    st.markdown(f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} — {info.get("date_naissance","—")} — ID : {info["patient_id"]}</div>',
                unsafe_allow_html=True)
    st.markdown("")
    col_back,col_print,_ = st.columns([1,1.5,4])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            for k in ["lomb_patient_id","lomb_patient_info","lomb_bilan_id"]:
                st.session_state[k] = None
            st.session_state.lomb_bilan_data = {}
            st.session_state.lomb_mode = "accueil"
            st.rerun()
    with col_print:
        if st.button("🖨️ Imprimer questionnaires", key="print_lomb_pat_btn"):
            st.session_state["show_print_lomb_patient"] = True
    if st.session_state.get("show_print_lomb_patient", False):
        _render_print_panel(patient_info=info, key_prefix="pat")
    st.markdown("---")
    col_left,col_right = st.columns(2)
    with col_left:
        st.markdown("#### 📋 Bilans existants")
        if bilans_df.empty:
            st.info("Aucun bilan pour ce patient.")
        else:
            for _, row in bilans_df.iterrows():
                c1,c2 = st.columns([3,1])
                with c1:
                    g = row.get("groupe_clinique","—") or "—"
                    st.markdown(f"**{row.get('date_bilan','—')}** — {row.get('type_bilan','—')} | Groupe : **{g}** | `{row.get('bilan_id','—')}`",
                                unsafe_allow_html=True)
                with c2:
                    if st.button("Ouvrir", key=f"lopen_{row['bilan_id']}"):
                        st.session_state.lomb_bilan_id   = row["bilan_id"]
                        st.session_state.lomb_bilan_data = row.to_dict()
                        st.session_state.lomb_mode       = "formulaire"
                        st.rerun()
    with col_right:
        st.markdown("#### ➕ Nouveau bilan")
        with st.form("lomb_new_bilan"):
            bilan_date = st.date_input("Date du bilan", value=date.today())
            bilan_type = st.selectbox("Type", ["Bilan initial","Bilan intermédiaire","Bilan final"])
            praticien  = st.text_input("Praticien")
            go_btn     = st.form_submit_button("Créer le bilan", type="primary")
        if go_btn:
            st.session_state.lomb_bilan_id   = None
            st.session_state.lomb_bilan_data = {"patient_id": st.session_state.lomb_patient_id,
                "date_bilan": str(bilan_date), "type_bilan": bilan_type, "praticien": praticien}
            st.session_state.lomb_mode = "formulaire"
            st.rerun()


def render_formulaire():
    info = st.session_state.lomb_patient_info
    bd   = st.session_state.lomb_bilan_data
    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— {bd.get("type_bilan","—")} du {bd.get("date_bilan","—")}</div>',
        unsafe_allow_html=True)
    st.markdown("")
    col_back, col_save, _ = st.columns([1,1,4])
    with col_back:
        if st.button("⬅️ Retour"):
            st.session_state.lomb_mode = "bilan"
            st.rerun()
    with col_save:
        save_top = st.button("💾 Sauvegarder", type="primary")
    st.markdown("---")
    collected = {}

    tab_gen, tab_s, tab_flags, tab_o, tab_diag, tab_a, tab_p, tab_q = st.tabs([
        "📝 Général", "🟦 S – Subjectif", "🚩 Drapeaux",
        "🔬 O – Objectif", "🩺 Diagnostics", "💡 A – Appréciation",
        "📋 P – Plan", "📊 Questionnaires",
    ])

    # ── GÉNÉRAL ──────────────────────────────────────────────────────────────
    with tab_gen:
        st.markdown('<div class="section-title">📝 Informations générales</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            bilan_date = st.date_input("Date du bilan",
                value=date.fromisoformat(bd.get("date_bilan", str(date.today()))), key="lg_date")
            bilan_type = st.selectbox("Type de bilan",
                ["Bilan initial","Bilan intermédiaire","Bilan final"],
                index=["Bilan initial","Bilan intermédiaire","Bilan final"].index(
                    bd.get("type_bilan","Bilan initial")), key="lg_type")
        with c2:
            praticien = st.text_input("Praticien", value=lv("praticien",""), key="lg_prat")
            notes_gen = st.text_area("Notes générales", value=lv("notes_generales",""), height=100, key="lg_notes")
        st.markdown("---")
        st.markdown('<div class="section-title">🏷️ Classification clinique</div>', unsafe_allow_html=True)
        groupe_stored = lv("groupe_clinique","—")
        groupe_idx    = GROUPES_CODES.index(groupe_stored) if groupe_stored in GROUPES_CODES else 0
        groupe_chosen = st.selectbox("Groupe clinique", GROUPES_OPTIONS, index=groupe_idx, key="lg_groupe")
        groupe_code   = GROUPES_CODES[GROUPES_OPTIONS.index(groupe_chosen)]
        if groupe_code != "—":
            color = GROUPES_COLORS[groupe_code]
            st.markdown(
                f'<div class="score-box" style="background:{color};font-size:1rem;padding:0.8rem;">'
                f'{groupe_chosen}<br><small style="font-size:0.8rem;font-weight:400;">'
                f'{GROUPES_DESC[groupe_code]}</small></div>',
                unsafe_allow_html=True)
        collected.update({"date_bilan":str(bilan_date),"type_bilan":bilan_type,
                          "praticien":praticien,"notes_generales":notes_gen,"groupe_clinique":groupe_code})

    # ── SUBJECTIF ─────────────────────────────────────────────────────────────
    with tab_s:
        st.markdown('<div class="soap-label">S — Subjectif</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="section-title">Motif de consultation</div>', unsafe_allow_html=True)
        motif = st.text_area("Motif", value=lv("s_motif_consultation",""), height=80, key="ls_motif")
        st.markdown('<div class="section-title">Caractéristiques de la douleur</div>', unsafe_allow_html=True)
        sc1,sc2 = st.columns(2)
        with sc1:
            loc_stored = lv_list("s_douleur_localisation")
            localisation = st.multiselect("Localisation", LOCALISATIONS,
                default=[x for x in loc_stored if x in LOCALISATIONS], key="ls_loc")
            # Type de douleur — avec option vide en premier
            TYPES_DOULEUR_OPT = ["— Non renseigné —"] + TYPES_DOULEUR
            td_stored = lv("s_type_douleur", "")
            td_idx = TYPES_DOULEUR_OPT.index(td_stored) if td_stored in TYPES_DOULEUR_OPT else 0
            type_douleur_sel = st.selectbox("Type de douleur", TYPES_DOULEUR_OPT,
                index=td_idx, key="ls_type")
            type_douleur = "" if type_douleur_sel == "— Non renseigné —" else type_douleur_sel
        with sc2:
            eva_repos = st.slider("EVA repos (0–10)", 0, 10, lv_int("s_eva_repos",0), key="ls_eva_r")
            eva_mvt   = st.slider("EVA mouvement (0–10)", 0, 10, lv_int("s_eva_mouvement",0), key="ls_eva_m")
            eva_nuit  = st.slider("EVA nuit (0–10)", 0, 10, lv_int("s_eva_nuit",0), key="ls_eva_n")
            def ec(s): return "#388e3c" if s<=3 else "#f57c00" if s<=6 else "#d32f2f"
            for lbl,val in [("Repos",eva_repos),("Mouvement",eva_mvt),("Nuit",eva_nuit)]:
                st.markdown(f'<small style="color:{ec(val)}">● EVA {lbl} : <b>{val}/10</b></small>', unsafe_allow_html=True)
        sc3,sc4 = st.columns(2)
        with sc3:
            agg_stored = lv_list("s_facteurs_aggravants")
            aggravants = st.multiselect("Facteurs aggravants", FACTEURS_AGGRAVANTS,
                default=[x for x in agg_stored if x in FACTEURS_AGGRAVANTS], key="ls_agg")
        with sc4:
            soul_stored = lv_list("s_facteurs_soulageants")
            soulageants = st.multiselect("Facteurs soulageants", FACTEURS_SOULAGEANTS,
                default=[x for x in soul_stored if x in FACTEURS_SOULAGEANTS], key="ls_soul")
        st.markdown('<div class="section-title">Historique</div>', unsafe_allow_html=True)
        sh1,sh2 = st.columns(2)
        with sh1:
            debut      = st.text_input("Début de la douleur", value=lv("s_debut_douleur",""), key="ls_debut")
            mode_debut = st.text_input("Mode d'apparition", value=lv("s_mode_debut",""), key="ls_mode")
            duree_ep   = st.text_input("Durée épisode actuel", value=lv("s_duree_episode",""), key="ls_duree")
            episodes   = st.text_input("Épisodes antérieurs", value=lv("s_episodes_anterieurs",""), key="ls_eps")
        with sh2:
            atcd       = st.text_area("Antécédents", value=lv("s_antecedents",""), height=80, key="ls_atcd")
            traitements= st.text_area("Traitements en cours", value=lv("s_traitements_en_cours",""), height=80, key="ls_trait")
        st.markdown('<div class="section-title">Impact fonctionnel</div>', unsafe_allow_html=True)

        # Cases à cocher
        ck1, ck2, _ = st.columns([1, 1, 2])
        with ck1:
            arret_travail = st.checkbox(
                "Arrêt de travail",
                value=lv("s_arret_travail","") == "Oui",
                key="ls_arret",
            )
        with ck2:
            reveil_nuit = st.checkbox(
                "Se réveille la nuit à cause de la douleur",
                value=lv("s_reveil_nuit","") == "Oui",
                key="ls_reveil",
            )

        si1,si2,si3 = st.columns(3)
        with si1: impact_avd  = st.text_area("Impact AVD", value=lv("s_impact_avd",""), height=80, key="ls_avd")
        with si2: impact_trav = st.text_area("Impact travail/loisirs", value=lv("s_impact_travail",""), height=80, key="ls_trav")
        with si3: impact_somm = st.text_area("Notes sommeil", value=lv("s_impact_sommeil",""), height=80, key="ls_somm")
        collected.update({
            "s_motif_consultation":motif, "s_douleur_localisation":"|".join(localisation),
            "s_eva_repos":eva_repos, "s_eva_mouvement":eva_mvt, "s_eva_nuit":eva_nuit,
            "s_type_douleur":type_douleur,
            "s_facteurs_aggravants":"|".join(aggravants), "s_facteurs_soulageants":"|".join(soulageants),
            "s_debut_douleur":debut, "s_mode_debut":mode_debut, "s_duree_episode":duree_ep,
            "s_episodes_anterieurs":episodes, "s_antecedents":atcd,
            "s_traitements_en_cours":traitements,
            "s_arret_travail": "Oui" if arret_travail else "Non",
            "s_reveil_nuit":   "Oui" if reveil_nuit else "Non",
            "s_impact_avd":impact_avd, "s_impact_travail":impact_trav, "s_impact_sommeil":impact_somm,
        })

    # ── DRAPEAUX ──────────────────────────────────────────────────────────────
    with tab_flags:
        st.markdown('<div class="section-title">🚩 Drapeaux rouges</div>', unsafe_allow_html=True)
        st.markdown('<div class="danger-box">⚠️ Présence de drapeaux rouges → investigation médicale urgente.</div>', unsafe_allow_html=True)
        dr_stored = lv_list("drapeaux_rouges_list")
        dr_sel = []
        cols_dr = st.columns(2)
        for i,item in enumerate(DRAPEAUX_ROUGES):
            with cols_dr[i%2]:
                if st.checkbox(item, value=item in dr_stored, key=f"dr_{i}"): dr_sel.append(item)
        if dr_sel:
            st.markdown(f'<div class="danger-box">🔴 <b>{len(dr_sel)} drapeau(x) rouge(s) détecté(s)</b></div>', unsafe_allow_html=True)
        dr_notes = st.text_area("Notes drapeaux rouges", value=lv("drapeaux_rouges_notes",""), height=60, key="dr_notes")
        st.markdown("---")
        st.markdown('<div class="section-title">🟡 Drapeaux jaunes</div>', unsafe_allow_html=True)
        st.markdown('<div class="warn-box">Drapeaux jaunes → approche biopsychosociale.</div>', unsafe_allow_html=True)
        dj_stored = lv_list("drapeaux_jaunes_list")
        dj_sel = []
        cols_dj = st.columns(2)
        for i,item in enumerate(DRAPEAUX_JAUNES):
            with cols_dj[i%2]:
                if st.checkbox(item, value=item in dj_stored, key=f"dj_{i}"): dj_sel.append(item)
        if dj_sel:
            st.markdown(f'<div class="warn-box">🟡 <b>{len(dj_sel)} drapeau(x) jaune(s)</b></div>', unsafe_allow_html=True)
        dj_notes = st.text_area("Notes drapeaux jaunes", value=lv("drapeaux_jaunes_notes",""), height=60, key="dj_notes")
        collected.update({"drapeaux_rouges_list":"|".join(dr_sel),"drapeaux_rouges_notes":dr_notes,
                          "drapeaux_jaunes_list":"|".join(dj_sel),"drapeaux_jaunes_notes":dj_notes})

    # ── OBJECTIF ──────────────────────────────────────────────────────────────
    with tab_o:
        st.markdown('<div class="soap-label">O — Objectif</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="section-title">Posture & observation</div>', unsafe_allow_html=True)
        posture_notes = st.text_area("Observation posturale", value=lv("o_posture_notes",""), height=80, key="lo_posture")
        st.markdown('<div class="section-title">Mobilité lombaire</div>', unsafe_allow_html=True)
        mo1,mo2,mo3,mo4 = st.columns(4)
        with mo1:
            schober = st.number_input("Schober modifié (cm)", 0.0, 30.0, lv_float("o_schober"), 0.5, key="lo_schober")
            flex_cm = st.number_input("Flexion doigt-sol (cm)", 0.0, 50.0, lv_float("o_flexion_cm"), 0.5, key="lo_flex")
        with mo2:
            ext_deg = st.number_input("Extension (°)", 0.0, 90.0, lv_float("o_extension_deg"), 1.0, key="lo_ext")
        with mo3:
            lat_d = st.number_input("Latéroflexion D (°)", 0.0, 90.0, lv_float("o_lat_droite_deg"), 1.0, key="lo_latd")
            lat_g = st.number_input("Latéroflexion G (°)", 0.0, 90.0, lv_float("o_lat_gauche_deg"), 1.0, key="lo_latg")
        with mo4:
            rot_d = st.number_input("Rotation D (°)", 0.0, 90.0, lv_float("o_rot_droite_deg"), 1.0, key="lo_rotd")
            rot_g = st.number_input("Rotation G (°)", 0.0, 90.0, lv_float("o_rot_gauche_deg"), 1.0, key="lo_rotg")
        st.markdown('<div class="section-title">Tests cliniques</div>', unsafe_allow_html=True)
        test_collected = {}
        for section_name, tests in TESTS_CLINIQUES.items():
            with st.expander(section_name):
                tc1,tc2 = st.columns(2)
                for i,test in enumerate(tests):
                    skey = "lo_" + test.lower().replace(" ","_").replace("/","_").replace("(","").replace(")","")[:30]
                    sv = lv(f"o_{skey}", RESULTATS_TEST[0])
                    idx = RESULTATS_TEST.index(sv) if sv in RESULTATS_TEST else 0
                    with (tc1 if i%2==0 else tc2):
                        chosen = st.selectbox(test, RESULTATS_TEST, index=idx, key=f"test_{skey}")
                        test_collected[f"o_{skey}"] = chosen if chosen != "—" else ""
        tests_notes = st.text_area("Notes complémentaires", value=lv("o_tests_notes",""), height=80, key="lo_notes")
        collected.update({"o_posture_notes":posture_notes,
            "o_schober":schober or "","o_flexion_cm":flex_cm or "",
            "o_extension_deg":ext_deg or "","o_lat_droite_deg":lat_d or "",
            "o_lat_gauche_deg":lat_g or "","o_rot_droite_deg":rot_d or "",
            "o_rot_gauche_deg":rot_g or "","o_tests_notes":tests_notes,**test_collected})

    # ── DIAGNOSTICS ───────────────────────────────────────────────────────────
    with tab_diag:
        st.markdown('<div class="section-title">🩺 Hypothèses diagnostiques</div>', unsafe_allow_html=True)
        diag_principal = st.text_input("Diagnostic principal", value=lv("diag_principal",""), key="ld_principal")
        diag_stored = lv_list("diag_diff_list")
        diag_sel = []
        for category, items in DIAG_DIFF.items():
            with st.expander(category):
                for item in items:
                    if st.checkbox(item, value=item in diag_stored, key=f"diag_{item.replace(' ','_')[:40]}"):
                        diag_sel.append(item)
        diag_notes = st.text_area("Raisonnement clinique", value=lv("diag_notes",""), height=100, key="ld_notes")
        collected.update({"diag_principal":diag_principal,"diag_diff_list":"|".join(diag_sel),"diag_notes":diag_notes})

    # ── APPRÉCIATION ──────────────────────────────────────────────────────────
    with tab_a:
        st.markdown('<div class="soap-label">A — Appréciation</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="info-box">Synthèse clinique, interprétation et pronostic.</div>', unsafe_allow_html=True)
        appreciation = st.text_area("Appréciation clinique", value=lv("a_appreciation",""), height=200, key="la_appr")
        collected["a_appreciation"] = appreciation

    # ── PLAN ──────────────────────────────────────────────────────────────────
    with tab_p:
        st.markdown('<div class="soap-label">P — Plan thérapeutique</div>', unsafe_allow_html=True)
        st.markdown("")
        pc1,pc2 = st.columns(2)
        with pc1:
            objectifs  = st.text_area("Objectifs thérapeutiques", value=lv("p_objectifs",""), height=100, key="lp_obj")
            traitement = st.text_area("Modalités de traitement", value=lv("p_traitement",""), height=100, key="lp_trait")
        with pc2:
            frequence  = st.text_input("Fréquence des séances", value=lv("p_frequence",""), key="lp_freq")
            duree_plan = st.text_input("Durée prévue", value=lv("p_duree",""), key="lp_duree")
            education  = st.text_area("Éducation du patient", value=lv("p_education",""), height=80, key="lp_edu")
            autogestion= st.text_area("Autogestion / exercices à domicile", value=lv("p_autogestion",""), height=80, key="lp_auto")
        collected.update({"p_objectifs":objectifs,"p_traitement":traitement,
                          "p_frequence":frequence,"p_duree":duree_plan,
                          "p_education":education,"p_autogestion":autogestion})

    # ── QUESTIONNAIRES ────────────────────────────────────────────────────────
    with tab_q:
        st.markdown('<div class="section-title">📊 Scores des questionnaires</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Entrez les scores calculés après avoir fait remplir les questionnaires papier au patient.</div>', unsafe_allow_html=True)
        qc1,qc2,qc3 = st.columns(3)
        with qc1:
            st.markdown("**📊 Oswestry (ODI)**")
            odi_score = st.number_input("Score ODI (%)", 0, 100, lv_int("odi_score",0), 1, key="lq_odi")
            if odi_score > 0:
                if odi_score<=20: oi,oc="#388e3c","Incapacité minimale (0–20%)"
                elif odi_score<=40: oc,oi="#8bc34a","Incapacité modérée (21–40%)"
                elif odi_score<=60: oc,oi="#f57c00","Incapacité sévère (41–60%)"
                elif odi_score<=80: oc,oi="#e64a19","Incapacité très sévère (61–80%)"
                else: oc,oi="#d32f2f","Grabataire / exagération (>80%)"
                st.markdown(f'<div class="score-box" style="background:{oc};font-size:0.9rem;">{odi_score}% — {oi}</div>', unsafe_allow_html=True)
                collected.update({"odi_score":odi_score,"odi_interpretation":oi})
            else:
                collected.update({"odi_score":"","odi_interpretation":""})
        with qc2:
            st.markdown("**😨 Tampa Scale (TSK-17)**")
            tampa_score = st.number_input("Score Tampa", 0, 68, lv_int("tampa_score",0), 1, key="lq_tampa")
            if tampa_score > 0:
                if tampa_score<=37: tc,ti="#388e3c","Kinésiophobie faible (≤ 37)"
                elif tampa_score<=44: tc,ti="#f57c00","Kinésiophobie modérée (38–44)"
                else: tc,ti="#d32f2f","Kinésiophobie élevée (> 44)"
                st.markdown(f'<div class="score-box" style="background:{tc};font-size:0.9rem;">{tampa_score}/68 — {ti}</div>', unsafe_allow_html=True)
                collected.update({"tampa_score":tampa_score,"tampa_interpretation":ti})
            else:
                collected.update({"tampa_score":"","tampa_interpretation":""})
        with qc3:
            st.markdown("**🧠 Örebro**")
            orebro_score = st.number_input("Score Örebro", 0, 100, lv_int("orebro_score",0), 1, key="lq_orebro")
            if orebro_score > 0:
                if orebro_score<=50: oc2,oi2="#388e3c","Risque faible (≤ 50)"
                elif orebro_score<=74: oc2,oi2="#f57c00","Risque moyen (51–74)"
                else: oc2,oi2="#d32f2f","Risque élevé (≥ 75)"
                st.markdown(f'<div class="score-box" style="background:{oc2};font-size:0.9rem;">{orebro_score} — {oi2}</div>', unsafe_allow_html=True)
                collected.update({"orebro_score":orebro_score,"orebro_interpretation":oi2})
            else:
                collected.update({"orebro_score":"","orebro_interpretation":""})

    # ── SAUVEGARDE ────────────────────────────────────────────────────────────
    if save_top or st.button("💾 Sauvegarder le bilan", type="primary", key="lomb_save_bot"):
        final_data = {**st.session_state.lomb_bilan_data,**collected,
                      "patient_id":st.session_state.lomb_patient_id}
        if st.session_state.lomb_bilan_id:
            final_data["bilan_id"] = st.session_state.lomb_bilan_id
        with st.spinner("Enregistrement…"):
            new_id = save_bilan_lombalgie(final_data)
        st.session_state.lomb_bilan_id   = new_id
        final_data["bilan_id"]           = new_id
        st.session_state.lomb_bilan_data = final_data
        st.success(f"✅ Bilan sauvegardé ! (ID : {new_id})")
        st.balloons()


# ── ROUTEUR ───────────────────────────────────────────────────────────────────
mode = st.session_state.lomb_mode
if mode == "accueil":
    render_accueil()
elif mode == "bilan":
    if not st.session_state.lomb_patient_info:
        st.session_state.lomb_mode = "accueil"; st.rerun()
    render_bilan_selection()
elif mode == "formulaire":
    if not st.session_state.lomb_patient_info:
        st.session_state.lomb_mode = "accueil"; st.rerun()
    render_formulaire()
else:
    st.session_state.lomb_mode = "accueil"; st.rerun()
