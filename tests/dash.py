"""tests/questionnaires/dash.py — DASH complet (Disabilities of Arm, Shoulder and Hand)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

DASH_ITEMS_FUNC = [
    ("dash_q1",  "Ouvrir un bocal hermétiquement fermé (neuf ou déjà ouvert)"),
    ("dash_q2",  "Écrire"),
    ("dash_q3",  "Tourner une clé"),
    ("dash_q4",  "Préparer un repas"),
    ("dash_q5",  "Pousser ou ouvrir une porte lourde"),
    ("dash_q6",  "Placer un objet sur une étagère au-dessus de votre tête"),
    ("dash_q7",  "Faire des travaux ménagers lourds (laver planchers, murs)"),
    ("dash_q8",  "Jardiner"),
    ("dash_q9",  "Faire son lit"),
    ("dash_q10", "Porter un sac ou une valise"),
    ("dash_q11", "Porter un objet lourd (plus de 5 kg)"),
    ("dash_q12", "Changer une ampoule électrique au-dessus de votre tête"),
    ("dash_q13", "Se laver ou se sécher les cheveux"),
    ("dash_q14", "Se laver le dos"),
    ("dash_q15", "Enfiler un chandail"),
    ("dash_q16", "Couper des aliments avec un couteau"),
    ("dash_q17", "Activités de loisirs peu exigeantes (cartes, tricot)"),
    ("dash_q18", "Activités de loisirs avec force ou chocs (golf, tennis)"),
    ("dash_q19", "Activités de loisirs avec mouvements libres du bras (natation, frisbee)"),
    ("dash_q20", "Se déplacer d'une région à l'autre (conduire, transports en commun)"),
    ("dash_q21", "Activités sexuelles"),
]
DASH_ITEMS_SYMP = [
    ("dash_q22", "Douleur au bras, épaule ou main"),
    ("dash_q23", "Douleur lors d'activités spécifiques"),
    ("dash_q24", "Sensation de fourmillement (picotements)"),
    ("dash_q25", "Faiblesse au bras, épaule ou main"),
    ("dash_q26", "Raideur au bras, épaule ou main"),
]
DASH_ITEMS_SOCIAL = [
    ("dash_q27", "Difficultés à dormir à cause de la douleur"),
    ("dash_q28", "Sentiment de moins d'estime de soi"),
    ("dash_q29", "Difficultés dans vos activités sociales"),
    ("dash_q30", "Limitations dans votre travail ou activités quotidiennes"),
]

DASH_OPTS_FUNC  = ["1 — Aucune difficulté", "2 — Légère difficulté", "3 — Difficulté modérée",
                   "4 — Grande difficulté", "5 — Incapable"]
DASH_OPTS_SYMP  = ["1 — Aucune", "2 — Légère", "3 — Modérée", "4 — Sévère", "5 — Extrême"]
DASH_OPTS_AGREE = ["1 — Pas du tout d'accord", "2 — Légèrement d'accord", "3 — Modérément d'accord",
                   "4 — Très d'accord", "5 — Tout à fait d'accord"]


def _dash_interp(score):
    if score <= 10: return "Très bonne fonction"
    if score <= 30: return "Légère incapacité"
    if score <= 50: return "Incapacité modérée"
    return "Incapacité sévère"


def _dash_color(score):
    if score <= 10: return "#388e3c"
    if score <= 30: return "#7cb87e"
    if score <= 50: return "#f57c00"
    return "#d32f2f"


@register_test
class DASH(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "dash", "nom": "DASH — Membre supérieur (complet)",
            "tab_label": "💪 DASH",
            "categorie": "questionnaire",
            "tags": ["épaule", "bras", "main", "membre supérieur", "fonctionnel"],
            "description": "DASH complet 30 items — Disabilities of Arm, Shoulder and Hand /100",
        }

    @classmethod
    def fields(cls):
        all_items = DASH_ITEMS_FUNC + DASH_ITEMS_SYMP + DASH_ITEMS_SOCIAL
        return [k for k, _ in all_items] + ["dash_score"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score DASH (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💪 DASH — Membre supérieur</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">30 questions sur les difficultés rencontrées la semaine passée. '
            'Score 0 (aucune incapacité) à 100 (incapacité maximale).</div>',
            unsafe_allow_html=True)

        collected = {}

        def _render_block(title, items, opts_list):
            with st.expander(title, expanded=False):
                for k, label in items:
                    raw = lv(k, None)
                    try:    stored = int(float(raw)) if raw not in (None, "", "None") else None
                    except: stored = None
                    opts_ext = [None] + list(range(1, 6))
                    def _fmt(x, o=opts_list):
                        return "— Non renseigné —" if x is None else o[x-1]
                    default_idx = stored if stored is not None else 0
                    chosen = st.radio(label, opts_ext, format_func=_fmt,
                                      index=default_idx,
                                      key=f"{key_prefix}_{k}", horizontal=True)
                    collected[k] = chosen if chosen is not None else ""

        _render_block("Activités fonctionnelles (Q1–Q21)", DASH_ITEMS_FUNC, DASH_OPTS_FUNC)
        _render_block("Symptômes (Q22–Q26)", DASH_ITEMS_SYMP, DASH_OPTS_SYMP)
        _render_block("Impact social/émotionnel (Q27–Q30)", DASH_ITEMS_SOCIAL, DASH_OPTS_AGREE)

        # Calcul score
        all_items = DASH_ITEMS_FUNC + DASH_ITEMS_SYMP + DASH_ITEMS_SOCIAL
        vals = []
        for k, _ in all_items:
            try:    vals.append(int(float(collected.get(k, ""))))
            except: pass

        if len(vals) >= 27:  # tolérance 3 items manquants
            score = round(((sum(vals) / len(vals)) - 1) * 25, 1)
            collected["dash_score"] = score
            color = _dash_color(score)
            st.markdown(
                f'<div class="score-box" style="background:{color}">'
                f'DASH : {score}/100 — {_dash_interp(score)}<br>'
                f'<small style="font-size:.75rem">({len(vals)}/30 items)</small></div>',
                unsafe_allow_html=True)
        else:
            collected["dash_score"] = ""
            if vals:
                st.caption(f"({len(vals)}/30 items renseignés — minimum 27 requis)")

        return collected

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("dash_score", ""))
        except: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        return {"score": s, "interpretation": f"{s}/100 — {_dash_interp(s)}",
                "color": _dash_color(s), "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        try:    return float(bilan_data.get("dash_score", "")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        vals = []
        for _, row in bilans_df.iterrows():
            try:    vals.append(float(row.get("dash_score", "")))
            except: vals.append(None)
        xp = [labels[i] for i, v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                name="DASH", line=dict(color="#7F77DD", width=2.5),
                marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp], textposition="top center"))
        for y, color, label in [(10, "#388e3c", "≤10 très bon"),
                                 (30, "#f57c00", "≤30 légère"),
                                 (50, "#e65100", "≤50 modérée")]:
            fig.add_hline(y=y, line_dash="dot", line_color=color,
                          annotation_text=label, annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0, 105], title="DASH /100"),
                          height=320, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('dash', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "DASH", "col_key": "dash_score",
             "values": [r.get("dash_score","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan": lbl, "DASH": row.get("dash_score", "—"),
                             "Interprétation": _dash_interp(float(row.get("dash_score", 0) or 0))}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
