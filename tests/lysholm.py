"""tests/questionnaires/lysholm.py — Score de Lysholm (genou)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

LYSHOLM_ITEMS = [
    ("lysholm_boiterie", "Boiterie", [
        (5, "Aucune"), (3, "Légère ou périodique"), (0, "Sévère et constante")]),
    ("lysholm_soutien", "Utilisation de soutien", [
        (5, "Aucun"), (2, "Canne ou béquilles nécessaires"), (0, "Impossible de mise en charge")]),
    ("lysholm_blocage", "Blocage", [
        (15, "Aucun blocage"), (10, "Accrochages mais pas de blocage"),
        (6, "Blocages occasionnels"), (2, "Blocages fréquents"), (0, "Genou bloqué")]),
    ("lysholm_instabilite", "Instabilité (dérobement)", [
        (25, "Jamais"), (20, "Rarement lors d'activités sportives ou efforts importants"),
        (15, "Fréquemment lors d'activités sportives"),
        (10, "Occasionnellement lors d'activités quotidiennes"),
        (5, "Souvent lors d'activités quotidiennes"), (0, "À chaque pas")]),
    ("lysholm_douleur", "Douleur", [
        (25, "Aucune"), (20, "Légère et occasionnelle"),
        (15, "Marquée lors d'efforts importants"),
        (10, "Marquée à 2 km de marche"), (5, "Marquée à moins de 2 km"),
        (0, "Constante")]),
    ("lysholm_gonflement", "Gonflement", [
        (10, "Aucun"), (6, "Lors d'efforts importants"),
        (2, "Lors d'efforts ordinaires"), (0, "Constant")]),
    ("lysholm_escaliers", "Montée des escaliers", [
        (10, "Aucune difficulté"), (6, "Légère difficulté"), (2, "Un à un"),
        (0, "Impossible")]),
    ("lysholm_accroupi", "Accroupissement", [
        (5, "Aucune difficulté"), (4, "Légère difficulté"),
        (2, "Pas au-delà de 90°"), (0, "Impossible")]),
]


def _lysholm_interp(score):
    if score >= 95: return "Excellent"
    if score >= 84: return "Bon"
    if score >= 65: return "Passable"
    return "Mauvais"


def _lysholm_color(score):
    if score >= 95: return "#388e3c"
    if score >= 84: return "#7cb87e"
    if score >= 65: return "#f57c00"
    return "#d32f2f"


@register_test
class Lysholm(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "lysholm", "nom": "Lysholm — Genou",
            "tab_label": "🦵 Lysholm",
            "categorie": "questionnaire",
            "tags": ["genou", "ligament", "LCA", "fonctionnel", "chirurgie"],
            "description": "Score de Lysholm — 8 items, /100. Excellent ≥95, Bon ≥84, Passable ≥65",
        }

    @classmethod
    def fields(cls):
        return [i[0] for i in LYSHOLM_ITEMS] + ["lysholm_score_total"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score Lysholm (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦵 Score de Lysholm</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Score fonctionnel du genou sur 100 points. '
            'Excellent ≥ 95 · Bon ≥ 84 · Passable ≥ 65 · Mauvais &lt; 65</div>',
            unsafe_allow_html=True)

        collected = {}
        total = 0
        for field, label, opts in LYSHOLM_ITEMS:
            raw = lv(field, None)
            try:    stored = int(float(raw)) if raw not in (None, "", "None") else None
            except: stored = None
            vals = [o[0] for o in opts]
            opts_ext = [None] + vals
            def _fmt(x, o=opts):
                return "— Non renseigné —" if x is None else next(l for s, l in o if s == x)
            default_idx = (vals.index(stored) + 1) if stored in vals else 0
            chosen = st.radio(f"**{label}**", opts_ext, format_func=_fmt,
                              index=default_idx, key=f"{key_prefix}_{field}", horizontal=True)
            collected[field] = chosen if chosen is not None else ""
            if chosen is not None:
                total += chosen

        collected["lysholm_score_total"] = total
        color = _lysholm_color(total)
        st.markdown(
            f'<div class="score-box" style="background:{color}">'
            f'Lysholm : {total}/100 — {_lysholm_interp(total)}</div>',
            unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls, data):
        try:    s = int(float(data.get("lysholm_score_total", "")))
        except: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        return {"score": s, "interpretation": f"{s}/100 — {_lysholm_interp(s)}",
                "color": _lysholm_color(s), "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        try:    return float(bilan_data.get("lysholm_score_total", "")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        vals = []
        for _, row in bilans_df.iterrows():
            try:    vals.append(float(row.get("lysholm_score_total", "")))
            except: vals.append(None)
        xp = [labels[i] for i, v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                name="Lysholm", line=dict(color="#2B57A7", width=2.5),
                marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp], textposition="top center"))
        for y, color, label in [(95, "#388e3c", "Excellent ≥95"),
                                 (84, "#7cb87e", "Bon ≥84"),
                                 (65, "#f57c00", "Passable ≥65")]:
            fig.add_hline(y=y, line_dash="dot", line_color=color,
                          annotation_text=label, annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0, 105], title="Score /100"),
                          height=320, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('lysholm', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "Lysholm", "col_key": "lysholm_score_total",
             "values": [r.get("lysholm_score_total","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan": lbl, "Lysholm": row.get("lysholm_score_total", "—"),
                             "Interprétation": _lysholm_interp(float(row.get("lysholm_score_total", 0) or 0))}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
