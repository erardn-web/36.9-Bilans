"""tests/questionnaires/lefs.py — LEFS (Lower Extremity Functional Scale)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

LEFS_ITEMS = [
    ("lefs_q1",  "Toutes vos activités habituelles de travail, de maison ou d'école"),
    ("lefs_q2",  "Vos passe-temps habituels, activités récréatives ou sportives"),
    ("lefs_q3",  "Entrer et sortir de la baignoire"),
    ("lefs_q4",  "Marcher entre les pièces"),
    ("lefs_q5",  "Mettre vos chaussures ou vos chaussettes"),
    ("lefs_q6",  "S'accroupir"),
    ("lefs_q7",  "Soulever un objet (ex: sac d'épicerie) du sol"),
    ("lefs_q8",  "Effectuer des activités légères (ex: faire le ménage)"),
    ("lefs_q9",  "Effectuer des activités modérées (ex: nettoyer le sol)"),
    ("lefs_q10", "Monter ou descendre une volée de marches"),
    ("lefs_q11", "Marcher une heure"),
    ("lefs_q12", "S'asseoir et se lever d'une chaise"),
    ("lefs_q13", "Courir sur terrain plat"),
    ("lefs_q14", "Courir sur terrain inégal"),
    ("lefs_q15", "Faire des virages serrés en courant"),
    ("lefs_q16", "Sautiller"),
    ("lefs_q17", "Tourner sur votre membre blessé"),
    ("lefs_q18", "Rouler dans un lit"),
    ("lefs_q19", "Entrer et sortir d'une voiture"),
    ("lefs_q20", "Marcher 2 pâtés de maisons"),
]
LEFS_OPTS = ["4 — Aucune difficulté", "3 — Un peu de difficulté",
             "2 — Difficulté modérée", "1 — Difficulté extrême", "0 — Incapable"]


def _lefs_interp(score):
    if score >= 70: return "Fonction excellente"
    if score >= 54: return "Fonction modérée"
    if score >= 40: return "Fonction limitée"
    return "Fonction très limitée"


@register_test
class LEFS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id": "lefs", "nom": "LEFS — Membres inférieurs",
                "tab_label": "🦿 LEFS", "categorie": "questionnaire",
                "tags": ["membres inférieurs", "fonctionnel", "genou", "hanche", "cheville"],
                "description": "Lower Extremity Functional Scale — 20 items /80, universel MI"}

    @classmethod
    def fields(cls):
        return [k for k, _ in LEFS_ITEMS] + ["lefs_score"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦿 LEFS — Échelle fonctionnelle membres inférieurs</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Pour chaque activité, indiquez votre niveau de difficulté aujourd\'hui. Score max = 80 (aucune limitation).</div>', unsafe_allow_html=True)
        collected = {}
        total = 0; answered = 0
        for field, label in LEFS_ITEMS:
            raw = lv(field, None)
            try:    stored = int(float(raw)) if raw not in (None,"","None") else None
            except: stored = None
            opts_ext = [None]+list(range(5))
            chosen = st.radio(label, opts_ext,
                format_func=lambda x,o=LEFS_OPTS: "— Non renseigné —" if x is None else o[4-x],
                index=(stored+1) if stored is not None else 0,
                key=f"{key_prefix}_{field}", horizontal=True)
            collected[field] = chosen if chosen is not None else ""
            if chosen is not None: total += chosen; answered += 1
        if answered >= 18:
            collected["lefs_score"] = total
            color = "#388e3c" if total >= 70 else "#f57c00" if total >= 54 else "#d32f2f"
            st.markdown(f'<div class="score-box" style="background:{color}">LEFS : {total}/80 — {_lefs_interp(total)}</div>', unsafe_allow_html=True)
        else:
            collected["lefs_score"] = ""
            if answered: st.caption(f"({answered}/20 items)")
        return collected

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("lefs_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color = "#388e3c" if s>=70 else "#f57c00" if s>=54 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/80 — {_lefs_interp(s)}","color":color,"details":{}}

    @classmethod
    def is_filled(cls, data):
        try: return float(data.get("lefs_score","")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals = []
        for _, row in bilans_df.iterrows():
            try: vals.append(float(row.get("lefs_score","")))
            except: vals.append(None)
        fig = go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="LEFS",
            line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
            text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=54,line_dash="dot",line_color="#f57c00",annotation_text="Seuil modéré")
        fig.update_layout(yaxis=dict(range=[0,85],title="LEFS /80"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"LEFS":r.get("lefs_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
