"""
Page : Bilan Lombalgie
Module de bilan pour les patients lombalgiques.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.google_sheets import (
    get_all_patients, create_patient,
    get_patient_bilans_lombalgie, save_bilan_lombalgie,
)
from utils.questionnaires_lombalgie import generate_questionnaires_lombalgie_pdf

# ─── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bilan Lombalgie",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .page-title  { font-size:2rem; font-weight:700; color:#2e5a1c; }
    .section-title { font-size:1.15rem; font-weight:600; color:#2e5a1c;
                     border-bottom:2px solid #e0f0d0; padding-bottom:4px; margin-bottom:1rem; }
    .score-box   { border-radius:10px; padding:1rem; text-align:center; color:white;
                   font-size:1.4rem; font-weight:700; }
    .info-box    { background:#f0f8e8; border-left:4px solid #2e5a1c;
                   padding:0.8rem 1rem; border-radius:0 8px 8px 0; margin-bottom:1rem; }
    .patient-badge { background:#2e5a1c; color:white; border-radius:8px;
                     padding:0.4rem 1rem; display:inline-block; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ─── Session state ────────────────────────────────────────────────────────────
def init_state():
    for k, v in {
        "lomb_patient_id":   None,
        "lomb_patient_info": None,
        "lomb_bilan_id":     None,
        "lomb_bilan_data":   {},
        "lomb_mode":         "accueil",
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 0 – ACCUEIL / SÉLECTION PATIENT
# ═══════════════════════════════════════════════════════════════════════════════

def render_accueil():
    st.markdown('<div class="page-title">🦴 Bilan Lombalgie</div>', unsafe_allow_html=True)
    st.markdown("##### Bilan physiothérapeutique — Lombalgie")

    # Bouton impression questionnaires vierges
    col_title, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🖨️ Imprimer questionnaires", key="print_lomb_accueil"):
            st.session_state["show_print_lomb_accueil"] = True

    st.markdown("---")

    # Panneau impression vierge
    if st.session_state.get("show_print_lomb_accueil", False):
        with st.container():
            st.markdown("""
            <div style="background:#f0f8e8; border:2px solid #2e5a1c; border-radius:10px;
                        padding:1.2rem 1.5rem; margin-bottom:1rem;">
                <span style="font-size:1.1rem; font-weight:700; color:#2e5a1c;">
                🖨️ Imprimer des questionnaires vierges — Lombalgie
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Colonnes de sélection (à compléter au fur et à mesure)
            st.info("Les questionnaires spécifiques à la lombalgie seront ajoutés ici au fur et à mesure du développement.")

            if st.button("✖ Fermer", key="close_print_lomb_accueil"):
                st.session_state["show_print_lomb_accueil"] = False
                st.rerun()
        st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🔍 Rechercher un patient existant")
        patients_df = get_all_patients()

        if patients_df.empty:
            st.info("Aucun patient enregistré pour le moment.")
        else:
            search = st.text_input("Recherche (nom, prénom)…", key="lomb_search_input")
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
                            if st.button("Sélectionner", key=f"lomb_sel_{row['patient_id']}"):
                                st.session_state.lomb_patient_id   = row["patient_id"]
                                st.session_state.lomb_patient_info = row.to_dict()
                                st.session_state.lomb_mode         = "bilan"
                                st.rerun()

    with col_b:
        st.markdown("#### ➕ Créer un nouveau patient")
        with st.form("lomb_form_new_patient", clear_on_submit=True):
            nom        = st.text_input("Nom *")
            prenom     = st.text_input("Prénom *")
            ddn        = st.date_input("Date de naissance *",
                                       min_value=date(1900, 1, 1),
                                       max_value=date.today())
            sexe       = st.selectbox("Sexe", ["Féminin", "Masculin", "Autre"])
            profession = st.text_input("Profession")
            submitted  = st.form_submit_button("Créer le patient", type="primary")

        if submitted:
            if not nom or not prenom:
                st.error("Le nom et le prénom sont obligatoires.")
            else:
                with st.spinner("Enregistrement…"):
                    pid = create_patient(nom, prenom, ddn, sexe, profession)
                patients_df2 = get_all_patients()
                row = patients_df2[patients_df2["patient_id"] == pid].iloc[0]
                st.session_state.lomb_patient_id   = pid
                st.session_state.lomb_patient_info = row.to_dict()
                st.session_state.lomb_mode         = "bilan"
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 – SÉLECTION / CRÉATION DU BILAN
# ═══════════════════════════════════════════════════════════════════════════════

def render_bilan_selection():
    info = st.session_state.lomb_patient_info
    bilans_df = get_patient_bilans_lombalgie(st.session_state.lomb_patient_id)

    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— {info.get("date_naissance","—")} — ID : {info["patient_id"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    col_back, col_print, _ = st.columns([1, 1.5, 4])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            st.session_state.lomb_patient_id   = None
            st.session_state.lomb_patient_info = None
            st.session_state.lomb_bilan_id     = None
            st.session_state.lomb_bilan_data   = {}
            st.session_state.lomb_mode         = "accueil"
            st.rerun()
    with col_print:
        if st.button("🖨️ Imprimer questionnaires", key="print_lomb_patient"):
            st.session_state["show_print_lomb_patient"] = True

    # Panneau impression avec nom patient
    if st.session_state.get("show_print_lomb_patient", False):
        with st.container():
            st.markdown("""
            <div style="background:#f0f8e8; border:2px solid #2e5a1c; border-radius:10px;
                        padding:1.2rem 1.5rem; margin-bottom:1rem;">
                <span style="font-size:1.1rem; font-weight:700; color:#2e5a1c;">
                🖨️ Sélectionner les questionnaires à imprimer
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.info("Les questionnaires spécifiques à la lombalgie seront ajoutés ici.")

            if st.button("✖ Fermer", key="close_print_lomb_patient"):
                st.session_state["show_print_lomb_patient"] = False
                st.rerun()

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📋 Bilans existants")
        if bilans_df.empty:
            st.info("Aucun bilan pour ce patient.")
        else:
            for _, row in bilans_df.iterrows():
                c1, c2 = st.columns([3, 1])
                with c1:
                    btype = row.get("type_bilan", "—")
                    bdate = row.get("date_bilan", "—")
                    bid   = row.get("bilan_id", "—")
                    st.markdown(
                        f"**{bdate}** — {btype} &nbsp;|&nbsp; `{bid}`",
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("Ouvrir", key=f"lomb_open_{row['bilan_id']}"):
                        st.session_state.lomb_bilan_id   = row["bilan_id"]
                        st.session_state.lomb_bilan_data = row.to_dict()
                        st.session_state.lomb_mode       = "formulaire"
                        st.rerun()

    with col_right:
        st.markdown("#### ➕ Nouveau bilan Lombalgie")
        with st.form("lomb_form_new_bilan"):
            bilan_date = st.date_input("Date du bilan", value=date.today())
            bilan_type = st.selectbox(
                "Type de bilan",
                ["Bilan initial", "Bilan intermédiaire", "Bilan final"]
            )
            praticien  = st.text_input("Praticien")
            go_btn     = st.form_submit_button("Créer le bilan", type="primary")

        if go_btn:
            st.session_state.lomb_bilan_id   = None
            st.session_state.lomb_bilan_data = {
                "patient_id": st.session_state.lomb_patient_id,
                "date_bilan": str(bilan_date),
                "type_bilan": bilan_type,
                "praticien":  praticien,
            }
            st.session_state.lomb_mode = "formulaire"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 – FORMULAIRE BILAN (squelette, à compléter)
# ═══════════════════════════════════════════════════════════════════════════════

def render_formulaire():
    info = st.session_state.lomb_patient_info
    bd   = st.session_state.lomb_bilan_data

    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— Bilan : {bd.get("type_bilan","—")} du {bd.get("date_bilan","—")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    col_back, col_save, _ = st.columns([1, 1, 4])
    with col_back:
        if st.button("⬅️ Retour"):
            st.session_state.lomb_mode = "bilan"
            st.rerun()
    with col_save:
        save_top = st.button("💾 Sauvegarder", type="primary")

    st.markdown("---")

    st.info(
        "🚧 Le formulaire de bilan Lombalgie est en cours de développement. "
        "Les onglets et questionnaires spécifiques seront ajoutés prochainement."
    )

    # ── Informations générales ────────────────────────────────────────────────
    st.markdown('<div class="section-title">📝 Informations générales</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    collected = {}
    with c1:
        bilan_date = st.date_input(
            "Date du bilan",
            value=date.fromisoformat(bd.get("date_bilan", str(date.today()))),
            key="lomb_g_date",
        )
        bilan_type = st.selectbox(
            "Type de bilan",
            ["Bilan initial", "Bilan intermédiaire", "Bilan final"],
            index=["Bilan initial", "Bilan intermédiaire", "Bilan final"].index(
                bd.get("type_bilan", "Bilan initial")
            ),
            key="lomb_g_type",
        )
    with c2:
        praticien  = st.text_input("Praticien", value=bd.get("praticien", ""), key="lomb_g_prat")
        notes_gen  = st.text_area("Notes générales", value=bd.get("notes_generales", ""),
                                   height=120, key="lomb_g_notes")

    collected.update({
        "date_bilan":      str(bilan_date),
        "type_bilan":      bilan_type,
        "praticien":       praticien,
        "notes_generales": notes_gen,
        "patient_id":      st.session_state.lomb_patient_id,
    })

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    if save_top or st.button("💾 Sauvegarder le bilan", type="primary", key="lomb_save_bottom"):
        final_data = {**st.session_state.lomb_bilan_data, **collected}
        if st.session_state.lomb_bilan_id:
            final_data["bilan_id"] = st.session_state.lomb_bilan_id

        with st.spinner("Enregistrement dans Google Sheets…"):
            new_id = save_bilan_lombalgie(final_data)

        st.session_state.lomb_bilan_id   = new_id
        final_data["bilan_id"]           = new_id
        st.session_state.lomb_bilan_data = final_data

        st.success(f"✅ Bilan sauvegardé ! (ID : {new_id})")
        st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTEUR
# ═══════════════════════════════════════════════════════════════════════════════

mode = st.session_state.lomb_mode

if mode == "accueil":
    render_accueil()
elif mode == "bilan":
    if st.session_state.lomb_patient_info is None:
        st.session_state.lomb_mode = "accueil"
        st.rerun()
    render_bilan_selection()
elif mode == "formulaire":
    if st.session_state.lomb_patient_info is None:
        st.session_state.lomb_mode = "accueil"
        st.rerun()
    render_formulaire()
else:
    st.session_state.lomb_mode = "accueil"
    st.rerun()
