"""
Page : Bilan SHV – Syndrome d'Hyperventilation
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, datetime
import io
import sys, os
# ─── Path ─────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.db import (
    get_all_patients, create_patient,
    get_patient_bilans, save_bilan, delete_bilan,
)
from utils.shv_data import HAD_QUESTIONS, compute_had_scores
from utils.shv_data import (
    SF12_QUESTIONS, SF12_KEYS, SF12_DIMENSIONS,
    compute_sf12_scores, interpret_pcs_mcs,
)
from utils.shv_data import (
    BOLT_DESCRIPTION, interpret_bolt,
    HVT_DESCRIPTION, HVT_SYMPTOMES,
)
from utils.shv_pdf import generate_pdf
from utils.shv_pdf import generate_questionnaires_pdf, QUESTIONNAIRES
from utils.shv_data import (
    NIJMEGEN_ITEMS, NIJMEGEN_OPTIONS, NIJMEGEN_KEYS, compute_nijmegen,
    GAZO_FIELDS, interpret_gazo,
    ETCO2_PATTERNS,
    PATTERN_MODES, PATTERN_AMPLITUDES, PATTERN_RYTHMES,
    interpret_mip_mep,
    MRC_GRADES,
    COMORB_CATEGORIES,
)

# ─── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bilan SHV",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .page-title  { font-size:2rem; font-weight:700; color:#1a3c5e; }
    .section-title { font-size:1.15rem; font-weight:600; color:#1a3c5e;
                     border-bottom:2px solid #e0ecf8; padding-bottom:4px; margin-bottom:1rem; }
    .score-box   { border-radius:10px; padding:1rem; text-align:center; color:white;
                   font-size:1.4rem; font-weight:700; }
    .info-box    { background:#f0f7ff; border-left:4px solid #1a3c5e;
                   padding:0.8rem 1rem; border-radius:0 8px 8px 0; margin-bottom:1rem; }
    .warn-box    { background:#fff8e1; border-left:4px solid #f9a825;
                   padding:0.8rem 1rem; border-radius:0 8px 8px 0; margin-bottom:1rem; }
    .success-box { background:#e8f5e9; border-left:4px solid #388e3c;
                   padding:0.8rem 1rem; border-radius:0 8px 8px 0; margin-bottom:1rem; }
    .patient-badge { background:#1a3c5e; color:white; border-radius:8px;
                     padding:0.4rem 1rem; display:inline-block; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ─── Helper: select_box avec valeur par défaut ────────────────────────────────
def sb(label, options, default=None, key=None):
    """Selectbox retournant le score (int) de l'option choisie.
    Affiche '— Non renseigné —' si aucune valeur stockée."""
    labels = ["— Non renseigné —"] + [o[1] for o in options]
    scores = [None]               + [o[0] for o in options]
    # Si valeur stockée → trouver son index, sinon rester sur 0 (non renseigné)
    idx = 0
    if default is not None and default in scores:
        idx = scores.index(default)
    chosen_label = st.selectbox(label, labels, index=idx, key=key)
    return scores[labels.index(chosen_label)]


# ─── État de session ───────────────────────────────────────────────────────────
def init_state():
    for k, v in {
        "patient_id": None,
        "patient_info": None,
        "bilan_id": None,
        "bilan_data": {},
        "mode": "accueil",  # accueil | recherche | nouveau_patient | bilan | formulaire | evolution
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 0 – ACCUEIL / SÉLECTION PATIENT
# ═══════════════════════════════════════════════════════════════════════════════

def render_accueil():
    st.markdown('<div class="page-title">🫁 Bilan SHV</div>', unsafe_allow_html=True)
    st.markdown("##### Syndrome d'hyperventilation – Gestion des patients")

    # ── Bouton impression questionnaires vierges ──────────────────────────────
    col_title, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🖨️ Imprimer questionnaires", key="print_accueil"):
            st.session_state["show_print_modal_accueil"] = True

    st.markdown("---")

    # ── Panneau d'impression (sans patient) ───────────────────────────────────
    if st.session_state.get("show_print_modal_accueil", False):
        with st.container():
            st.markdown("""
            <div style="background:#e8f0f8; border:2px solid #1a3c5e; border-radius:10px;
                        padding:1.2rem 1.5rem; margin-bottom:1rem;">
                <span style="font-size:1.1rem; font-weight:700; color:#1a3c5e;">
                🖨️ Imprimer des questionnaires vierges
                </span>
            </div>
            """, unsafe_allow_html=True)

            pcol1, pcol2, pcol3, pcol4, pcol5, pcol6, pcol7, pcol8 = st.columns(8)
            with pcol1:
                p_had  = st.checkbox("😟 HAD",       value=True, key="pa_had")
            with pcol2:
                p_sf12 = st.checkbox("📊 SF-12",     value=True, key="pa_sf12")
            with pcol3:
                p_hvt  = st.checkbox("🌬️ Test HV",   value=True, key="pa_hvt")
            with pcol4:
                p_bolt = st.checkbox("⏱️ BOLT",       value=True, key="pa_bolt")
            with pcol5:
                p_nij  = st.checkbox("📋 Nijmegen",  value=True, key="pa_nij")
            with pcol6:
                p_mrc  = st.checkbox("🚶 MRC",        value=True, key="pa_mrc")
            with pcol7:
                p_comb = st.checkbox("🏥 Comorb.",    value=True, key="pa_comb")
            with pcol8:
                p_musc = st.checkbox("💪 Testing", value=True, key="pa_musc")

            selected = []
            if p_had:  selected.append("had")
            if p_sf12: selected.append("sf12")
            if p_hvt:  selected.append("hvt")
            if p_bolt: selected.append("bolt")
            if p_nij:  selected.append("nijmegen")
            if p_mrc:  selected.append("mrc")
            if p_comb: selected.append("comorb")
            if p_musc: selected.append("muscle")

            ga, gb, _ = st.columns([1.5, 1, 4])
            with ga:
                if selected:
                    with st.spinner("Génération…"):
                        q_pdf = generate_questionnaires_pdf(selected, patient_info=None)
                    st.download_button(
                        label="📥 Télécharger le PDF",
                        data=q_pdf,
                        file_name=f"questionnaires_vierges_{date.today()}.pdf",
                        mime="application/pdf",
                        type="primary",
                        key="dl_q_accueil",
                    )
                else:
                    st.warning("Sélectionnez au moins un questionnaire.")
            with gb:
                if st.button("✖ Fermer", key="close_print_accueil"):
                    st.session_state["show_print_modal_accueil"] = False
                    st.rerun()

        st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🔍 Rechercher un patient existant")
        patients_df = get_all_patients()

        if patients_df.empty:
            st.info("Aucun patient enregistré pour le moment.")
        else:
            search = st.text_input("Recherche (nom, prénom)…", key="search_input")
            if search:
                mask = (
                    patients_df["nom"].str.contains(search.upper(), na=False) |
                    patients_df["prenom"].str.contains(search.capitalize(), na=False)
                )
                filtered = patients_df[mask]
            else:
                filtered = patients_df

            if filtered.empty:
                st.warning("Aucun résultat.")
            else:
                for _, row in filtered.iterrows():
                    with st.container():
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(
                                f"**{row['nom']} {row['prenom']}** &nbsp;|&nbsp; "
                                f"{row.get('date_naissance','—')} &nbsp;|&nbsp; "
                                f"ID : `{row['patient_id']}`",
                                unsafe_allow_html=True,
                            )
                        with c2:
                            if st.button("Sélectionner", key=f"sel_{row['patient_id']}"):
                                st.session_state.patient_id   = row["patient_id"]
                                st.session_state.patient_info = row.to_dict()
                                st.session_state.mode         = "bilan"
                                st.rerun()

    with col_b:
        st.markdown("#### ➕ Créer un nouveau patient")
        with st.form("form_new_patient", clear_on_submit=True):
            nom       = st.text_input("Nom *")
            prenom    = st.text_input("Prénom *")
            ddn       = st.date_input("Date de naissance *",
                                      min_value=date(1900, 1, 1),
                                      max_value=date.today())
            sexe      = st.selectbox("Sexe", ["Féminin", "Masculin", "Autre"])
            submitted = st.form_submit_button("➕ Créer", type="primary")

        if submitted:
            if not nom or not prenom:
                st.error("Le nom et le prénom sont obligatoires.")
            else:
                with st.spinner("Enregistrement…"):
                    pid = create_patient(nom, prenom, ddn, sexe, "")
                patients_df2 = get_all_patients()
                row = patients_df2[patients_df2["patient_id"] == pid].iloc[0]
                st.session_state.patient_id   = pid
                st.session_state.patient_info = row.to_dict()
                st.session_state.mode         = "bilan"
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 – SÉLECTION / CRÉATION DU BILAN
# ═══════════════════════════════════════════════════════════════════════════════

def render_bilan_selection():
    info = st.session_state.patient_info
    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— {info.get("date_naissance","—")} — ID : {info["patient_id"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    # Chargement des bilans en premier
    bilans_df = get_patient_bilans(st.session_state.patient_id)

    # Bilans filtrés selon la sélection
    def get_selected_bilans(df):
        sel = st.session_state.get("selected_bilan_ids", None)
        if sel is None or df.empty:
            return df
        filtered = df[df["bilan_id"].isin(sel)]
        return filtered if not filtered.empty else df

    col_back, col_evol, col_pdf, col_print, _ = st.columns([1, 1, 1.2, 1.5, 1])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            st.session_state.patient_id   = None
            st.session_state.patient_info = None
            st.session_state.bilan_id     = None
            st.session_state.bilan_data   = {}
            st.session_state.pop("selected_bilan_ids", None)
            st.session_state.mode         = "accueil"
            st.rerun()
    with col_evol:
        if not bilans_df.empty and len(bilans_df) >= 1:
            if st.button("📈 Voir l'évolution", type="primary"):
                st.session_state.mode = "evolution"
                st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            sel_df = get_selected_bilans(bilans_df)
            with st.spinner("Génération du PDF…"):
                pdf_bytes = generate_pdf(sel_df, info)
            n_sel = len(sel_df)
            st.download_button(
                label=f"📄 Exporter PDF ({n_sel} bilan{'s' if n_sel>1 else ''})",
                data=pdf_bytes,
                file_name=f"evolution_SHV_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf",
            )
    with col_print:
        if st.button("🖨️ Imprimer questionnaires"):
            st.session_state["show_print_modal"] = True

    st.markdown("---")

    # ── Panneau d'impression des questionnaires ───────────────────────────────
    if st.session_state.get("show_print_modal", False):
        with st.container():
            st.markdown("""
            <div style="background:#e8f0f8; border:2px solid #1a3c5e; border-radius:10px;
                        padding:1.2rem 1.5rem; margin-bottom:1rem;">
                <span style="font-size:1.1rem; font-weight:700; color:#1a3c5e;">
                🖨️ Sélectionner les questionnaires à imprimer
                </span>
            </div>
            """, unsafe_allow_html=True)

            pcol1, pcol2, pcol3, pcol4, pcol5, pcol6, pcol7, pcol8 = st.columns(8)
            with pcol1:
                print_had  = st.checkbox("😟 HAD",      value=True, key="print_had")
            with pcol2:
                print_sf12 = st.checkbox("📊 SF-12",    value=True, key="print_sf12")
            with pcol3:
                print_hvt  = st.checkbox("🌬️ Test HV",  value=True, key="print_hvt")
            with pcol4:
                print_bolt = st.checkbox("⏱️ BOLT",     value=True, key="print_bolt")
            with pcol5:
                print_nij  = st.checkbox("📋 Nijmegen", value=True, key="print_nij")
            with pcol6:
                print_mrc  = st.checkbox("🚶 MRC",      value=True, key="print_mrc")
            with pcol7:
                print_comb = st.checkbox("🏥 Comorb.",  value=True, key="print_comb")
            with pcol8:
                print_musc = st.checkbox("💪 Testing",value=True, key="print_musc")

            selected = []
            if print_had:  selected.append("had")
            if print_sf12: selected.append("sf12")
            if print_hvt:  selected.append("hvt")
            if print_bolt: selected.append("bolt")
            if print_nij:  selected.append("nijmegen")
            if print_mrc:  selected.append("mrc")
            if print_comb: selected.append("comorb")
            if print_musc: selected.append("muscle")

            ga, gb, gc = st.columns([1.5, 1, 4])
            with ga:
                if selected:
                    with st.spinner("Génération…"):
                        q_pdf = generate_questionnaires_pdf(selected, info)
                    st.download_button(
                        label="📥 Télécharger le PDF",
                        data=q_pdf,
                        file_name=f"questionnaires_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                        mime="application/pdf",
                        type="primary",
                        key="dl_questionnaires",
                    )
                else:
                    st.warning("Sélectionnez au moins un questionnaire.")
            with gb:
                if st.button("✖ Fermer", key="close_print"):
                    st.session_state["show_print_modal"] = False
                    st.rerun()


    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📋 Bilans existants")
        if bilans_df.empty:
            st.info("Aucun bilan pour ce patient.")
        else:
            # Sélection des bilans pour évolution/PDF
            st.markdown("<small style='color:#888'>Cochez les bilans à inclure dans l'évolution et le PDF</small>",
                        unsafe_allow_html=True)

            selected_ids = st.session_state.get("selected_bilan_ids", None)
            if selected_ids is None:
                # Tout coché par défaut
                selected_ids = list(bilans_df["bilan_id"])
                st.session_state["selected_bilan_ids"] = selected_ids

            # Nettoyage : retirer les IDs qui n'existent plus
            valid_ids = list(bilans_df["bilan_id"])
            selected_ids = [i for i in selected_ids if i in valid_ids]
            st.session_state["selected_bilan_ids"] = selected_ids

            new_selected = []
            for _, row in bilans_df.iterrows():
                bid   = row.get("bilan_id", "—")
                bdate = row.get("date_bilan", "—")
                btype = row.get("type_bilan", "—")

                c_check, c_info, c_open, c_del = st.columns([0.5, 3.5, 0.8, 0.8])
                with c_check:
                    checked = st.checkbox("", value=bid in selected_ids,
                                         key=f"sel_{bid}", label_visibility="collapsed")
                    if checked:
                        new_selected.append(bid)
                with c_info:
                    st.markdown(f"**{bdate}** — {btype}  \n<small>`{bid}`</small>",
                                unsafe_allow_html=True)
                with c_open:
                    if st.button("✏️", key=f"open_{bid}", help="Ouvrir ce bilan"):
                        st.session_state.bilan_id   = bid
                        st.session_state.bilan_data = row.to_dict()
                        st.session_state.mode       = "formulaire"
                        st.session_state["shv_unsaved"] = False
                        st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"del_req_{bid}", help="Supprimer ce bilan"):
                        st.session_state[f"confirm_del_{bid}"] = True

                # Confirmation suppression
                if st.session_state.get(f"confirm_del_{bid}", False):
                    st.warning(
                        f"⚠️ Supprimer définitivement le bilan **{bdate} — {btype}** ? "
                        "Cette action est irréversible."
                    )
                    ca, cb, _ = st.columns([1, 1, 3])
                    with ca:
                        if st.button("✅ Confirmer", key=f"del_ok_{bid}", type="primary"):
                            with st.spinner("Suppression…"):
                                ok = delete_bilan(bid)
                            if ok:
                                st.success("Bilan supprimé.")
                            else:
                                st.error("Erreur lors de la suppression.")
                            st.session_state.pop(f"confirm_del_{bid}", None)
                            # Mettre à jour la sélection
                            st.session_state["selected_bilan_ids"] = [
                                i for i in selected_ids if i != bid]
                            st.rerun()
                    with cb:
                        if st.button("✖ Annuler", key=f"del_cancel_{bid}"):
                            st.session_state.pop(f"confirm_del_{bid}", None)
                            st.rerun()

            st.session_state["selected_bilan_ids"] = new_selected

            # Info nombre sélectionné
            n_sel = len(new_selected)
            n_tot = len(bilans_df)
            if n_sel < n_tot:
                st.markdown(
                    f"<small style='color:#f57c00'>⚡ {n_sel}/{n_tot} bilans sélectionnés "
                    f"pour l'évolution</small>",
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown("#### ➕ Nouveau bilan SHV")
        with st.form("form_new_bilan"):
            bilan_date = st.date_input("Date du bilan", value=date.today())
            bilan_type = st.selectbox(
                "Type de bilan",
                ["Bilan initial", "Bilan intermédiaire", "Bilan final"]
            )
            praticien  = st.text_input("Praticien")
            go_btn     = st.form_submit_button("➕ Créer", type="primary")

        if go_btn:
            st.session_state.bilan_id   = None  # sera généré à la sauvegarde
            st.session_state.bilan_data = {
                "patient_id": st.session_state.patient_id,
                "date_bilan": str(bilan_date),
                "type_bilan": bilan_type,
                "praticien":  praticien,
            }
            st.session_state.mode = "formulaire"
            st.session_state["shv_unsaved"] = True
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 – FORMULAIRE BILAN
# ═══════════════════════════════════════════════════════════════════════════════

def safe_float(val, default=0.0):
    """Convertit en float sans planter sur une chaîne invalide."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def load_val(key, default=None):
    """Récupère une valeur existante du bilan (si re-chargement)."""
    v = st.session_state.bilan_data.get(key)
    if v is None or v == "":
        return default
    try:
        return int(v)
    except (ValueError, TypeError):
        return v


def load_val_or_none(key):
    """Returns stored value or None for blank number_input."""
    v = load_val(key)
    if v is None: return None
    try:
        result = float(v)
        return int(result) if result == int(result) else result
    except: return None





def highlight_filled_tabs(tab_definitions: list):
    """Fond vert sur les onglets remplis via CSS nth-child."""
    bd = st.session_state.get("bilan_data", {})
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

    info = st.session_state.patient_info
    bd   = st.session_state.bilan_data

    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— Bilan : {bd.get("type_bilan","—")} du {bd.get("date_bilan","—")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    col_back, col_save, _ = st.columns([1, 1, 4])
    with col_back:
        if st.button("⬅️ Retour"):
            # Toujours demander confirmation sauf si venait de sauvegarder
            if not st.session_state.get("shv_just_saved", False):
                st.session_state["shv_confirm_back"] = True
            else:
                st.session_state.pop("shv_just_saved", None)
                st.session_state.mode = "bilan"
                st.rerun()
    with col_save:
        save_top = st.button("💾 Sauvegarder", type="primary")

    # Alerte si retour sans sauvegarde
    if st.session_state.get("shv_confirm_back", False):
        st.warning(
            "⚠️ **Modifications non sauvegardées.** "
            "Êtes-vous sûr(e) de vouloir quitter sans sauvegarder ?"
        )
        ca, cb, _ = st.columns([1.2, 1.2, 4])
        with ca:
            if st.button("🚪 Quitter sans sauvegarder", type="primary", key="shv_confirm_back_ok"):
                st.session_state["shv_confirm_back"] = False
                st.session_state["shv_unsaved"] = False
                st.session_state.mode = "bilan"
                st.rerun()
        with cb:
            if st.button("✏️ Continuer l'édition", key="shv_confirm_back_cancel"):
                st.session_state["shv_confirm_back"] = False
                st.rerun()

    st.markdown("---")

    # ──── Onglets ────────────────────────────────────────────────────────────
    tab_gen, tab_had, tab_sf12, tab_bolt, tab_hvt, \
    tab_nij, tab_gazo, tab_etco2, tab_pattern, tab_snif, tab_mrc, tab_comorb, tab_muscle = st.tabs([
        "📝 Général",
        "😟 HAD",
        "📊 SF-12",
        "⏱️ BOLT",
        "🌬️ Test HV",
        "📋 Nijmegen",
        "🧪 Gazométrie",
        "📈 Capnographie",
        "🔬 Pattern respi.",
        "💪 SNIF/PImax/PEmax",
        "🚶 MRC Dyspnée",
        "🏥 Comorbidités",
        "💪 Testing",
    ])

    # Pré-remplir depuis les données existantes pour ne pas perdre les valeurs non visitées
    collected = dict(st.session_state.bilan_data)
    highlight_filled_tabs([
        ("📝 Général",            []),
        ("😟 HAD",                ["had_score_anxiete","had_score_depression"]),
        ("📊 SF-12",              ["sf12_pcs","sf12_mcs"]),
        ("⏱️ BOLT",               ["bolt_score"]),
        ("🌬️ Test HV",            ["hvt_symptomes_reproduits","hvt_repos_0_petco2"]),
        ("📋 Nijmegen",           ["nij_score"]),
        ("🧪 Gazométrie",         ["gazo_ph","gazo_paco2","gazo_sato2"]),
        ("📈 Capnographie",       ["etco2_repos","etco2_pattern"]),
        ("🔬 Pattern respi.",     ["pattern_frequence","pattern_mode"]),
        ("💪 SNIF/PImax/PEmax",   ["snif_val","pimax_val","pemax_val"]),
        ("🚶 MRC Dyspnée",        ["mrc_score"]),
        ("🏥 Comorbidités",       ["comorb_list","comorb_traitements"]),
        ("💪 Testing",            ["musc_hip_flex_d","musc_knee_ext_d"]),
    ])

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 1 – GÉNÉRAL
    # ═════════════════════════════════════════════════════════════════════════
    with tab_gen:
        st.markdown('<div class="section-title">📝 Informations générales du bilan</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            bilan_date = st.date_input(
                "Date du bilan",
                value=date.fromisoformat(bd.get("date_bilan", str(date.today()))),
                key="g_date",
            )
            bilan_type = st.selectbox(
                "Type de bilan",
                ["Bilan initial", "Bilan intermédiaire", "Bilan final"],
                index=["Bilan initial", "Bilan intermédiaire", "Bilan final"].index(
                    bd.get("type_bilan", "Bilan initial")
                ),
                key="g_type",
            )
        with c2:
            praticien = st.text_input("Praticien", value=bd.get("praticien", ""), key="g_prat")
            notes_gen = st.text_area("Notes générales", value=bd.get("notes_generales", ""),
                                     height=120, key="g_notes")

        collected.update({
            "date_bilan":      str(bilan_date),
            "type_bilan":      bilan_type,
            "praticien":       praticien,
            "notes_generales": notes_gen,
        })

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 2 – HAD
    # ═════════════════════════════════════════════════════════════════════════
    with tab_had:
        st.markdown('<div class="section-title">😟 Échelle HAD — Anxiété & Dépression</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Questionnaire auto-rapporté de 14 items. '
            'Score 0–7 : normal · 8–10 : douteux · 11–21 : pathologique</div>',
            unsafe_allow_html=True,
        )

        had_answers = {}
        for key, subscale, question, options in HAD_QUESTIONS:
            label = f"({'A' if subscale == 'A' else 'D'}) {question}"
            val = load_val(f"had_{key}")
            scores_list = [o[0] for o in options]
            default_idx = scores_list.index(val) if val in scores_list else 0
            had_answers[key] = st.radio(
                label,
                options=[o[0] for o in options],
                format_func=lambda x, opts=options: next(l for s, l in opts if s == x),
                index=default_idx,
                horizontal=True,
                key=f"had_{key}",
            )

        # Scores
        had_scores = compute_had_scores(had_answers)
        st.markdown("---")
        st.markdown("#### 📊 Résultats HAD")
        ca, cd = st.columns(2)

        def had_color(s):
            if s <= 7: return "#388e3c"
            if s <= 10: return "#f57c00"
            return "#d32f2f"

        with ca:
            st.markdown(
                f'<div class="score-box" style="background:{had_color(had_scores["score_anxiete"])};">'
                f'Anxiété : {had_scores["score_anxiete"]}/21<br>'
                f'<small style="font-size:.75rem">{had_scores["interp_anxiete"]}</small></div>',
                unsafe_allow_html=True,
            )
        with cd:
            st.markdown(
                f'<div class="score-box" style="background:{had_color(had_scores["score_depression"])};">'
                f'Dépression : {had_scores["score_depression"]}/21<br>'
                f'<small style="font-size:.75rem">{had_scores["interp_depression"]}</small></div>',
                unsafe_allow_html=True,
            )

        # Stocker
        for key in had_answers:
            collected[f"had_{key}"] = had_answers[key]
        collected["had_score_anxiete"]    = had_scores["score_anxiete"]
        collected["had_score_depression"] = had_scores["score_depression"]

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 3 – SF-12
    # ═════════════════════════════════════════════════════════════════════════
    with tab_sf12:
        st.markdown('<div class="section-title">📊 SF-12 — Qualité de vie</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">12 questions mesurant 8 dimensions de la qualité de vie, '
            'et deux scores composites : <strong>PCS-12</strong> (physique) et <strong>MCS-12</strong> (mental). '
            'Score de référence = 50 (moyenne population générale).</div>',
            unsafe_allow_html=True,
        )

        sf_ans = {}
        last_intro = None

        for q in SF12_QUESTIONS:
            key     = q["key"]
            options = q["options"]
            intro   = q.get("intro")

            # Afficher l'intro une seule fois par groupe
            if intro and intro != last_intro:
                st.markdown(f"---\n*{intro}*")
                last_intro = intro

            sf_ans[key] = sb(
                q["texte"], options,
                default=load_val(f"sf12_{key}"),
                key=f"sf12_{key}",
            )

        # ── Scores SF-12 ─────────────────────────────────────────────────────
        sf_scores = compute_sf12_scores(sf_ans)
        st.markdown("---")
        st.markdown("#### 📊 Résultats SF-12")

        # Scores composites PCS / MCS en gros encadrés
        cp1, cp2 = st.columns(2)
        def pcs_mcs_color(s):
            if s is None: return "#888"
            if s >= 55:   return "#388e3c"
            if s >= 45:   return "#2196f3"
            if s >= 35:   return "#f57c00"
            return "#d32f2f"

        with cp1:
            pcs = sf_scores.get("pcs")
            st.markdown(
                f'<div class="score-box" style="background:{pcs_mcs_color(pcs)};">'
                f'PCS-12 : {pcs if pcs is not None else "—"}<br>'
                f'<small style="font-size:.75rem">Score composite physique<br>'
                f'{interpret_pcs_mcs(pcs)}</small></div>',
                unsafe_allow_html=True,
            )
        with cp2:
            mcs = sf_scores.get("mcs")
            st.markdown(
                f'<div class="score-box" style="background:{pcs_mcs_color(mcs)};">'
                f'MCS-12 : {mcs if mcs is not None else "—"}<br>'
                f'<small style="font-size:.75rem">Score composite mental<br>'
                f'{interpret_pcs_mcs(mcs)}</small></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Graphique barres 8 dimensions
        dim_keys_plot = ["pf", "rp", "bp", "gh", "vt", "sf", "re", "mh"]
        dim_labels_plot = [SF12_DIMENSIONS[k] for k in dim_keys_plot]
        scores_vals = [sf_scores.get(k) or 0 for k in dim_keys_plot]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dim_labels_plot,
            y=scores_vals,
            marker_color=["#388e3c" if s >= 66 else "#f57c00" if s >= 33 else "#d32f2f"
                          for s in scores_vals],
            text=[f"{s}" for s in scores_vals],
            textposition="outside",
        ))
        fig.update_layout(
            yaxis=dict(range=[0, 115], title="Score (0–100)"),
            xaxis_tickangle=-30,
            height=360,
            margin=dict(t=20, b=80),
            plot_bgcolor="white",
        )
        fig.add_hline(y=50, line_dash="dot", line_color="grey",
                      annotation_text="50 (référence)", annotation_position="right")
        st.plotly_chart(fig, use_container_width=True)

        # Stocker
        for k, v in sf_ans.items():
            collected[f"sf12_{k}"] = v if v is not None else ""
        for dim_key, dim_val in sf_scores.items():
            collected[f"sf12_{dim_key}"] = dim_val if dim_val is not None else ""

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 4 – BOLT
    # ═════════════════════════════════════════════════════════════════════════
    with tab_bolt:
        st.markdown('<div class="section-title">⏱️ BOLT – Body Oxygen Level Test</div>',
                    unsafe_allow_html=True)
        st.markdown(BOLT_DESCRIPTION)

        bolt_val = st.number_input(
            "Résultat BOLT (secondes)",
            min_value=0, max_value=120,
            value=(int(load_val("bolt_score")) if load_val("bolt_score") else None),
            help="Laisser à 0 si non réalisé",
            step=1,
            key="bolt_input",
        )

        if bolt_val is not None and bolt_val > 0:
            interp = interpret_bolt(bolt_val)
            st.markdown(
                f'<div class="score-box" style="background:{interp["color"]};">'
                f'{bolt_val} s — {interp["cat"]}<br>'
                f'<small style="font-size:.8rem">{interp["desc"]}</small></div>',
                unsafe_allow_html=True,
            )
            collected["bolt_score"]          = bolt_val if bolt_val is not None else ""
            collected["bolt_interpretation"] = interp["cat"]
        else:
            collected["bolt_score"]          = ""
            collected["bolt_interpretation"] = ""

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 5 – TEST HYPERVENTILATION VOLONTAIRE
    # ═════════════════════════════════════════════════════════════════════════
    with tab_hvt:
        st.markdown('<div class="section-title">🌬️ Test d\'hyperventilation volontaire</div>',
                    unsafe_allow_html=True)
        st.markdown(HVT_DESCRIPTION)

        # ── Grille de mesures ─────────────────────────────────────────────────
        st.markdown("#### 📊 Grille de mesures")
        st.markdown(
            '<div class="info-box">Entrez les valeurs mesurées à chaque temps. '
            'Laissez à 0 si non mesuré.</div>',
            unsafe_allow_html=True,
        )

        # Définition des phases et time points
        HVT_PHASES = [
            ("repos", "🟦 Repos",        [0, 1, 2, 3]),
            ("hv",    "🔴 HV",           [1, 2, 3]),
            ("rec",   "🟩 Récupération", [1, 2, 3, 4, 5]),
        ]
        HVT_PARAMS = [
            ("petco2", "PetCO₂ (mmHg)", 0.0, 80.0, 0.5),
            ("fr",     "FR (cyc/min)",  0.0, 60.0, 1.0),
            ("spo2",   "SpO₂ (%)",      0.0, 100.0, 0.5),
            ("fc",     "FC (bpm)",      0.0, 220.0, 1.0),
        ]

        hvt_grid = {}

        for phase_key, phase_label, times in HVT_PHASES:
            st.markdown(f"**{phase_label}**")
            col_headers = st.columns([1.2] + [1]*len(HVT_PARAMS))
            col_headers[0].markdown("**Temps**")
            for j, (p_key, p_label, *_) in enumerate(HVT_PARAMS):
                col_headers[j+1].markdown(f"**{p_label}**")

            for t in times:
                row_cols = st.columns([1.2] + [1]*len(HVT_PARAMS))
                row_cols[0].markdown(
                    f"<small>{'T0' if t == 0 else f'{t} min'}</small>",
                    unsafe_allow_html=True,
                )
                for j, (p_key, p_label, *_) in enumerate(HVT_PARAMS):
                    cell_key = f"hvt_{phase_key}_{t}_{p_key}"
                    stored   = load_val(cell_key)
                    # Afficher vide si pas de valeur
                    display  = str(int(safe_float(stored))) if stored else ""
                    entered  = row_cols[j+1].text_input(
                        label="",
                        value=display,
                        key=f"grid_{cell_key}",
                        label_visibility="collapsed",
                        placeholder="—",
                    )
                    # Stocker uniquement si valeur valide
                    try:
                        hvt_grid[cell_key] = int(float(entered)) if entered.strip() else ""
                    except (ValueError, AttributeError):
                        hvt_grid[cell_key] = ""
            st.markdown("---")

        # Graphique temps réel des 4 paramètres
        st.markdown("#### 📈 Visualisation")

        import plotly.graph_objects as go_local
        from plotly.subplots import make_subplots as ms_local

        # Construire les séries temporelles
        all_times_labels = (
            ["T0", "R1'", "R2'", "R3'",
             "HV1'", "HV2'", "HV3'",
             "Rec1'", "Rec2'", "Rec3'", "Rec4'", "Rec5'"]
        )
        all_keys = (
            [("repos", t) for t in [0,1,2,3]] +
            [("hv",    t) for t in [1,2,3]] +
            [("rec",   t) for t in [1,2,3,4,5]]
        )

        fig_hvt_grid = ms_local(rows=2, cols=2,
                                subplot_titles=["PetCO₂ (mmHg)","FR (cyc/min)","SpO₂ (%)","FC (bpm)"],
                                shared_xaxes=False)
        param_positions = [("petco2",1,1,"#1a3c5e"), ("fr",1,2,"#f57c00"),
                           ("spo2",2,1,"#388e3c"),  ("fc",2,2,"#7b1fa2")]

        # Lignes séparatrices phases
        phase_sep_x = [3.5, 6.5]  # entre repos/HV et HV/rec

        for p_key, r, c, color in param_positions:
            y_vals = []
            for ph_key, t in all_keys:
                k = f"hvt_{ph_key}_{t}_{p_key}"
                v = hvt_grid.get(k) or load_val(k)
                try:
                    y_vals.append(float(v) if v else None)
                except (TypeError, ValueError):
                    y_vals.append(None)

            fig_hvt_grid.add_trace(
                go_local.Scatter(
                    x=all_times_labels, y=y_vals,
                    mode="lines+markers",
                    line=dict(color=color, width=2.5),
                    marker=dict(size=8),
                    showlegend=False,
                    connectgaps=False,
                ),
                row=r, col=c,
            )
            # Zones de couleur
            for sep in phase_sep_x:
                fig_hvt_grid.add_vline(x=sep, line_dash="dot",
                                       line_color="grey", line_width=1,
                                       row=r, col=c)

        # Référence PetCO2
        fig_hvt_grid.add_hline(y=35, line_dash="dot", line_color="#d32f2f",
                                annotation_text="35 mmHg", row=1, col=1)
        fig_hvt_grid.add_hline(y=45, line_dash="dot", line_color="#388e3c",
                                annotation_text="45 mmHg", row=1, col=1)
        # Référence SpO2
        fig_hvt_grid.add_hline(y=95, line_dash="dot", line_color="#f57c00",
                                annotation_text="95%", row=2, col=1)

        fig_hvt_grid.update_layout(
            height=500, plot_bgcolor="white",
            margin=dict(t=40, b=20),
        )
        fig_hvt_grid.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_hvt_grid, use_container_width=True)

        # ── Résultat global ───────────────────────────────────────────────────
        st.markdown("#### 🏁 Résultat global")
        col_hvt1, col_hvt2 = st.columns(2)
        with col_hvt1:
            hvt_reproduits = st.radio(
                "Le test reproduit-il les symptômes habituels du patient ?",
                ["Non réalisé", "Oui ✅", "Partiellement ⚠️", "Non ❌"],
                index=["Non réalisé", "Oui ✅", "Partiellement ⚠️", "Non ❌"].index(
                    load_val("hvt_symptomes_reproduits", "Non réalisé")
                    if load_val("hvt_symptomes_reproduits", "Non réalisé")
                       in ["Non réalisé", "Oui ✅", "Partiellement ⚠️", "Non ❌"]
                    else "Non réalisé"
                ),
                key="hvt_rep",
            )
        with col_hvt2:
            hvt_duree = st.number_input(
                "Temps de retour à la normale (minutes)",
                min_value=0, max_value=60,
                value=(int(load_val("hvt_duree_retour")) if load_val("hvt_duree_retour") else None),
                help="Laisser à 0 si non mesuré",
                step=1, key="hvt_duree",
            )

        # Symptômes
        existing_symptomes = str(load_val("hvt_symptomes_list", "") or "").split("|")
        symptomes_selectionnes = st.multiselect(
            "Symptômes reproduits pendant le test :",
            HVT_SYMPTOMES,
            default=[s for s in existing_symptomes if s in HVT_SYMPTOMES],
            key="hvt_symptomes",
        )

        hvt_notes = st.text_area(
            "Observations / notes cliniques",
            value=str(load_val("hvt_notes", "") or ""),
            height=100, key="hvt_notes_field",
        )

        if "Oui ✅" in hvt_reproduits:
            st.markdown(
                '<div class="success-box">✅ <strong>Test positif</strong> — '
                'Confirme le diagnostic de SHV.</div>', unsafe_allow_html=True,
            )
        elif "Partiellement" in hvt_reproduits:
            st.markdown(
                '<div class="warn-box">⚠️ <strong>Test partiellement positif</strong> — '
                'Arguments en faveur d\'un SHV.</div>', unsafe_allow_html=True,
            )

        collected.update({
            "hvt_symptomes_reproduits": hvt_reproduits,
            "hvt_symptomes_list":       "|".join(symptomes_selectionnes),
            "hvt_duree_retour":         hvt_duree if (hvt_duree is not None and hvt_duree > 0) else "",
            "hvt_notes":                hvt_notes,
            **hvt_grid,
        })

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 6 – NIJMEGEN
    # ═════════════════════════════════════════════════════════════════════════
    with tab_nij:
        st.markdown('<div class="section-title">📋 Questionnaire de Nijmegen</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">16 symptômes cotés de 0 (jamais) à 4 (très souvent). '
            'Score ≥ 23 : SHV probable · 15–22 : borderline · &lt; 15 : peu probable.</div>',
            unsafe_allow_html=True,
        )
        nij_answers = {}
        for i, item in enumerate(NIJMEGEN_ITEMS):
            key = f"nij_{i+1}"
            val = load_val(key)
            # Options avec "— Non renseigné —" en premier (valeur None)
            opts_extended = [None] + [o[0] for o in NIJMEGEN_OPTIONS]
            def _nij_fmt(x, opts=NIJMEGEN_OPTIONS):
                if x is None: return "— Non renseigné —"
                return next(l for s, l in opts if s == x)
            stored_score = int(float(val)) if val is not None and str(val).strip() not in ("", "None") else None
            default_idx = opts_extended.index(stored_score) if stored_score in opts_extended else 0
            chosen = st.radio(
                f"{i+1}. {item}",
                options=opts_extended,
                format_func=_nij_fmt,
                index=default_idx, horizontal=True,
                key=f"nij_r_{i+1}",
            )
            if chosen is not None:
                nij_answers[key] = chosen

        nij_result = compute_nijmegen(nij_answers)
        st.markdown("---")
        if nij_result["score"] is not None:
            st.markdown(
                f'<div class="score-box" style="background:{nij_result["color"]};">'
                f'Score Nijmegen : {nij_result["score"]} / 64<br>'
                f'<small style="font-size:.8rem">{nij_result["interpretation"]}</small></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="info-box">Remplissez les items pour calculer le score.</div>',
                        unsafe_allow_html=True)
        for k, v in nij_answers.items():
            collected[k] = v
        # Stocker "" pour les items non renseignés
        all_nij_keys = [f"nij_{i+1}" for i in range(len(NIJMEGEN_ITEMS))]
        for k in all_nij_keys:
            if k not in nij_answers:
                collected[k] = ""
        collected["nij_score"]          = nij_result["score"] if nij_result["score"] is not None else ""
        collected["nij_interpretation"] = nij_result["interpretation"]

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 7 – GAZOMÉTRIE
    # ═════════════════════════════════════════════════════════════════════════
    with tab_gazo:
        st.markdown('<div class="section-title">🧪 Gazométrie</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Valeurs normales : pH 7.35–7.45 · PaCO₂ 35–45 mmHg · '
            'PaO₂ 75–100 mmHg · HCO₃⁻ 22–26 mmol/L · SatO₂ ≥ 95%</div>',
            unsafe_allow_html=True,
        )
        g_type_opts = ["— Non renseigné —", "Artériel", "Veineux", "Capillaire", "Non réalisé"]
        g_type_val  = str(load_val("gazo_type") or "Non réalisé")
        g_type_idx  = g_type_opts.index(g_type_val) if g_type_val in g_type_opts else 3
        gazo_type   = st.selectbox("Type de prélèvement", g_type_opts, index=g_type_idx, key="gazo_type")

        gc1, gc2 = st.columns(2)
        gazo_vals = {}
        num_fields = [("gazo_ph","pH","7.35–7.45"), ("gazo_paco2","PaCO₂ (mmHg)","35–45"),
                      ("gazo_pao2","PaO₂ (mmHg)","75–100"), ("gazo_hco3","HCO₃⁻ (mmol/L)","22–26"),
                      ("gazo_sato2","SatO₂ (%)","≥ 95"), ("gazo_fio2","FiO₂ (%)","21 air ambiant")]
        for i, (fkey, flabel, fref) in enumerate(num_fields):
            col = gc1 if i % 2 == 0 else gc2
            with col:
                raw = load_val(fkey)
                val_in = safe_float(raw)
                entered = st.number_input(f"{flabel} ({fref})", value=val_in,
                                          step=0.1, format="%.2f", key=fkey)
                gazo_vals[fkey] = entered if entered != 0.0 else ""
                if entered and entered != 0.0:
                    ok, msg = interpret_gazo(fkey, entered)
                    if ok is not None:
                        color = "#388e3c" if ok else "#d32f2f"
                        st.markdown(f'<small style="color:{color}">{msg}</small>',
                                    unsafe_allow_html=True)
        gazo_notes = st.text_area("Notes / contexte", value=str(load_val("gazo_notes") or ""),
                                  height=80, key="gazo_notes_field")
        collected.update({"gazo_type": gazo_type, **gazo_vals, "gazo_notes": gazo_notes})

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 8 – CAPNOGRAPHIE
    # ═════════════════════════════════════════════════════════════════════════
    with tab_etco2:
        st.markdown('<div class="section-title">📈 Capnographie — ETCO₂</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">ETCO₂ normal au repos : <strong>35–45 mmHg</strong>. '
            'Valeur abaissée = hypocapnie = argument fort pour le SHV.</div>',
            unsafe_allow_html=True,
        )
        ec1, ec2 = st.columns(2)
        with ec1:
            etco2_repos = st.number_input(
                "ETCO₂ au repos (mmHg)", min_value=0.0, max_value=80.0,
                value=safe_float(load_val("etco2_repos")), step=0.5, key="etco2_repos", help="0 = non mesuré",
            )
            if etco2_repos is not None and etco2_repos > 0:
                color = "#388e3c" if 35 <= etco2_repos <= 45 else "#f57c00" if etco2_repos >= 30 else "#d32f2f"
                label = "Normal" if 35 <= etco2_repos <= 45 else "Hypocapnie" if etco2_repos < 35 else "Hypercapnie"
                st.markdown(f'<small style="color:{color}">▶ {label}</small>', unsafe_allow_html=True)
        with ec2:
            etco2_effort = st.number_input(
                "ETCO₂ post-effort (mmHg)", min_value=0.0, max_value=80.0,
                value=safe_float(load_val("etco2_post_effort")), step=0.5, key="etco2_effort", help="0 = non mesuré",
            )

        pat_opts  = ETCO2_PATTERNS
        pat_opts  = ["— Non renseigné —"] + list(pat_opts)
        pat_val   = str(load_val("etco2_pattern") or "")
        pat_idx   = pat_opts.index(pat_val) if pat_val in pat_opts else 0
        etco2_pat = st.selectbox("Pattern capnographique", pat_opts, index=pat_idx, key="etco2_pat")
        etco2_notes = st.text_area("Notes", value=str(load_val("etco2_notes") or ""),
                                   height=80, key="etco2_notes")
        collected.update({
            "etco2_repos": etco2_repos or "", "etco2_post_effort": etco2_effort or "",
            "etco2_pattern": etco2_pat, "etco2_notes": etco2_notes,
        })

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 9 – PATTERN RESPIRATOIRE
    # ═════════════════════════════════════════════════════════════════════════
    with tab_pattern:
        st.markdown('<div class="section-title">🔬 Pattern respiratoire</div>',
                    unsafe_allow_html=True)
        pc1, pc2 = st.columns(2)
        with pc1:
            pat_freq = st.number_input(
                "Fréquence respiratoire (cycles/min)", min_value=0, max_value=60,
                value=(int(load_val("pattern_frequence")) if load_val("pattern_frequence") else None), step=1, key="pat_freq",
                help="Laisser à 0 si non mesuré",
            )
            if pat_freq is not None and pat_freq > 0:
                color = "#388e3c" if 12 <= pat_freq <= 18 else "#f57c00" if pat_freq <= 20 else "#d32f2f"
                st.markdown(f'<small style="color:{color}">Normale : 12–18 · Tachypnée : &gt; 20</small>',
                            unsafe_allow_html=True)

            def radio_load(label, opts, key):
                opts_with_empty = ["— Non renseigné —"] + list(opts)
                val = str(load_val(key) or "")
                idx = opts_with_empty.index(val) if val in opts_with_empty else 0
                chosen = st.radio(label, opts_with_empty, index=idx, key=key)
                return "" if chosen == "— Non renseigné —" else chosen

            pat_amp  = radio_load("Amplitude", PATTERN_AMPLITUDES, "pat_amp")
        with pc2:
            pat_mode = radio_load("Mode ventilatoire", PATTERN_MODES, "pat_mode")
            pat_ryt  = radio_load("Rythme", PATTERN_RYTHMES, "pat_rythme")

        pat_para  = st.checkbox("Respiration paradoxale", value=bool(load_val("pattern_paradoxal")),
                                key="pat_paradoxal")
        pat_notes = st.text_area("Observations cliniques",
                                 value=str(load_val("pattern_notes") or ""),
                                 height=100, key="pat_notes")
        collected.update({
            "pattern_frequence": pat_freq if pat_freq is not None else "", "pattern_amplitude": pat_amp,
            "pattern_mode": pat_mode, "pattern_rythme": pat_ryt,
            "pattern_paradoxal": "Oui" if pat_para else "Non",
            "pattern_notes": pat_notes,
        })

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 10 – SNIF / PImax / PEmax
    # ═════════════════════════════════════════════════════════════════════════
    with tab_snif:
        st.markdown('<div class="section-title">💪 SNIF Test · PImax · PEmax</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">'
            '<strong>SNIF</strong> : Sniff Nasal Inspiratory Pressure — effort inspiratoire maximal nasal. '
            '<strong>PImax</strong> : Pression Inspiratoire Maximale (MIP). '
            '<strong>PEmax</strong> : Pression Expiratoire Maximale (MEP). '
            'Valeur normale : ≥ 80% de la valeur prédite.</div>',
            unsafe_allow_html=True,
        )

        def muscle_row(label, key_val, key_pred, key_pct):
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                _v_stored = load_val(key_val)
                v = st.number_input(f"{label} — Mesuré (cmH₂O)",
                                    value=(safe_float(_v_stored) if _v_stored else None),
                                    step=1.0, key=key_val)
            with sc2:
                _p_stored = load_val(key_pred)
                p = st.number_input(f"{label} — Prédit (cmH₂O)",
                                    value=(safe_float(_p_stored) if _p_stored else None),
                                    step=1.0, key=key_pred)
            with sc3:
                if v and p:
                    pct, interp_txt, color = interpret_mip_mep(v, p)
                    st.metric(f"{label} % prédit", f"{pct:.0f}%" if pct else "—")
                    st.markdown(f'<small style="color:{color}">{interp_txt}</small>',
                                unsafe_allow_html=True)
                    collected[key_pct] = round(pct, 1) if pct else ""
                else:
                    collected[key_pct] = ""
            collected[key_val]  = v or ""
            collected[key_pred] = p or ""

        muscle_row("SNIF",  "snif_val",  "snif_pred",  "snif_pct")
        st.markdown("---")
        muscle_row("PImax", "pimax_val", "pimax_pred", "pimax_pct")
        st.markdown("---")
        muscle_row("PEmax", "pemax_val", "pemax_pred", "pemax_pct")

        snif_notes = st.text_area("Notes", value=str(load_val("snif_pimax_pemax_notes") or ""),
                                  height=80, key="snif_notes")
        collected["snif_pimax_pemax_notes"] = snif_notes

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 11 – MRC DYSPNÉE
    # ═════════════════════════════════════════════════════════════════════════
    with tab_mrc:
        st.markdown('<div class="section-title">🚶 Échelle de dyspnée MRC</div>',
                    unsafe_allow_html=True)
        mrc_opts_display = ["— Non renseigné —"] + [g[1] for g in MRC_GRADES]
        mrc_scores_map   = {g[1]: g[0] for g in MRC_GRADES}
        mrc_stored       = load_val("mrc_score")
        mrc_stored_label = next(
            (g[1] for g in MRC_GRADES if str(g[0]) == str(mrc_stored)), None
        ) if mrc_stored not in (None, "", "0") else None
        mrc_default_idx  = mrc_opts_display.index(mrc_stored_label) if mrc_stored_label else 0
        mrc_chosen = st.radio("Grade MRC", mrc_opts_display,
                              index=mrc_default_idx, key="mrc_radio")
        if mrc_chosen == "— Non renseigné —":
            collected["mrc_score"] = ""
        else:
            mrc_score_val = mrc_scores_map[mrc_chosen]
            mrc_colors = ["#388e3c", "#8bc34a", "#f57c00", "#e64a19", "#d32f2f"]
            st.markdown(
                f'<div class="score-box" style="background:{mrc_colors[mrc_score_val]};">'
                f'MRC Grade {mrc_score_val} / 4</div>',
                unsafe_allow_html=True,
            )
            collected["mrc_score"] = mrc_score_val

    # ═════════════════════════════════════════════════════════════════════════
    #  TAB 12 – COMORBIDITÉS
    # ═════════════════════════════════════════════════════════════════════════
    with tab_comorb:
        st.markdown('<div class="section-title">🏥 Comorbidités & traitements</div>',
                    unsafe_allow_html=True)
        existing_comorb = str(load_val("comorb_list") or "").split("|")
        existing_trait  = str(load_val("comorb_traitements") or "").split("|")

        all_selected = []
        treat_selected = []

        for category, items in COMORB_CATEGORIES.items():
            if category == "💊 Traitements en cours":
                with st.expander(category):
                    for item in items:
                        if st.checkbox(item, value=item in existing_trait,
                                       key=f"trait_{item}"):
                            treat_selected.append(item)
            else:
                with st.expander(category):
                    for item in items:
                        if st.checkbox(item, value=item in existing_comorb,
                                       key=f"comorb_{item}"):
                            all_selected.append(item)

        comorb_notes = st.text_area("Autres comorbidités / remarques",
                                    value=str(load_val("comorb_notes") or ""),
                                    height=80, key="comorb_notes")
        collected.update({
            "comorb_list":         "|".join(all_selected),
            "comorb_traitements":  "|".join(treat_selected),
            "comorb_notes":        comorb_notes,
        })

    # ═════════════════════════════════════════════════════════════════════════
    #  SAUVEGARDE
    # ═════════════════════════════════════════════════════════════════════════
    # ── MUSCULAIRE MI ─────────────────────────────────────────────────────────
    with tab_muscle:
        from utils.muscle_widget import render_muscle_tab
        muscle_data = render_muscle_tab(lv_fn=load_val, key_prefix="shv", show_leg_press=False)
        collected.update(muscle_data)


    if save_top or st.button("💾 Sauvegarder le bilan", type="primary", key="save_bottom"):
        final_data = {
            **st.session_state.bilan_data,
            **collected,
            "patient_id": st.session_state.patient_id,
        }
        if st.session_state.bilan_id:
            final_data["bilan_id"] = st.session_state.bilan_id

        with st.spinner("Enregistrement dans Google Sheets…"):
            new_id = save_bilan(final_data)

        st.session_state.bilan_id   = new_id
        final_data["bilan_id"]      = new_id
        st.session_state.bilan_data = final_data

        st.session_state["shv_unsaved"] = False
        st.session_state["shv_just_saved"] = True
        st.success(f"✅ Bilan sauvegardé avec succès ! (ID : {new_id})")
        st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 – ÉVOLUTION & EXPORT EXCEL
# ═══════════════════════════════════════════════════════════════════════════════

def safe_num(val):
    try:
        v = float(val)
        return v if v != 0 else None
    except (TypeError, ValueError):
        return None


def render_evolution():
    info      = st.session_state.patient_info
    all_df    = get_patient_bilans(st.session_state.patient_id)

    # Filtrer selon la sélection
    sel       = st.session_state.get("selected_bilan_ids", None)
    bilans_df = all_df[all_df["bilan_id"].isin(sel)] if sel else all_df
    if bilans_df.empty:
        bilans_df = all_df

    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} — Évolution</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    n_sel = len(bilans_df)
    n_tot = len(all_df)
    if n_sel < n_tot:
        st.info(f"ℹ️ Affichage de {n_sel}/{n_tot} bilans sélectionnés.")

    col_back, col_export, _ = st.columns([1, 1.5, 4])
    with col_back:
        if st.button("⬅️ Retour"):
            st.session_state.mode = "bilan"
            st.rerun()
    with col_export:
        if not bilans_df.empty:
            with st.spinner("Génération du PDF…"):
                pdf_bytes = generate_pdf(bilans_df, info)
            st.download_button(
                label=f"📄 Exporter en PDF ({n_sel} bilan{'s' if n_sel>1 else ''})",
                data=pdf_bytes,
                file_name=f"evolution_SHV_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf",
                type="primary",
            )

    st.markdown("---")

    if bilans_df.empty:
        st.info("Aucun bilan disponible pour ce patient.")
        return

    # Trier par date
    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan")
    labels = [f"{row['date_bilan'].strftime('%d/%m/%y')} – {row.get('type_bilan','')}"
              for _, row in bilans_df.iterrows()]

    # ── Onglets ──────────────────────────────────────────────────────────────
    tab_had, tab_bolt, tab_sf12, tab_hvt, tab_nij, \
    tab_etco2_ev, tab_pattern_ev, tab_gazo_ev, tab_musc, tab_mrc_ev, tab_comorb2 = st.tabs([
        "😟 HAD", "⏱️ BOLT", "📊 SF-12", "🌬️ Test HV",
        "📋 Nijmegen", "📈 Capnographie", "🔬 Pattern respi.",
        "🧪 Gazométrie", "💪 Force musculaire", "🚶 MRC Dyspnée", "🏥 Comorbidités", "💪 Testing MI",
    ])

    # ── HAD ──────────────────────────────────────────────────────────────────
    with tab_had:
        st.markdown('<div class="section-title">😟 Évolution HAD</div>', unsafe_allow_html=True)

        scores_a = [safe_num(r.get("had_score_anxiete"))   for _, r in bilans_df.iterrows()]
        scores_d = [safe_num(r.get("had_score_depression")) for _, r in bilans_df.iterrows()]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=labels, y=scores_a, mode="lines+markers+text",
            name="Anxiété", line=dict(color="#f57c00", width=3),
            marker=dict(size=10), text=[str(v) if v else "" for v in scores_a],
            textposition="top center",
        ))
        fig.add_trace(go.Scatter(
            x=labels, y=scores_d, mode="lines+markers+text",
            name="Dépression", line=dict(color="#7b1fa2", width=3),
            marker=dict(size=10), text=[str(v) if v else "" for v in scores_d],
            textposition="top center",
        ))
        fig.add_hrect(y0=0,  y1=7,  fillcolor="green",  opacity=0.07, line_width=0,
                      annotation_text="Normal", annotation_position="right")
        fig.add_hrect(y0=8,  y1=10, fillcolor="orange", opacity=0.07, line_width=0,
                      annotation_text="Douteux", annotation_position="right")
        fig.add_hrect(y0=11, y1=21, fillcolor="red",    opacity=0.07, line_width=0,
                      annotation_text="Pathologique", annotation_position="right")
        fig.update_layout(
            yaxis=dict(range=[0, 22], title="Score /21"),
            xaxis_tickangle=-20, height=400,
            plot_bgcolor="white", legend=dict(orientation="h"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tableau récap
        df_had = pd.DataFrame({
            "Bilan":       labels,
            "Anxiété /21": scores_a,
            "Dépression /21": scores_d,
        })
        st.dataframe(df_had, use_container_width=True, hide_index=True)

    # ── BOLT ─────────────────────────────────────────────────────────────────
    with tab_bolt:
        st.markdown('<div class="section-title">⏱️ Évolution BOLT</div>', unsafe_allow_html=True)

        bolt_vals = [safe_num(r.get("bolt_score")) for _, r in bilans_df.iterrows()]
        colors    = []
        for v in bolt_vals:
            if v is None:      colors.append("#cccccc")
            elif v < 10:       colors.append("#d32f2f")
            elif v < 20:       colors.append("#f57c00")
            elif v < 40:       colors.append("#fbc02d")
            else:              colors.append("#388e3c")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=labels, y=bolt_vals,
            marker_color=colors,
            text=[f"{v}s" if v else "—" for v in bolt_vals],
            textposition="outside",
        ))
        fig.add_hline(y=20, line_dash="dot", line_color="#f57c00",
                      annotation_text="Seuil 20s", annotation_position="right")
        fig.add_hline(y=40, line_dash="dot", line_color="#388e3c",
                      annotation_text="Seuil 40s", annotation_position="right")
        fig.update_layout(
            yaxis=dict(range=[0, max([v or 0 for v in bolt_vals] + [50]) + 10],
                       title="Secondes"),
            xaxis_tickangle=-20, height=380,
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

        df_bolt = pd.DataFrame({"Bilan": labels, "BOLT (s)": bolt_vals})
        st.dataframe(df_bolt, use_container_width=True, hide_index=True)

    # ── SF-12 ─────────────────────────────────────────────────────────────────
    with tab_sf12:
        st.markdown('<div class="section-title">📊 Évolution SF-12</div>', unsafe_allow_html=True)

        dim_keys   = ["pf", "rp", "bp", "gh", "vt", "sf", "re", "mh"]
        dim_labels = ["Fonct. physique", "Limit. physique", "Douleur",
                      "Santé générale", "Vitalité", "Vie sociale",
                      "Limit. émotionnel", "Santé psychique"]

        # ── Scores composites PCS/MCS ─────────────────────────────────────────
        st.markdown("#### 🏅 Scores composites PCS-12 / MCS-12")
        pcs_vals = [safe_num(r.get("sf12_pcs")) for _, r in bilans_df.iterrows()]
        mcs_vals = [safe_num(r.get("sf12_mcs")) for _, r in bilans_df.iterrows()]

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatter(
            x=labels, y=pcs_vals, mode="lines+markers+text",
            name="PCS-12 (physique)", line=dict(color="#1a3c5e", width=3),
            marker=dict(size=10),
            text=[str(v) if v else "" for v in pcs_vals],
            textposition="top center",
        ))
        fig_comp.add_trace(go.Scatter(
            x=labels, y=mcs_vals, mode="lines+markers+text",
            name="MCS-12 (mental)", line=dict(color="#f57c00", width=3),
            marker=dict(size=10),
            text=[str(v) if v else "" for v in mcs_vals],
            textposition="bottom center",
        ))
        fig_comp.add_hline(y=50, line_dash="dot", line_color="grey",
                           annotation_text="50 (référence)", annotation_position="right")
        fig_comp.update_layout(
            yaxis=dict(range=[20, 70], title="Score (réf. 50)"),
            xaxis_tickangle=-20, height=380,
            plot_bgcolor="white", legend=dict(orientation="h"),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        # ── 8 dimensions ──────────────────────────────────────────────────────
        st.markdown("#### 📊 Évolution par dimension")
        fig = make_subplots(rows=2, cols=4, subplot_titles=dim_labels, shared_yaxes=True)
        colors_bilans = ["#1a3c5e", "#2196f3", "#00bcd4", "#26c6da",
                         "#80deea", "#b2ebf2", "#e0f7fa", "#f5f5f5"]
        for i, (dk, dl) in enumerate(zip(dim_keys, dim_labels)):
            row_i, col_i = divmod(i, 4)
            vals = [safe_num(r.get(f"sf12_{dk}")) for _, r in bilans_df.iterrows()]
            fig.add_trace(
                go.Bar(x=labels, y=vals,
                       marker_color=[colors_bilans[j % len(colors_bilans)]
                                     for j in range(len(vals))],
                       text=[str(v) if v else "—" for v in vals],
                       textposition="outside", showlegend=False),
                row=row_i + 1, col=col_i + 1,
            )
        fig.update_yaxes(range=[0, 115])
        fig.update_layout(height=550, plot_bgcolor="white", margin=dict(t=40, b=60))
        st.plotly_chart(fig, use_container_width=True)

        # ── Radar comparatif ──────────────────────────────────────────────────
        if len(bilans_df) >= 2:
            st.markdown("#### 🕸️ Comparaison radar")
            fig_radar = go.Figure()
            palette = ["#1a3c5e", "#f57c00", "#388e3c", "#7b1fa2", "#d32f2f"]
            for j, (_, row) in enumerate(bilans_df.iterrows()):
                vals_r = [safe_num(row.get(f"sf12_{dk}")) or 0 for dk in dim_keys]
                vals_r += [vals_r[0]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals_r, theta=dim_labels + [dim_labels[0]],
                    fill="toself", opacity=0.4, name=labels[j],
                    line=dict(color=palette[j % len(palette)]),
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                height=450, showlegend=True,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # ── Tableau récap ─────────────────────────────────────────────────────
        df_sf = pd.DataFrame(
            {**{"Bilan": labels},
             **{"PCS-12": pcs_vals, "MCS-12": mcs_vals},
             **{dl: [safe_num(r.get(f"sf12_{dk}")) for _, r in bilans_df.iterrows()]
                for dk, dl in zip(dim_keys, dim_labels)}}
        )
        st.dataframe(df_sf, use_container_width=True, hide_index=True)

    # ── HVT ──────────────────────────────────────────────────────────────────
    with tab_hvt:
        st.markdown('<div class="section-title">🌬️ Évolution Test HV</div>', unsafe_allow_html=True)

        rows_hvt = []
        for lbl, (_, row) in zip(labels, bilans_df.iterrows()):
            rows_hvt.append({
                "Bilan":                lbl,
                "Symptômes reproduits": row.get("hvt_symptomes_reproduits", "—"),
                "Retour normal (min)":  row.get("hvt_duree_retour", "—"),
                "Symptômes listés":     row.get("hvt_symptomes_list", "—"),
                "Notes":                row.get("hvt_notes", "—"),
            })
        df_hvt = pd.DataFrame(rows_hvt)
        st.dataframe(df_hvt, use_container_width=True, hide_index=True)

        # Durée de retour dans le temps
        durees = [safe_num(r.get("hvt_duree_retour")) for _, r in bilans_df.iterrows()]
        if any(d for d in durees):
            fig_hvt = go.Figure()
            fig_hvt.add_trace(go.Bar(
                x=labels, y=durees,
                marker_color="#1a3c5e",
                text=[f"{v} min" if v else "—" for v in durees],
                textposition="outside",
            ))
            fig_hvt.update_layout(
                title="Durée de retour à la normale (minutes)",
                yaxis_title="Minutes",
                xaxis_tickangle=-20,
                height=340,
                plot_bgcolor="white",
            )
            st.plotly_chart(fig_hvt, use_container_width=True)

    # ── NIJMEGEN ─────────────────────────────────────────────────────────────
    with tab_nij:
        st.markdown('<div class="section-title">📋 Évolution Nijmegen</div>', unsafe_allow_html=True)
        nij_vals = [safe_num(r.get("nij_score")) for _, r in bilans_df.iterrows()]

        fig_nij = go.Figure()
        fig_nij.add_trace(go.Scatter(
            x=labels, y=nij_vals, mode="lines+markers+text",
            name="Score Nijmegen", line=dict(color="#1a3c5e", width=3),
            marker=dict(size=10),
            text=[str(int(v)) if v else "" for v in nij_vals],
            textposition="top center",
        ))
        fig_nij.add_hrect(y0=0,  y1=14, fillcolor="green",  opacity=0.07, line_width=0,
                          annotation_text="Négatif", annotation_position="right")
        fig_nij.add_hrect(y0=15, y1=22, fillcolor="orange", opacity=0.07, line_width=0,
                          annotation_text="Borderline", annotation_position="right")
        fig_nij.add_hrect(y0=23, y1=64, fillcolor="red",    opacity=0.07, line_width=0,
                          annotation_text="Positif SHV", annotation_position="right")
        fig_nij.add_hline(y=23, line_dash="dot", line_color="#d32f2f",
                          annotation_text="Seuil 23", annotation_position="right")
        fig_nij.update_layout(
            yaxis=dict(range=[0, 66], title="Score /64"),
            xaxis_tickangle=-20, height=380, plot_bgcolor="white",
        )
        st.plotly_chart(fig_nij, use_container_width=True)
        df_nij = pd.DataFrame({"Bilan": labels, "Score Nijmegen /64": nij_vals,
                               "Interprétation": [r.get("nij_interpretation","—")
                                                  for _, r in bilans_df.iterrows()]})
        st.dataframe(df_nij, use_container_width=True, hide_index=True)

    # ── RESPIRATOIRE (Gazométrie + Capnographie + Pattern + MRC) ─────────────
    # ── CAPNOGRAPHIE ──────────────────────────────────────────────────────────
    with tab_etco2_ev:
        st.markdown('<div class="section-title">📈 Évolution Capnographie — ETCO₂</div>',
                    unsafe_allow_html=True)
        etco2_vals = [safe_num(r.get("etco2_repos")) for _, r in bilans_df.iterrows()]
        if any(etco2_vals):
            fig_etco2 = go.Figure()
            fig_etco2.add_trace(go.Bar(
                x=labels, y=etco2_vals,
                marker_color=["#388e3c" if v and 35<=v<=45 else "#f57c00" if v and v>=30
                              else "#d32f2f" if v else "#ccc" for v in etco2_vals],
                text=[f"{v} mmHg" if v else "—" for v in etco2_vals],
                textposition="outside",
            ))
            fig_etco2.add_hline(y=35, line_dash="dot", line_color="#f57c00",
                                annotation_text="35 mmHg", annotation_position="right")
            fig_etco2.add_hline(y=45, line_dash="dot", line_color="#388e3c",
                                annotation_text="45 mmHg", annotation_position="right")
            fig_etco2.update_layout(yaxis=dict(range=[0, 60], title="mmHg"),
                                    height=320, plot_bgcolor="white", xaxis_tickangle=-20)
            st.plotly_chart(fig_etco2, use_container_width=True)
        else:
            st.info("Aucune valeur ETCO₂ enregistrée.")
        etco2_table = [{"Bilan": lbl,
                        "ETCO₂ repos (mmHg)": r.get("etco2_repos","—") or "—",
                        "ETCO₂ post-effort":  r.get("etco2_post_effort","—") or "—",
                        "Pattern":            r.get("etco2_pattern","—") or "—"}
                       for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(etco2_table), use_container_width=True, hide_index=True)

    # ── PATTERN RESPIRATOIRE ──────────────────────────────────────────────────
    with tab_pattern_ev:
        st.markdown('<div class="section-title">🔬 Évolution Pattern respiratoire</div>',
                    unsafe_allow_html=True)
        pat_fr_vals = [safe_num(r.get("pattern_frequence")) for _, r in bilans_df.iterrows()]
        if any(pat_fr_vals):
            fig_fr = go.Figure()
            fig_fr.add_trace(go.Scatter(
                x=labels, y=pat_fr_vals, mode="lines+markers+text",
                line=dict(color="#1a3c5e", width=2.5), marker=dict(size=9),
                text=[str(int(v)) if v else "" for v in pat_fr_vals],
                textposition="top center",
            ))
            fig_fr.add_hline(y=12, line_dash="dot", line_color="#388e3c",
                             annotation_text="12 min normal", annotation_position="right")
            fig_fr.add_hline(y=18, line_dash="dot", line_color="#f57c00",
                             annotation_text="18 max normal", annotation_position="right")
            fig_fr.add_hline(y=20, line_dash="dot", line_color="#d32f2f",
                             annotation_text="20 tachypnée", annotation_position="right")
            fig_fr.update_layout(yaxis=dict(range=[0, 35], title="Cycles/min"),
                                 title="Fréquence respiratoire",
                                 height=320, plot_bgcolor="white", xaxis_tickangle=-20)
            st.plotly_chart(fig_fr, use_container_width=True)
        else:
            st.info("Aucune fréquence respiratoire enregistrée.")
        pattern_table = [{"Bilan": lbl,
                          "FR (cyc/min)": r.get("pattern_frequence","—") or "—",
                          "Mode":         r.get("pattern_mode","—") or "—",
                          "Amplitude":    r.get("pattern_amplitude","—") or "—",
                          "Rythme":       r.get("pattern_rythme","—") or "—",
                          "Paradoxal":    r.get("pattern_paradoxal","—") or "—",
                          "Notes":        r.get("pattern_notes","") or ""}
                         for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(pattern_table), use_container_width=True, hide_index=True)

    # ── GAZOMÉTRIE ────────────────────────────────────────────────────────────
    with tab_gazo_ev:
        st.markdown('<div class="section-title">🧪 Évolution Gazométrie</div>',
                    unsafe_allow_html=True)
        paco2_vals = [safe_num(r.get("gazo_paco2")) for _, r in bilans_df.iterrows()]
        if any(paco2_vals):
            fig_paco2 = go.Figure()
            fig_paco2.add_trace(go.Scatter(
                x=labels, y=paco2_vals, mode="lines+markers+text",
                line=dict(color="#7b1fa2", width=2.5), marker=dict(size=9),
                text=[str(v) if v else "" for v in paco2_vals],
                textposition="top center",
            ))
            fig_paco2.add_hline(y=35, line_dash="dot", line_color="#f57c00",
                                annotation_text="35 hypocapnie", annotation_position="right")
            fig_paco2.add_hline(y=45, line_dash="dot", line_color="#388e3c",
                                annotation_text="45 normal max", annotation_position="right")
            fig_paco2.update_layout(yaxis=dict(range=[20, 60], title="mmHg"),
                                    title="PaCO₂", height=320,
                                    plot_bgcolor="white", xaxis_tickangle=-20)
            st.plotly_chart(fig_paco2, use_container_width=True)
        else:
            st.info("Aucune valeur de gazométrie enregistrée.")
        gazo_table = [{"Bilan": lbl,
                       "Type":            r.get("gazo_type","—") or "—",
                       "pH":              r.get("gazo_ph","—") or "—",
                       "PaCO₂ (mmHg)":   r.get("gazo_paco2","—") or "—",
                       "PaO₂ (mmHg)":    r.get("gazo_pao2","—") or "—",
                       "HCO₃⁻ (mmol/L)": r.get("gazo_hco3","—") or "—",
                       "SatO₂ (%)":      r.get("gazo_sato2","—") or "—"}
                      for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(gazo_table), use_container_width=True, hide_index=True)

    # ── MRC DYSPNÉE ───────────────────────────────────────────────────────────
    with tab_mrc_ev:
        st.markdown('<div class="section-title">🚶 Évolution MRC Dyspnée</div>',
                    unsafe_allow_html=True)
        mrc_vals = [safe_num(r.get("mrc_score")) for _, r in bilans_df.iterrows()]
        if any(v is not None for v in mrc_vals):
            fig_mrc = go.Figure()
            fig_mrc.add_trace(go.Bar(
                x=labels, y=mrc_vals,
                marker_color=[
                    ["#388e3c","#8bc34a","#f57c00","#e64a19","#d32f2f"][int(v or 0)]
                    for v in mrc_vals
                ],
                text=[f"Grade {int(v)}" if v is not None else "—" for v in mrc_vals],
                textposition="outside",
            ))
            fig_mrc.update_layout(yaxis=dict(range=[0, 5], title="Grade MRC"),
                                  height=320, plot_bgcolor="white", xaxis_tickangle=-20)
            st.plotly_chart(fig_mrc, use_container_width=True)
        else:
            st.info("Aucune valeur MRC enregistrée.")
        mrc_table = [{"Bilan": lbl, "Grade MRC": r.get("mrc_score","—") or "—"}
                     for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(mrc_table), use_container_width=True, hide_index=True)

    # ── FORCE MUSCULAIRE ──────────────────────────────────────────────────────
    with tab_musc:
        st.markdown('<div class="section-title">💪 Évolution — Force musculaire respiratoire</div>',
                    unsafe_allow_html=True)
        musc_keys  = [("snif_pct","SNIF % prédit"), ("pimax_pct","PImax % prédit"),
                      ("pemax_pct","PEmax % prédit")]
        fig_musc = go.Figure()
        colors_musc = ["#1a3c5e", "#f57c00", "#388e3c"]
        for (mkey, mlabel), color in zip(musc_keys, colors_musc):
            vals = [safe_num(r.get(mkey)) for _, r in bilans_df.iterrows()]
            fig_musc.add_trace(go.Scatter(
                x=labels, y=vals, mode="lines+markers+text",
                name=mlabel, line=dict(color=color, width=2.5),
                marker=dict(size=9),
                text=[f"{int(v)}%" if v else "" for v in vals],
                textposition="top center",
            ))
        fig_musc.add_hline(y=80, line_dash="dot", line_color="grey",
                           annotation_text="80% (normal)", annotation_position="right")
        fig_musc.update_layout(
            yaxis=dict(range=[0, 130], title="% valeur prédite"),
            xaxis_tickangle=-20, height=400, plot_bgcolor="white",
            legend=dict(orientation="h"),
        )
        st.plotly_chart(fig_musc, use_container_width=True)
        musc_table = [{"Bilan": lbl,
                       "SNIF mesuré": r.get("snif_val","—"), "SNIF % prédit": r.get("snif_pct","—"),
                       "PImax mesuré": r.get("pimax_val","—"), "PImax % prédit": r.get("pimax_pct","—"),
                       "PEmax mesuré": r.get("pemax_val","—"), "PEmax % prédit": r.get("pemax_pct","—")}
                      for lbl, (_, r) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(musc_table), use_container_width=True, hide_index=True)

    # ── COMORBIDITÉS ──────────────────────────────────────────────────────────
    with tab_comorb2:
        st.markdown('<div class="section-title">🏥 Comorbidités & traitements</div>',
                    unsafe_allow_html=True)
        comorb_table = []
        for lbl, (_, row) in zip(labels, bilans_df.iterrows()):
            comorb_table.append({
                "Bilan":         lbl,
                "Comorbidités":  str(row.get("comorb_list","—") or "—").replace("|"," · "),
                "Traitements":   str(row.get("comorb_traitements","—") or "—").replace("|"," · "),
                "Notes":         str(row.get("comorb_notes","") or ""),
            })
        st.dataframe(pd.DataFrame(comorb_table), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTEUR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

mode = st.session_state.mode

if mode == "accueil":
    render_accueil()
elif mode == "bilan":
    if st.session_state.patient_info is None:
        st.session_state.mode = "accueil"
        st.rerun()
    render_bilan_selection()
elif mode == "formulaire":
    if st.session_state.patient_info is None:
        st.session_state.mode = "accueil"
        st.rerun()
    render_formulaire()
elif mode == "evolution":
    if st.session_state.patient_info is None:
        st.session_state.mode = "accueil"
        st.rerun()
    render_evolution()
else:
    st.session_state.mode = "accueil"
    st.rerun()
