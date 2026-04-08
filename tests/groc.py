"""tests/questionnaires/groc.py — GROC (Global Rating of Change)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

GROC_OPTIONS = [
    (-7, "Extrêmement empiré"),
    (-6, "Beaucoup empiré"),
    (-5, "Assez empiré"),
    (-4, "Empiré"),
    (-3, "Un peu empiré"),
    (-2, "Légèrement empiré"),
    (-1, "Quasi identique, très légèrement empiré"),
    (0,  "Identique"),
    (1,  "Quasi identique, très légèrement amélioré"),
    (2,  "Légèrement amélioré"),
    (3,  "Un peu amélioré"),
    (4,  "Amélioré"),
    (5,  "Assez amélioré"),
    (6,  "Beaucoup amélioré"),
    (7,  "Extrêmement amélioré"),
]


@register_test
class GROC(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "groc", "nom": "GROC — Changement global perçu",
            "tab_label": "📈 GROC",
            "categorie": "questionnaire",
            "tags": ["changement", "perception", "universel", "évolution"],
            "description": "Global Rating of Change — évaluation subjective du changement -7 à +7",
        }

    @classmethod
    def fields(cls):
        return ["groc_score", "groc_appreciation", "groc_notes"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score", "label": "Score GROC (-7 à +7)", "default": True},
            {"key": "appreciation", "label": "Appréciation textuelle", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📈 GROC — Changement global perçu</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Depuis le début du traitement, comment évaluez-vous '
            'l\'évolution de votre état général ?</div>', unsafe_allow_html=True)

        raw = lv("groc_score", None)
        try:    stored = int(float(raw)) if raw not in (None, "", "None") else 0
        except: stored = 0

        opts_vals  = [o[0] for o in GROC_OPTIONS]
        opts_labels = [f"{o[0]:+d} — {o[1]}" for o in GROC_OPTIONS]
        default_idx = opts_vals.index(stored) if stored in opts_vals else 7  # 0 = index 7

        chosen_label = st.selectbox("Évaluation", opts_labels,
                                    index=default_idx, key=f"{key_prefix}_groc_score")
        chosen_val = opts_vals[opts_labels.index(chosen_label)]

        appr = lv("groc_appreciation", "")
        appreciation = st.text_input("Précision / commentaire patient",
                                     value=appr, key=f"{key_prefix}_groc_appr",
                                     placeholder="ex: je marche mieux mais la douleur persiste")
        notes = st.text_area("Notes cliniques", value=lv("groc_notes", ""),
                             height=70, key=f"{key_prefix}_groc_notes")

        if chosen_val > 0:
            color = "#388e3c" if chosen_val >= 3 else "#7cb87e"
            msg   = "Amélioration" if chosen_val >= 3 else "Légère amélioration"
        elif chosen_val < 0:
            color = "#d32f2f" if chosen_val <= -3 else "#f57c00"
            msg   = "Détérioration" if chosen_val <= -3 else "Légère détérioration"
        else:
            color = "#888888"; msg = "Stable"

        st.markdown(
            f'<div class="score-box" style="background:{color}">'
            f'GROC : {chosen_val:+d} — {msg}</div>',
            unsafe_allow_html=True)

        return {"groc_score": chosen_val, "groc_appreciation": appreciation, "groc_notes": notes}

    @classmethod
    def score(cls, data):
        try:    s = int(float(data.get("groc_score", "")))
        except: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        color = "#388e3c" if s >= 3 else "#7cb87e" if s > 0 else "#d32f2f" if s <= -3 else "#f57c00" if s < 0 else "#888"
        return {"score": s, "interpretation": f"{s:+d}/7", "color": color, "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        v = bilan_data.get("groc_score", "")
        return str(v).strip() not in ("", "None", "nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        vals = []
        for _, row in bilans_df.iterrows():
            try:    vals.append(int(float(row.get("groc_score", ""))))
            except: vals.append(None)
        xp = [labels[i] for i, v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                name="GROC", line=dict(color="#1D9E75", width=2.5),
                marker=dict(size=9),
                text=[f"{v:+d}" for v in yp], textposition="top center"))
        fig.add_hline(y=0, line_dash="dash", line_color="#888",
                      annotation_text="Stable", annotation_position="right")
        fig.add_hline(y=3, line_dash="dot", line_color="#388e3c",
                      annotation_text="Amélioration clinique", annotation_position="right")
        fig.add_hline(y=-3, line_dash="dot", line_color="#d32f2f",
                      annotation_text="Détérioration clinique", annotation_position="right")
        fig.update_layout(yaxis=dict(range=[-8, 8], title="Score GROC"),
                          height=300, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('groc', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "GROC", "col_key": "groc_score",
             "values": [r.get("groc_score","—") for _,r in bilans_df.iterrows()]},
            {"label": "Commentaire", "col_key": "groc_appreciation",
             "values": [r.get("groc_appreciation","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan": lbl, "GROC": row.get("groc_score", "—"),
                             "Commentaire": row.get("groc_appreciation", "—")}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
