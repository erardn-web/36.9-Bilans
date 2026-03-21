"""
Page : Bilan Lombalgie — Formulaire SOAP complet
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.db import (
    get_all_patients, create_patient,
    get_patient_bilans_lombalgie, save_bilan_lombalgie, delete_bilan_lombalgie,
)
from utils.lombalgie_data import (
    GROUPES_CLINIQUES, GROUPES_OPTIONS, GROUPES_CODES,
    GROUPES_DESC, GROUPES_COLORS,
    DRAPEAUX_ROUGES, DRAPEAUX_JAUNES,
    LOCALISATIONS,
    FACTEURS_AGGRAVANTS, FACTEURS_SOULAGEANTS,
    TYPES_DOULEUR, RYTHME_DOULEUR,
    TESTS_CLINIQUES, RESULTATS_TEST,
)
from utils.lombalgie_pdf import (
    generate_questionnaires_lombalgie_pdf,
    ODI_SECTIONS, ODI_KEYS, compute_odi,
    TAMPA_ITEMS, TAMPA_KEYS, TAMPA_SCALE, TAMPA_SCALE_VALUES, compute_tampa,
    OREBRO_ITEMS, OREBRO_KEYS, compute_orebro,
)
from utils.lombalgie_pdf import generate_pdf_lombalgie

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

def lv_int_or_none(key):
    """Returns stored int value or None (for number_input blank state)."""
    v = lv(key, None)
    if v is None or str(v).strip() in ("", "None", "0"): return None
    try:
        result = int(float(v))
        return result if result != 0 else None
    except: return None

def lv_float_or_none(key):
    """Returns stored float value or None."""
    v = lv(key, None)
    if v is None or str(v).strip() in ("", "None"): return None
    try:
        result = float(v)
        return result if result != 0.0 else None
    except: return None



def _render_print_panel(patient_info, key_prefix):
    st.markdown("""<div style="background:#f0f8e8;border:2px solid #2e5a1c;border-radius:10px;
        padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <span style="font-size:1.1rem;font-weight:700;color:#2e5a1c;">
        🖨️ Sélectionner les questionnaires à imprimer</span></div>""",
        unsafe_allow_html=True)
    p1,p2,p3,p4,p5 = st.columns(5)
    with p1: pr_odi   = st.checkbox("📊 Oswestry (ODI)",   value=True, key=f"{key_prefix}_odi")
    with p2: pr_tampa = st.checkbox("😨 Tampa Scale",       value=True, key=f"{key_prefix}_tampa")
    with p3: pr_oreb  = st.checkbox("🧠 Örebro",            value=True, key=f"{key_prefix}_orebro")
    with p4: pr_drap  = st.checkbox("🚩 Drapeaux",          value=True, key=f"{key_prefix}_drap")
    with p5: pr_luom  = st.checkbox("🏃 Luomajoki",         value=True, key=f"{key_prefix}_luom")
    selected = (
        (["odi"]       if pr_odi   else []) +
        (["tampa"]     if pr_tampa else []) +
        (["orebro"]    if pr_oreb  else []) +
        (["drapeaux"]  if pr_drap  else []) +
        (["luomajoki"] if pr_luom  else [])
    )
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
                    c1, c2 = st.columns([3, 1])
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
            sub  = st.form_submit_button("Créer", type="primary")
        if sub:
            if not nom or not prenom: st.error("Nom et prénom obligatoires.")
            else:
                pid = create_patient(nom, prenom, ddn, sexe, "")
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

    def get_selected_bilans(df):
        sel = st.session_state.get("lomb_selected_bilan_ids", None)
        if sel is None or df.empty: return df
        filtered = df[df["bilan_id"].isin(sel)]
        return filtered if not filtered.empty else df

    col_back, col_print, col_evol, col_pdf, _ = st.columns([1, 1.5, 1.2, 1.2, 1])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            for k in ["lomb_patient_id","lomb_patient_info","lomb_bilan_id"]:
                st.session_state[k] = None
            st.session_state.lomb_bilan_data = {}
            st.session_state.pop("lomb_selected_bilan_ids", None)
            st.session_state.lomb_mode = "accueil"
            st.rerun()
    with col_print:
        if st.button("🖨️ Imprimer questionnaires", key="print_lomb_pat_btn"):
            st.session_state["show_print_lomb_patient"] = True
    with col_evol:
        if not bilans_df.empty:
            if st.button("📈 Voir l'évolution", type="primary", key="lomb_evol_btn"):
                st.session_state.lomb_mode = "evolution"
                st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            sel_df = get_selected_bilans(bilans_df)
            with st.spinner("PDF…"):
                pdf_bytes = generate_pdf_lombalgie(sel_df, info)
            n_sel = len(sel_df)
            st.download_button(
                label=f"📄 Exporter PDF ({n_sel} bilan{'s' if n_sel > 1 else ''})",
                data=pdf_bytes,
                file_name=f"evolution_lombalgie_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf",
            )

    if st.session_state.get("show_print_lomb_patient", False):
        _render_print_panel(patient_info=info, key_prefix="pat")

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📋 Bilans existants")
        if bilans_df.empty:
            st.info("Aucun bilan pour ce patient.")
        else:
            st.markdown("<small style='color:#888'>Cochez les bilans à inclure dans l'évolution et le PDF</small>",
                        unsafe_allow_html=True)

            selected_ids = st.session_state.get("lomb_selected_bilan_ids", None)
            if selected_ids is None:
                selected_ids = list(bilans_df["bilan_id"])
                st.session_state["lomb_selected_bilan_ids"] = selected_ids

            valid_ids = list(bilans_df["bilan_id"])
            selected_ids = [i for i in selected_ids if i in valid_ids]
            st.session_state["lomb_selected_bilan_ids"] = selected_ids

            new_selected = []
            for _, row in bilans_df.iterrows():
                bid   = row.get("bilan_id", "—")
                bdate = row.get("date_bilan", "—")
                btype = row.get("type_bilan", "—")
                g     = row.get("groupe_clinique", "") or ""

                c_check, c_info, c_open, c_del = st.columns([0.5, 3.5, 0.8, 0.8])
                with c_check:
                    checked = st.checkbox("", value=bid in selected_ids,
                                         key=f"lsel_{bid}", label_visibility="collapsed")
                    if checked:
                        new_selected.append(bid)
                with c_info:
                    groupe_str = f" | **{g}**" if g and g != "—" else ""
                    st.markdown(f"**{bdate}** — {btype}{groupe_str}  \n<small>`{bid}`</small>",
                                unsafe_allow_html=True)
                with c_open:
                    if st.button("✏️ Ouvrir", key=f"lopen_{bid}"):
                        st.session_state.lomb_bilan_id   = bid
                        st.session_state.lomb_bilan_data = row.to_dict()
                        st.session_state.lomb_mode       = "formulaire"
                        st.session_state["lomb_unsaved"] = True
                        st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"ldel_req_{bid}", help="Supprimer ce bilan"):
                        st.session_state[f"lomb_confirm_del_{bid}"] = True

                if st.session_state.get(f"lomb_confirm_del_{bid}", False):
                    st.warning(
                        f"⚠️ Supprimer définitivement le bilan **{bdate} — {btype}** ? "
                        "Cette action est irréversible."
                    )
                    ca, cb, _ = st.columns([1, 1, 3])
                    with ca:
                        if st.button("✅ Confirmer", key=f"ldel_ok_{bid}", type="primary"):
                            with st.spinner("Suppression…"):
                                ok = delete_bilan_lombalgie(bid)
                            if ok:
                                st.success("Bilan supprimé.")
                            else:
                                st.error("Erreur lors de la suppression.")
                            st.session_state.pop(f"lomb_confirm_del_{bid}", None)
                            st.session_state["lomb_selected_bilan_ids"] = [
                                i for i in selected_ids if i != bid]
                            st.rerun()
                    with cb:
                        if st.button("✖ Annuler", key=f"ldel_cancel_{bid}"):
                            st.session_state.pop(f"lomb_confirm_del_{bid}", None)
                            st.rerun()

            st.session_state["lomb_selected_bilan_ids"] = new_selected

            n_sel = len(new_selected)
            n_tot = len(bilans_df)
            if n_sel < n_tot:
                st.markdown(
                    f"<small style='color:#f57c00'>⚡ {n_sel}/{n_tot} bilans sélectionnés pour l'évolution</small>",
                    unsafe_allow_html=True,
                )

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
            st.session_state["lomb_unsaved"] = True
            st.rerun()

def render_formulaire():
    info = st.session_state.lomb_patient_info
    bd   = st.session_state.lomb_bilan_data
    st.session_state["lomb_unsaved"] = True
    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— {bd.get("type_bilan","—")} du {bd.get("date_bilan","—")}</div>',
        unsafe_allow_html=True)
    st.markdown("")
    col_back, col_save, _ = st.columns([1,1,4])
    with col_back:
        if st.button("⬅️ Retour"):
            if st.session_state.get("lomb_unsaved", False):
                st.session_state["lomb_confirm_back"] = True
            else:
                st.session_state.lomb_mode = "bilan"
                st.rerun()

    # Alerte si retour sans sauvegarde
    if st.session_state.get("lomb_confirm_back", False):
        st.warning(
            "⚠️ **Modifications non sauvegardées.** "
            "Êtes-vous sûr(e) de vouloir quitter sans sauvegarder ?"
        )
        ca, cb, _ = st.columns([1.2, 1.2, 4])
        with ca:
            if st.button("✅ Quitter sans sauvegarder", type="primary", key="lomb_back_ok"):
                st.session_state["lomb_confirm_back"] = False
                st.session_state["lomb_unsaved"] = False
                st.session_state.lomb_mode = "bilan"
                st.rerun()
        with cb:
            if st.button("✖ Continuer l'édition", key="lomb_back_cancel"):
                st.session_state["lomb_confirm_back"] = False
                st.rerun()
    with col_save:
        save_top = st.button("💾 Sauvegarder", type="primary")
    st.markdown("---")
    collected = {}

    tab_gen, tab_s, tab_flags, tab_o, tab_diag, tab_pronostic, tab_p, tab_q = st.tabs([
        "📝 Général", "🟦 S – Subjectif", "🚩 Drapeaux",
        "🔬 O – Objectif", "🩺 Raisonnement clinique", "🔮 A – Pronostic",
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
        st.markdown("---")
        st.markdown('<div class="section-title">🩺 Diagnostic principal</div>', unsafe_allow_html=True)
        diag_principal = st.text_input("Diagnostic principal retenu",
            value=lv("diag_principal",""), key="ld_principal")
        collected.update({"date_bilan":str(bilan_date),"type_bilan":bilan_type,
                          "praticien":praticien,"notes_generales":notes_gen,
                          "groupe_clinique":groupe_code,"diag_principal":diag_principal})

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
            _EVA_OPTS = ["—", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            def _eva_default(key):
                v = lv(key, None)
                if v is None or str(v).strip() in ("", "None"): return "—"
                try: return int(float(v))
                except: return "—"
            eva_repos = st.select_slider("EVA repos (0–10)", options=_EVA_OPTS,
                value=_eva_default("s_eva_repos"), key="ls_eva_r",
                format_func=lambda x: "Non renseigné" if x == "—" else str(x))
            eva_mvt   = st.select_slider("EVA mouvement (0–10)", options=_EVA_OPTS,
                value=_eva_default("s_eva_mouvement"), key="ls_eva_m",
                format_func=lambda x: "Non renseigné" if x == "—" else str(x))
            eva_nuit  = st.select_slider("EVA nuit (0–10)", options=_EVA_OPTS,
                value=_eva_default("s_eva_nuit"), key="ls_eva_n",
                format_func=lambda x: "Non renseigné" if x == "—" else str(x))
            # Convert "—" back to empty string for storage
            eva_repos = "" if eva_repos == "—" else eva_repos
            eva_mvt   = "" if eva_mvt   == "—" else eva_mvt
            eva_nuit  = "" if eva_nuit  == "—" else eva_nuit
            def ec(s): return "#388e3c" if s<=3 else "#f57c00" if s<=6 else "#d32f2f"
            for lbl,val in [("Repos",eva_repos),("Mouvement",eva_mvt),("Nuit",eva_nuit)]:
                if val == "": continue
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

        # ── Mobilité lombaire ─────────────────────────────────────────────────
        st.markdown('<div class="section-title">Mobilité lombaire</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box"><small>1/3 = très limité · 2/3 = modérément limité · '
            '3/3 = amplitude complète (normale)</small></div>',
            unsafe_allow_html=True,
        )

        MOB_OPTS = ["— Non renseigné —", "1/3", "2/3", "3/3"]

        def mob_select(label, key):
            stored = lv(key, "")
            idx = MOB_OPTS.index(stored) if stored in MOB_OPTS else 0
            chosen = st.selectbox(label, MOB_OPTS, index=idx, key=f"lo_{key}")
            return "" if chosen == "— Non renseigné —" else chosen

        mo1, mo2, mo3, mo4 = st.columns(4)
        with mo1:
            schober = st.number_input("Schober modifié (cm)", 0.0, 30.0,
                lv_float_or_none("o_schober"), 0.5, key="lo_schober", help="0 = non mesuré")
            flex_cm = st.number_input("Flexion doigt-sol (cm)", 0.0, 50.0,
                lv_float_or_none("o_flexion_cm"), 0.5, key="lo_flex", help="0 = non mesuré")
        with mo2:
            ext_mob  = mob_select("Extension", "o_extension_mob")
        with mo3:
            lat_d_mob = mob_select("Latéroflexion Droite", "o_lat_droite_mob")
            lat_g_mob = mob_select("Latéroflexion Gauche", "o_lat_gauche_mob")
        with mo4:
            rot_d_mob = mob_select("Rotation Droite", "o_rot_droite_mob")
            rot_g_mob = mob_select("Rotation Gauche", "o_rot_gauche_mob")

        # ── Tests cliniques ───────────────────────────────────────────────────
        st.markdown('<div class="section-title">Tests cliniques</div>', unsafe_allow_html=True)
        test_collected = {}

        # Tous les tests sauf contrôle moteur (remplacé par Luomajoki)
        TESTS_SANS_CM = {k: v for k, v in TESTS_CLINIQUES.items()
                         if k != "Tests de contrôle moteur"}

        for section_name, tests in TESTS_SANS_CM.items():
            with st.expander(section_name):
                tc1, tc2 = st.columns(2)
                for i, test in enumerate(tests):
                    skey = "lo_" + test.lower().replace(" ","_").replace("/","_").replace("(","").replace(")","")[:30]
                    sv   = lv(f"o_{skey}", RESULTATS_TEST[0])
                    idx  = RESULTATS_TEST.index(sv) if sv in RESULTATS_TEST else 0
                    with (tc1 if i % 2 == 0 else tc2):
                        chosen = st.selectbox(test, RESULTATS_TEST, index=idx, key=f"test_{skey}")
                        test_collected[f"o_{skey}"] = chosen if chosen != "—" else ""

        # ── Tests de Luomajoki ────────────────────────────────────────────────
        with st.expander("Tests de Luomajoki — Contrôle du mouvement lombaire"):
            st.markdown(
                '<div class="info-box"><small>'
                '<b>Batterie de 6 tests de contrôle du mouvement lombaire</b> (Luomajoki et al., 2007). '
                'Résultat : ✅ Réussi (contrôle correct) · ❌ Échoué (perte de contrôle lombaire). '
                'Score total sur 6 — un score ≥ 3 échecs est cliniquement significatif.'
                '</small></div>',
                unsafe_allow_html=True,
            )
            LUOM_TESTS = [
                ("luom_waiters_bow",
                 "1. Waiters Bow (hip hinge)",
                 "Le patient se penche en avant en fléchissant les hanches sans flexion lombaire. "
                 "Échec si flexion ou extension lombaire compensatoire."),
                ("luom_pelvic_tilt",
                 "2. Pelvic Tilt (debout)",
                 "Le patient effectue une antéversion et rétroversion pelviennes. "
                 "Échec si mouvement lombaire au lieu du mouvement pelvien pur."),
                ("luom_knee_lift",
                 "3. Knee Lift (debout)",
                 "Le patient lève le genou jusqu'à 90° en unipodal. "
                 "Échec si inclinaison lombaire ou rotation du bassin."),
                ("luom_one_leg_stance",
                 "4. One-Leg Stance (station unipodale)",
                 "Le patient maintient l'équilibre sur un pied pendant 10 secondes. "
                 "Échec si oscillation lombaire ou chute du bassin > 2 cm."),
                ("luom_sitting_knee_ext",
                 "5. Sitting Knee Extension (ASLR assis)",
                 "Le patient étend le genou en position assise. "
                 "Échec si flexion lombaire compensatoire."),
                ("luom_prone_knee_bend",
                 "6. Prone Knee Bend (décubitus ventral)",
                 "Le patient fléchit le genou à 90° en décubitus ventral. "
                 "Échec si antéversion pelvienne ou extension lombaire compensatoire."),
            ]

            LUOM_OPTS = ["— Non testé —", "✅ Réussi", "❌ Échoué"]
            luom_scores = []
            lc1, lc2 = st.columns(2)
            for i, (lkey, lname, ldesc) in enumerate(LUOM_TESTS):
                stored_luom = lv(f"o_{lkey}", "")
                idx_luom    = LUOM_OPTS.index(stored_luom) if stored_luom in LUOM_OPTS else 0
                with (lc1 if i % 2 == 0 else lc2):
                    st.markdown(f"**{lname}**")
                    st.markdown(f"<small style='color:#666'>{ldesc}</small>",
                                unsafe_allow_html=True)
                    chosen_luom = st.radio(
                        label=lname, options=LUOM_OPTS, index=idx_luom,
                        horizontal=True, key=f"luom_{lkey}",
                        label_visibility="collapsed",
                    )
                    test_collected[f"o_{lkey}"] = chosen_luom if chosen_luom != "— Non testé —" else ""
                    if chosen_luom == "❌ Échoué":
                        luom_scores.append(1)

            # Score total Luomajoki
            n_echecs = len(luom_scores)
            if n_echecs > 0:
                color_luom = "#d32f2f" if n_echecs >= 3 else "#f57c00" if n_echecs >= 1 else "#388e3c"
                st.markdown(
                    f'<div class="score-box" style="background:{color_luom};font-size:1rem;margin-top:0.5rem;">'
                    f'{n_echecs} / 6 tests échoués'
                    f'{"  — Dysfonction de contrôle moteur significative" if n_echecs >= 3 else ""}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            test_collected["o_luomajoki_score"] = n_echecs if n_echecs > 0 else ""

        tests_notes = st.text_area("Notes complémentaires (objectif)",
            value=lv("o_tests_notes",""), height=80, key="lo_notes")

        collected.update({
            "o_posture_notes":  posture_notes,
            "o_schober":        schober or "",
            "o_flexion_cm":     flex_cm or "",
            "o_extension_mob":  ext_mob,
            "o_lat_droite_mob": lat_d_mob,
            "o_lat_gauche_mob": lat_g_mob,
            "o_rot_droite_mob": rot_d_mob,
            "o_rot_gauche_mob": rot_g_mob,
            "o_tests_notes":    tests_notes,
            **test_collected,
        })

    # ── DIAGNOSTICS ───────────────────────────────────────────────────────────
    with tab_diag:
        st.markdown('<div class="section-title">🩺 Raisonnement clinique</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Notez ici votre raisonnement clinique : hypothèses, '
            'diagnostics différentiels, éléments qui orientent ou excluent certains diagnostics.</div>',
            unsafe_allow_html=True,
        )
        diag_notes = st.text_area("Raisonnement clinique",
            value=lv("diag_notes",""), height=300, key="ld_notes",
            placeholder="Ex : Arguments en faveur d'un syndrome facettaire : extension plus douloureuse que flexion, "
                        "soulagement en décharge... Hypothèse myofasciale écartée car..."
        )
        collected.update({"diag_notes": diag_notes})

    # ── APPRÉCIATION ──────────────────────────────────────────────────────────
    with tab_pronostic:
        st.markdown('<div class="soap-label">A — Pronostic</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="info-box">Pronostic et synthèse clinique : facteurs favorables, défavorables, objectifs à long terme.</div>', unsafe_allow_html=True)
        appreciation = st.text_area("Appréciation clinique", value=lv("a_appreciation",""), height=200, key="la_appr", placeholder="Pronostic favorable / réservé / défavorable... Facteurs favorables : ... Facteurs défavorables : ...")
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
        st.markdown('<div class="section-title">📊 Questionnaires</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Le patient remplit les questionnaires directement ici. '
            'Les scores sont calculés automatiquement.</div>',
            unsafe_allow_html=True,
        )

        q_tab_odi, q_tab_tampa, q_tab_orebro = st.tabs([
            "📊 Oswestry (ODI)", "😨 Tampa Scale", "🧠 Örebro",
        ])

        # ── ODI ──────────────────────────────────────────────────────────────
        with q_tab_odi:
            st.markdown("**Oswestry Disability Index** — Cochez UNE seule réponse par section.")
            odi_answers = {}
            for key, title, options in ODI_SECTIONS:
                stored = lv_int(key, -1)
                # -1 = non répondu
                opts_with_empty = ["— Non répondu —"] + options
                default_idx = stored + 1 if 0 <= stored <= 5 else 0
                chosen = st.radio(
                    title, opts_with_empty,
                    index=default_idx,
                    key=f"q_{key}",
                )
                if chosen != "— Non répondu —":
                    odi_answers[key] = options.index(chosen)
                    collected[key] = options.index(chosen)
                else:
                    collected[key] = ""

            odi_result = compute_odi(odi_answers)
            if odi_result["score"] is not None:
                st.markdown("---")
                st.markdown(
                    f'<div class="score-box" style="background:{odi_result["color"]};">'
                    f'ODI : {odi_result["score"]}% — {odi_result["interpretation"]}</div>',
                    unsafe_allow_html=True,
                )
                collected.update({"odi_score": odi_result["score"],
                                   "odi_interpretation": odi_result["interpretation"]})
            else:
                collected.update({"odi_score": "", "odi_interpretation": ""})

        # ── TAMPA ─────────────────────────────────────────────────────────────
        with q_tab_tampa:
            st.markdown(
                "**Tampa Scale for Kinesiophobia (TSK-17)** — "
                "1 = Pas du tout d'accord · 2 = Plutôt pas d'accord · "
                "3 = Plutôt d'accord · 4 = Tout à fait d'accord"
            )
            st.markdown(
                '<div class="info-box"><small>(R) = item inversé pour le calcul du score</small></div>',
                unsafe_allow_html=True,
            )
            tampa_answers = {}
            for key, reversed_item, text in TAMPA_ITEMS:
                num = int(key.split("_")[1])
                stored = lv_int(key, 0)
                r_label = " *(R)*" if reversed_item else ""
                TAMPA_OPTS_EXTENDED = [0] + TAMPA_SCALE_VALUES
                TAMPA_FMT = {0: "— Non répondu —", 1: TAMPA_SCALE[0], 2: TAMPA_SCALE[1], 3: TAMPA_SCALE[2], 4: TAMPA_SCALE[3]}
                default_idx = stored if 1 <= stored <= 4 else 0
                chosen_val = st.radio(
                    f"{num}.{r_label} {text}",
                    options=TAMPA_OPTS_EXTENDED,
                    format_func=lambda x: TAMPA_FMT.get(x, "—"),
                    index=default_idx,
                    horizontal=True,
                    key=f"q_{key}",
                )
                if chosen_val == 0:
                    collected[key] = ""
                else:
                    tampa_answers[key] = chosen_val
                    collected[key] = chosen_val

            tampa_result = compute_tampa(tampa_answers)
            if tampa_result["score"] is not None:
                st.markdown("---")
                st.markdown(
                    f'<div class="score-box" style="background:{tampa_result["color"]};">'
                    f'Tampa : {tampa_result["score"]}/68 — {tampa_result["interpretation"]}</div>',
                    unsafe_allow_html=True,
                )
                collected.update({"tampa_score": tampa_result["score"],
                                   "tampa_interpretation": tampa_result["interpretation"]})
            else:
                collected.update({"tampa_score": "", "tampa_interpretation": ""})

        # ── ÖREBRO ────────────────────────────────────────────────────────────
        with q_tab_orebro:
            st.markdown(
                "**Örebro Musculoskeletal Pain Questionnaire** — "
                "Entourez le chiffre qui correspond le mieux à votre situation."
            )
            orebro_answers = {}
            for key, question, hint in OREBRO_ITEMS:
                num = int(key.split("_")[1])
                stored = lv_int(key, -1)
                default_idx = stored if 0 <= stored <= 10 else 0
                st.markdown(f"**{num}. {question}**")
                st.markdown(f"<small style='color:#888'>{hint}</small>", unsafe_allow_html=True)
                val = st.slider(
                    label=f"orebro_{num}",
                    min_value=0, max_value=10,
                    value=default_idx,
                    key=f"q_{key}",
                    label_visibility="collapsed",
                )
                orebro_answers[key] = val
                collected[key] = val

            orebro_result = compute_orebro(orebro_answers)
            if orebro_result["score"] is not None:
                st.markdown("---")
                st.markdown(
                    f'<div class="score-box" style="background:{orebro_result["color"]};">'
                    f'Örebro : {orebro_result["score"]}/100 — {orebro_result["interpretation"]}</div>',
                    unsafe_allow_html=True,
                )
                collected.update({"orebro_score": orebro_result["score"],
                                   "orebro_interpretation": orebro_result["interpretation"]})
            else:
                collected.update({"orebro_score": "", "orebro_interpretation": ""})

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
        st.session_state["lomb_unsaved"] = False
        st.success(f"✅ Bilan sauvegardé ! (ID : {new_id})")
        st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
#  ÉVOLUTION
# ═══════════════════════════════════════════════════════════════════════════════

def safe_n(val):
    try:
        v = float(val)
        return v if v != 0 else None
    except (TypeError, ValueError):
        return None


def render_evolution():
    info          = st.session_state.lomb_patient_info
    bilans_df_all = get_patient_bilans_lombalgie(st.session_state.lomb_patient_id)

    # Appliquer la sélection (clé cohérente avec render_bilan_selection)
    sel = st.session_state.get("lomb_selected_ids", None)
    if sel and not bilans_df_all.empty:
        filtered  = bilans_df_all[bilans_df_all["bilan_id"].isin(sel)]
        bilans_df = filtered if not filtered.empty else bilans_df_all
    else:
        bilans_df = bilans_df_all

    n_sel = len(bilans_df)
    n_tot = len(bilans_df_all)

    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} — Évolution Lombalgie</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    if n_sel < n_tot:
        st.info(f"ℹ️ Affichage de {n_sel}/{n_tot} bilans sélectionnés.")

    col_back, col_pdf, _ = st.columns([1, 1.5, 4])
    with col_back:
        if st.button("⬅️ Retour"):
            st.session_state.lomb_mode = "bilan"
            st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            with st.spinner("Génération du PDF…"):
                pdf_bytes = generate_pdf_lombalgie(bilans_df, info)
            st.download_button(
                label=f"📄 Exporter en PDF ({n_sel} bilan{'s' if n_sel>1 else ''})",
                data=pdf_bytes,
                file_name=f"evolution_lombalgie_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf",
                type="primary",
            )

    st.markdown("---")

    if bilans_df.empty:
        st.info("Aucun bilan disponible.")
        return

    # Trier par date
    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)
    labels = [
        f"{r['date_bilan'].strftime('%d/%m/%y')} – {r.get('type_bilan','')}"
        for _, r in bilans_df.iterrows()
    ]

    tab_doul, tab_q, tab_mob, tab_luom, tab_soap = st.tabs([
        "🩸 Douleur (EVA)", "📊 Questionnaires", "🦴 Mobilité",
        "🏃 Luomajoki", "📋 SOAP synthèse",
    ])

    # ── EVA ──────────────────────────────────────────────────────────────────
    with tab_doul:
        st.markdown('<div class="section-title">🩸 Évolution des EVA</div>', unsafe_allow_html=True)
        fig_eva = go.Figure()
        for key, label, color in [
            ("s_eva_repos",    "EVA Repos",     "#388e3c"),
            ("s_eva_mouvement","EVA Mouvement", "#f57c00"),
            ("s_eva_nuit",     "EVA Nuit",      "#7b1fa2"),
        ]:
            vals = [safe_n(r.get(key)) for _, r in bilans_df.iterrows()]
            fig_eva.add_trace(go.Scatter(
                x=labels, y=vals, mode="lines+markers+text",
                name=label, line=dict(color=color, width=2.5),
                marker=dict(size=9),
                text=[str(int(v)) if v is not None else "" for v in vals],
                textposition="top center",
            ))
        for y, col, lbl in [(3,"#388e3c","3 légère"),(6,"#f57c00","6 modérée")]:
            fig_eva.add_hline(y=y, line_dash="dot", line_color=col,
                              annotation_text=lbl, annotation_position="right")
        fig_eva.update_layout(
            yaxis=dict(range=[0,11], title="EVA /10"),
            xaxis_tickangle=-20, height=380,
            plot_bgcolor="white", legend=dict(orientation="h"),
        )
        st.plotly_chart(fig_eva, use_container_width=True)
        df_eva = pd.DataFrame({
            "Bilan": labels,
            "EVA repos": [safe_n(r.get("s_eva_repos")) for _, r in bilans_df.iterrows()],
            "EVA mouvement": [safe_n(r.get("s_eva_mouvement")) for _, r in bilans_df.iterrows()],
            "EVA nuit": [safe_n(r.get("s_eva_nuit")) for _, r in bilans_df.iterrows()],
            "Groupe": [r.get("groupe_clinique","—") for _, r in bilans_df.iterrows()],
        })
        st.dataframe(df_eva, use_container_width=True, hide_index=True)

    # ── QUESTIONNAIRES ────────────────────────────────────────────────────────
    with tab_q:
        st.markdown('<div class="section-title">📊 Évolution des questionnaires</div>',
                    unsafe_allow_html=True)
        fig_q = make_subplots(rows=1, cols=3,
                              subplot_titles=["ODI (%)", "Tampa (/68)", "Örebro (/100)"])
        q_configs = [
            ("odi_score",    "#1a3c5e", [(20,"#388e3c"),(40,"#8bc34a"),(60,"#f57c00"),(80,"#e64a19")], 1),
            ("tampa_score",  "#f57c00", [(37,"#388e3c"),(44,"#f57c00")], 2),
            ("orebro_score", "#7b1fa2", [(50,"#388e3c"),(74,"#f57c00")], 3),
        ]
        for key, color, thresholds, col in q_configs:
            vals = [safe_n(r.get(key)) for _, r in bilans_df.iterrows()]
            fig_q.add_trace(go.Scatter(
                x=labels, y=vals, mode="lines+markers+text",
                line=dict(color=color, width=2.5), marker=dict(size=9),
                text=[str(int(v)) if v is not None else "" for v in vals],
                textposition="top center", showlegend=False,
            ), row=1, col=col)
            for thr, tc in thresholds:
                fig_q.add_hline(y=thr, line_dash="dot", line_color=tc, row=1, col=col)
        fig_q.update_xaxes(tickangle=-20)
        fig_q.update_layout(height=380, plot_bgcolor="white", margin=dict(t=40,b=60))
        st.plotly_chart(fig_q, use_container_width=True)
        df_q = pd.DataFrame({
            "Bilan": labels,
            "ODI (%)": [safe_n(r.get("odi_score")) for _, r in bilans_df.iterrows()],
            "Interprétation ODI": [r.get("odi_interpretation","—") for _, r in bilans_df.iterrows()],
            "Tampa (/68)": [safe_n(r.get("tampa_score")) for _, r in bilans_df.iterrows()],
            "Örebro (/100)": [safe_n(r.get("orebro_score")) for _, r in bilans_df.iterrows()],
        })
        st.dataframe(df_q, use_container_width=True, hide_index=True)

    # ── MOBILITÉ ──────────────────────────────────────────────────────────────
    with tab_mob:
        st.markdown('<div class="section-title">🦴 Évolution mobilité lombaire</div>',
                    unsafe_allow_html=True)
        mob_keys = [
            ("o_extension_mob",  "Extension"),
            ("o_lat_droite_mob", "Latéroflexion D"),
            ("o_lat_gauche_mob", "Latéroflexion G"),
            ("o_rot_droite_mob", "Rotation D"),
            ("o_rot_gauche_mob", "Rotation G"),
        ]
        MOB_NUM = {"1/3": 1, "2/3": 2, "3/3": 3}
        mob_table = [{"Bilan": lbl} for lbl in labels]
        for key, klabel in mob_keys:
            for i, (_, row) in enumerate(bilans_df.iterrows()):
                mob_table[i][klabel] = row.get(key, "—") or "—"

        # Graphique barres groupées
        fig_mob = go.Figure()
        colors_mob = ["#1a3c5e","#f57c00","#388e3c","#7b1fa2","#d32f2f"]
        for (key, klabel), color in zip(mob_keys, colors_mob):
            vals = [MOB_NUM.get(r.get(key,""), None) for _, r in bilans_df.iterrows()]
            fig_mob.add_trace(go.Bar(
                name=klabel, x=labels, y=vals,
                marker_color=color,
                text=[r.get(key,"—") or "—" for _, r in bilans_df.iterrows()],
                textposition="outside",
            ))
        fig_mob.update_layout(
            barmode="group", yaxis=dict(range=[0,4], tickvals=[1,2,3],
            ticktext=["1/3","2/3","3/3"], title="Amplitude"),
            xaxis_tickangle=-20, height=380, plot_bgcolor="white",
            legend=dict(orientation="h"),
        )
        st.plotly_chart(fig_mob, use_container_width=True)

        # Schober
        schober_vals = [safe_n(r.get("o_schober")) for _, r in bilans_df.iterrows()]
        if any(schober_vals):
            fig_sch = go.Figure()
            fig_sch.add_trace(go.Scatter(
                x=labels, y=schober_vals, mode="lines+markers+text",
                line=dict(color="#1a3c5e", width=2.5), marker=dict(size=9),
                text=[str(v) if v else "" for v in schober_vals],
                textposition="top center",
            ))
            fig_sch.add_hline(y=5, line_dash="dot", line_color="#388e3c",
                              annotation_text="5 cm (normal)", annotation_position="right")
            fig_sch.update_layout(title="Schober modifié (cm)", yaxis_title="cm",
                                  height=280, plot_bgcolor="white", xaxis_tickangle=-20)
            st.plotly_chart(fig_sch, use_container_width=True)

        st.dataframe(pd.DataFrame(mob_table), use_container_width=True, hide_index=True)

    # ── LUOMAJOKI ─────────────────────────────────────────────────────────────
    with tab_luom:
        st.markdown('<div class="section-title">🏃 Évolution tests de Luomajoki</div>',
                    unsafe_allow_html=True)
        luom_vals = [safe_n(r.get("o_luomajoki_score")) for _, r in bilans_df.iterrows()]
        if any(luom_vals):
            fig_luom = go.Figure()
            fig_luom.add_trace(go.Bar(
                x=labels, y=luom_vals,
                marker_color=["#d32f2f" if v and v>=3 else "#f57c00" if v and v>=1
                              else "#388e3c" for v in luom_vals],
                text=[f"{int(v)}/6" if v is not None else "—" for v in luom_vals],
                textposition="outside",
            ))
            fig_luom.add_hline(y=3, line_dash="dot", line_color="#d32f2f",
                               annotation_text="Seuil 3 (significatif)", annotation_position="right")
            fig_luom.update_layout(
                yaxis=dict(range=[0,7], title="Nombre d'échecs /6"),
                height=320, plot_bgcolor="white", xaxis_tickangle=-20,
            )
            st.plotly_chart(fig_luom, use_container_width=True)
        else:
            st.info("Aucun test de Luomajoki enregistré.")

        LUOM_NOMS = ["Waiters Bow","Pelvic Tilt","Knee Lift",
                     "One-Leg Stance","Sitting Knee Ext.","Prone Knee Bend"]
        LUOM_KEYS = ["o_luom_waiters_bow","o_luom_pelvic_tilt","o_luom_knee_lift",
                     "o_luom_one_leg_stance","o_luom_sitting_knee_ext","o_luom_prone_knee_bend"]
        luom_table = [{"Bilan": lbl} for lbl in labels]
        for nom, key in zip(LUOM_NOMS, LUOM_KEYS):
            for i, (_, row) in enumerate(bilans_df.iterrows()):
                luom_table[i][nom] = row.get(key,"—") or "—"
        luom_table_with_score = [{**row, "Score /6": bilans_df.iloc[i].get("o_luomajoki_score","—")}
                                  for i, row in enumerate(luom_table)]
        st.dataframe(pd.DataFrame(luom_table_with_score), use_container_width=True, hide_index=True)

    # ── SOAP SYNTHÈSE ─────────────────────────────────────────────────────────
    with tab_soap:
        st.markdown('<div class="section-title">📋 Synthèse SOAP par bilan</div>',
                    unsafe_allow_html=True)
        for lbl, (_, row) in zip(labels, bilans_df.iterrows()):
            with st.expander(f"📄 {lbl} — Groupe {row.get('groupe_clinique','—') or '—'}"):
                col_s, col_a = st.columns(2)
                with col_s:
                    st.markdown("**🟦 Subjectif**")
                    st.markdown(f"Motif : {row.get('s_motif_consultation','—') or '—'}")
                    st.markdown(f"Localisation : {str(row.get('s_douleur_localisation','')).replace('|',' · ') or '—'}")
                    st.markdown(f"Type douleur : {row.get('s_type_douleur','—') or '—'}")
                    st.markdown(f"EVA repos/mvt/nuit : {row.get('s_eva_repos','—')} / {row.get('s_eva_mouvement','—')} / {row.get('s_eva_nuit','—')}")
                    arret = row.get('s_arret_travail','—') or '—'
                    reveil = row.get('s_reveil_nuit','—') or '—'
                    st.markdown(f"Arrêt travail : **{arret}** | Réveil nocturne : **{reveil}**")
                with col_a:
                    st.markdown("**💡 Appréciation**")
                    st.markdown(row.get('a_appreciation','—') or '—')
                col_o, col_p = st.columns(2)
                with col_o:
                    st.markdown("**🔬 Objectif (scores)**")
                    st.markdown(f"ODI : {row.get('odi_score','—') or '—'}%")
                    st.markdown(f"Tampa : {row.get('tampa_score','—') or '—'}/68")
                    st.markdown(f"Örebro : {row.get('orebro_score','—') or '—'}")
                    st.markdown(f"Luomajoki : {row.get('o_luomajoki_score','—') or '—'}/6 échecs")
                with col_p:
                    st.markdown("**📋 Plan**")
                    st.markdown(row.get('p_objectifs','—') or '—')


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
elif mode == "evolution":
    if not st.session_state.lomb_patient_info:
        st.session_state.lomb_mode = "accueil"; st.rerun()
    render_evolution()
else:
    st.session_state.lomb_mode = "accueil"; st.rerun()
