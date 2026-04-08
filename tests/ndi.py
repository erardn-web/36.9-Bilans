"""tests/questionnaires/ndi.py — NDI (Neck Disability Index)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

NDI_ITEMS = [
    ("ndi_s1",  "Intensité de la douleur",
     ["0 — Aucune douleur", "1 — Douleur très légère", "2 — Douleur modérée",
      "3 — Douleur assez sévère", "4 — Douleur très sévère", "5 — Douleur maximale"]),
    ("ndi_s2",  "Soins personnels (se laver, s'habiller)",
     ["0 — Autonome, sans douleur", "1 — Autonome, avec douleur",
      "2 — Lent et prudent", "3 — Aide partielle", "4 — Aide importante", "5 — Incapable"]),
    ("ndi_s3",  "Soulever des charges",
     ["0 — Charges lourdes sans douleur", "1 — Charges lourdes avec douleur",
      "2 — Charges légères à moyennes", "3 — Charges très légères seulement",
      "4 — Incapable de soulever", "5 — Incapable de rien porter"]),
    ("ndi_s4",  "Lecture",
     ["0 — Autant que souhaité", "1 — Autant, avec légère douleur",
      "2 — Autant, avec douleur modérée", "3 — Moins à cause de la douleur",
      "4 — Très peu", "5 — Incapable"]),
    ("ndi_s5",  "Maux de tête",
     ["0 — Aucun", "1 — Légers, occasionnels", "2 — Modérés, occasionnels",
      "3 — Modérés, fréquents", "4 — Sévères, fréquents", "5 — Permanents"]),
    ("ndi_s6",  "Concentration",
     ["0 — Complète, sans difficulté", "1 — Complète, légère difficulté",
      "2 — Difficulté modérée", "3 — Grande difficulté", "4 — Très grande difficulté",
      "5 — Incapable"]),
    ("ndi_s7",  "Travail",
     ["0 — Travail habituel", "1 — Travail habituel avec douleur",
      "2 — La plupart du travail", "3 — Travail réduit", "4 — Presque aucun travail",
      "5 — Incapable de travailler"]),
    ("ndi_s8",  "Conduite automobile",
     ["0 — Sans douleur", "1 — Légère douleur", "2 — Douleur modérée",
      "3 — Douleur sévère", "4 — Presque incapable", "5 — Incapable"]),
    ("ndi_s9",  "Sommeil",
     ["0 — Non perturbé", "1 — Légèrement perturbé (<1h)",
      "2 — Modérément perturbé (1–2h)", "3 — Perturbé (2–3h)",
      "4 — Très perturbé (3–5h)", "5 — Complètement perturbé (5–7h)"]),
    ("ndi_s10", "Loisirs",
     ["0 — Activités habituelles", "1 — Activités habituelles avec douleur",
      "2 — La plupart des activités", "3 — Peu d'activités", "4 — Presque aucune",
      "5 — Aucune"]),
]


def _ndi_interp(pct):
    if pct <= 8:   return "Pas d'incapacité"
    if pct <= 28:  return "Incapacité légère"
    if pct <= 48:  return "Incapacité modérée"
    if pct <= 64:  return "Incapacité sévère"
    return "Incapacité complète"


def _ndi_color(pct):
    if pct <= 8:  return "#388e3c"
    if pct <= 28: return "#7cb87e"
    if pct <= 48: return "#f57c00"
    if pct <= 64: return "#e65100"
    return "#d32f2f"


@register_test
class NDI(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "ndi", "nom": "NDI — Index d'incapacité cervicale",
            "tab_label": "🦴 NDI",
            "categorie": "questionnaire",
            "tags": ["cervical", "incapacité", "cou", "douleur cervicale"],
            "description": "Neck Disability Index — 10 items, score /50, interprétation en %",
        }

    @classmethod
    def fields(cls):
        return [i[0] for i in NDI_ITEMS] + ["ndi_score_total", "ndi_score_pct"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score NDI (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦴 NDI — Index d\'incapacité cervicale</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Pour chaque section, cochez l\'énoncé qui décrit '
            'le mieux votre état aujourd\'hui. Score 0–8 % : aucune · 9–28 % : légère · '
            '29–48 % : modérée · 49–64 % : sévère · &gt;65 % : complète.</div>',
            unsafe_allow_html=True)

        collected = {}
        total = 0
        answered = 0
        for field, label, opts in NDI_ITEMS:
            raw = lv(field, None)
            try:    stored = int(float(raw)) if raw not in (None, "", "None") else None
            except: stored = None
            opts_ext = [None] + list(range(6))
            def _fmt(x, o=opts):
                return "— Non renseigné —" if x is None else o[x]
            chosen = st.radio(f"**{label}**", opts_ext, format_func=_fmt,
                              index=(stored + 1) if stored is not None else 0,
                              key=f"{key_prefix}_{field}", horizontal=False)
            collected[field] = chosen if chosen is not None else ""
            if chosen is not None:
                total += chosen
                answered += 1

        if answered == 10:
            pct = round((total / 50) * 100)
            collected["ndi_score_total"] = total
            collected["ndi_score_pct"]   = pct
            color = _ndi_color(pct)
            st.markdown(
                f'<div class="score-box" style="background:{color}">'
                f'NDI : {total}/50 ({pct}%) — {_ndi_interp(pct)}</div>',
                unsafe_allow_html=True)
        else:
            collected["ndi_score_total"] = ""
            collected["ndi_score_pct"]   = ""
            if answered > 0:
                st.caption(f"({answered}/10 items renseignés)")

        return collected

    @classmethod
    def score(cls, data):
        try:    pct = float(data.get("ndi_score_pct", ""))
        except: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        tot = data.get("ndi_score_total", "—")
        return {"score": pct, "interpretation": f"{tot}/50 ({pct:.0f}%) — {_ndi_interp(pct)}",
                "color": _ndi_color(pct), "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        try:    return float(bilan_data.get("ndi_score_pct", "")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        vals = []
        for _, row in bilans_df.iterrows():
            try:    vals.append(float(row.get("ndi_score_pct", "")))
            except: vals.append(None)
        xp = [labels[i] for i, v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                name="NDI %", line=dict(color="#D85A30", width=2.5),
                marker=dict(size=9),
                text=[f"{v:.0f}%" for v in yp], textposition="top center"))
        for y, color, label in [(8, "#388e3c", "≤8% normal"),
                                 (28, "#f57c00", "≤28% légère"),
                                 (48, "#e65100", "≤48% modérée")]:
            fig.add_hline(y=y, line_dash="dot", line_color=color,
                          annotation_text=label, annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0, 105], title="NDI (%)"),
                          height=320, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('ndi', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "NDI /50", "col_key": "ndi_score_total",
             "values": [r.get("ndi_score_total","—") for _,r in bilans_df.iterrows()]},
            {"label": "NDI %", "col_key": "ndi_score_pct",
             "values": [r.get("ndi_score_pct","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan": lbl, "NDI /50": row.get("ndi_score_total", "—"),
                             "NDI %": row.get("ndi_score_pct", "—"),
                 "Interprétation": _ndi_interp(float(row.get("ndi_score_pct", 0) or 0))}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
