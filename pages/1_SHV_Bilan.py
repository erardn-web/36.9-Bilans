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

from utils.google_sheets import (
    get_all_patients, create_patient,
    get_patient_bilans, save_bilan,
)
from utils.had import HAD_QUESTIONS, compute_had_scores
from utils.sf12 import (
    SF12_QUESTIONS, SF12_KEYS, SF12_DIMENSIONS,
    compute_sf12_scores, interpret_pcs_mcs,
)
from utils.shv_tests import (
    BOLT_DESCRIPTION, interpret_bolt,
    HVT_DESCRIPTION, HVT_SYMPTOMES,
)
from utils.pdf_export import generate_pdf
from utils.questionnaires_print import generate_questionnaires_pdf, QUESTIONNAIRES

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
    """Selectbox retournant le score (int) de l'option choisie."""
    labels = [o[1] for o in options]
    scores = [o[0] for o in options]
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

            pcol1, pcol2, pcol3, pcol4 = st.columns(4)
            with pcol1:
                p_had  = st.checkbox("😟 HAD",       value=True, key="pa_had")
            with pcol2:
                p_sf12 = st.checkbox("📊 SF-12",     value=True, key="pa_sf12")
            with pcol3:
                p_hvt  = st.checkbox("🌬️ Test HV",   value=True, key="pa_hvt")
            with pcol4:
                p_bolt = st.checkbox("⏱️ BOLT",       value=True, key="pa_bolt")

            selected = []
            if p_had:  selected.append("had")
            if p_sf12: selected.append("sf12")
            if p_hvt:  selected.append("hvt")
            if p_bolt: selected.append("bolt")

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
            profession= st.text_input("Profession")
            submitted = st.form_submit_button("Créer le patient", type="primary")

        if submitted:
            if not nom or not prenom:
                st.error("Le nom et le prénom sont obligatoires.")
            else:
                with st.spinner("Enregistrement…"):
                    pid = create_patient(nom, prenom, ddn, sexe, profession)
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

    col_back, col_evol, col_pdf, col_print, _ = st.columns([1, 1, 1.2, 1.5, 1])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            st.session_state.patient_id   = None
            st.session_state.patient_info = None
            st.session_state.bilan_id     = None
            st.session_state.bilan_data   = {}
            st.session_state.mode         = "accueil"
            st.rerun()
    with col_evol:
        if not bilans_df.empty and len(bilans_df) >= 1:
            if st.button("📈 Voir l'évolution", type="primary"):
                st.session_state.mode = "evolution"
                st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            with st.spinner("Génération du PDF…"):
                pdf_bytes = generate_pdf(bilans_df, info)
            st.download_button(
                label="📄 Exporter PDF",
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

            pcol1, pcol2, pcol3, pcol4 = st.columns(4)
            with pcol1:
                print_had  = st.checkbox("😟 HAD", value=True, key="print_had")
            with pcol2:
                print_sf12 = st.checkbox("📊 SF-12", value=True, key="print_sf12")
            with pcol3:
                print_hvt  = st.checkbox("🌬️ Test HV", value=True, key="print_hvt")
            with pcol4:
                print_bolt = st.checkbox("⏱️ BOLT", value=True, key="print_bolt")

            selected = []
            if print_had:  selected.append("had")
            if print_sf12: selected.append("sf12")
            if print_hvt:  selected.append("hvt")
            if print_bolt: selected.append("bolt")

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
                    if st.button("Ouvrir", key=f"open_{row['bilan_id']}"):
                        st.session_state.bilan_id   = row["bilan_id"]
                        st.session_state.bilan_data = row.to_dict()
                        st.session_state.mode       = "formulaire"
                        st.rerun()

    with col_right:
        st.markdown("#### ➕ Nouveau bilan SHV")
        with st.form("form_new_bilan"):
            bilan_date = st.date_input("Date du bilan", value=date.today())
            bilan_type = st.selectbox(
                "Type de bilan",
                ["Bilan initial", "Bilan intermédiaire", "Bilan final"]
            )
            praticien  = st.text_input("Praticien")
            go_btn     = st.form_submit_button("Créer le bilan", type="primary")

        if go_btn:
            st.session_state.bilan_id   = None  # sera généré à la sauvegarde
            st.session_state.bilan_data = {
                "patient_id": st.session_state.patient_id,
                "date_bilan": str(bilan_date),
                "type_bilan": bilan_type,
                "praticien":  praticien,
            }
            st.session_state.mode = "formulaire"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 – FORMULAIRE BILAN
# ═══════════════════════════════════════════════════════════════════════════════

def load_val(key, default=None):
    """Récupère une valeur existante du bilan (si re-chargement)."""
    v = st.session_state.bilan_data.get(key)
    if v is None or v == "":
        return default
    try:
        return int(v)
    except (ValueError, TypeError):
        return v


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
            st.session_state.mode = "bilan"
            st.rerun()
    with col_save:
        save_top = st.button("💾 Sauvegarder", type="primary")

    st.markdown("---")

    # ──── Onglets ────────────────────────────────────────────────────────────
    tab_gen, tab_had, tab_sf12, tab_bolt, tab_hvt = st.tabs([
        "📝 Général", "😟 HAD", "📊 SF-12", "⏱️ BOLT", "🌬️ Test HV"
    ])

    collected = {}   # on accumulera toutes les valeurs ici

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
            collected[f"sf12_{k}"] = v
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
            value=int(load_val("bolt_score") or 0),
            step=1,
            key="bolt_input",
        )

        if bolt_val > 0:
            interp = interpret_bolt(bolt_val)
            st.markdown(
                f'<div class="score-box" style="background:{interp["color"]};">'
                f'{bolt_val} s — {interp["cat"]}<br>'
                f'<small style="font-size:.8rem">{interp["desc"]}</small></div>',
                unsafe_allow_html=True,
            )
            collected["bolt_score"]          = bolt_val
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

        # Symptômes reproduits
        existing_symptomes = str(load_val("hvt_symptomes_list", "") or "").split("|")
        symptomes_selectionnes = st.multiselect(
            "Symptômes reproduits pendant le test :",
            HVT_SYMPTOMES,
            default=[s for s in existing_symptomes if s in HVT_SYMPTOMES],
            key="hvt_symptomes",
        )

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
                value=int(load_val("hvt_duree_retour") or 0),
                step=1,
                key="hvt_duree",
            )

        hvt_notes = st.text_area(
            "Observations / notes cliniques",
            value=str(load_val("hvt_notes", "") or ""),
            height=120,
            key="hvt_notes_field",
        )

        if "Oui ✅" in hvt_reproduits:
            st.markdown(
                '<div class="success-box">✅ <strong>Test positif</strong> — '
                'Confirme le diagnostic de SHV.</div>',
                unsafe_allow_html=True,
            )
        elif "Partiellement" in hvt_reproduits:
            st.markdown(
                '<div class="warn-box">⚠️ <strong>Test partiellement positif</strong> — '
                'Arguments en faveur d\'un SHV.</div>',
                unsafe_allow_html=True,
            )

        collected.update({
            "hvt_symptomes_reproduits": hvt_reproduits,
            "hvt_symptomes_list":       "|".join(symptomes_selectionnes),
            "hvt_duree_retour":         hvt_duree if hvt_duree > 0 else "",
            "hvt_notes":                hvt_notes,
        })

    # ═════════════════════════════════════════════════════════════════════════
    #  SAUVEGARDE
    # ═════════════════════════════════════════════════════════════════════════
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
    info     = st.session_state.patient_info
    bilans_df = get_patient_bilans(st.session_state.patient_id)

    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} — Évolution</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

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
                label="📄 Exporter en PDF",
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
    tab_had, tab_bolt, tab_sf12, tab_hvt = st.tabs([
        "😟 HAD", "⏱️ BOLT", "📊 SF-12", "🌬️ Test HV"
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
