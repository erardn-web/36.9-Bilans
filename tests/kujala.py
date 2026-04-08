"""tests/questionnaires/kujala.py — Score de Kujala AKPS (Anterior Knee Pain Scale)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

KUJALA_ITEMS = [
    ("kuj_q1","Boiterie",[(5,"Aucune"),(3,"Légère ou périodique"),(0,"Constante")]),
    ("kuj_q2","Soutien de la mise en charge",[(5,"Aucun besoin"),(3,"Bâton ou béquilles"),(0,"Mise en charge impossible")]),
    ("kuj_q3","Marcher",[(5,"Pas de problème"),(3,"Douleur après >2 km"),(2,"Douleur après <2 km"),(1,"Douleur après <500 m"),(0,"Toujours de la douleur")]),
    ("kuj_q4","Escaliers",[(10,"Pas de problème"),(8,"Légère douleur"),(5,"Douleur modérée"),(2,"Seulement en descendant"),(0,"Impossible")]),
    ("kuj_q5","Accroupissement/agenouillement",[(5,"Pas de problème"),(4,"Légère douleur"),(3,"Modérée, parfois impossible"),(2,"Douleur importante"),(0,"Impossible")]),
    ("kuj_q6","Courir",[(10,"Pas de problème"),(8,"Légère douleur"),(5,"Douleur modérée"),(2,"Douleur sévère"),(0,"Impossible")]),
    ("kuj_q7","Sauter",[(10,"Pas de problème"),(7,"Légère douleur"),(4,"Douleur modérée"),(2,"Douleur sévère"),(0,"Impossible")]),
    ("kuj_q8","Maintien en position assise prolongée",[(10,"Pas de problème"),(8,"Légère douleur"),(6,"Douleur modérée"),(4,"Souvent, obligé de se lever"),(2,"Impossible")]),
    ("kuj_q9","Douleur",[(10,"Aucune"),(8,"Légère, parfois"),(5,"Modérée, parfois"),(2,"Sévère, parfois"),(0,"Constante")]),
    ("kuj_q10","Gonflement",[(10,"Aucun"),(8,"Après effort sévère"),(6,"Après effort léger"),(2,"Toujours"),(0,"Permanent et sévère")]),
    ("kuj_q11","Atrophie de la cuisse",[(5,"Aucune"),(3,"Légère"),(0,"Importante")]),
    ("kuj_q12","Flexion du genou",[(5,"Aucune limitation"),(4,"Légère limitation"),(2,"Moins de 90°"),(0,"Moins de 90° et douleur")]),
    ("kuj_q13","Instabilité du genou",[(5,"Aucune"),(3,"Parfois avec sport intense"),(1,"Fréquemment avec sport"),(0,"Lors d'activités courantes")]),
]


def _kujala_interp(s):
    if s>=85: return "Excellent"
    if s>=70: return "Bon"
    if s>=55: return "Passable"
    return "Mauvais"


@register_test
class Kujala(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"kujala","nom":"Kujala AKPS — Genou antérieur","tab_label":"🦵 Kujala","categorie":"questionnaire",
                "tags":["genou","fémoro-patellaire","douleur antérieure","PFPS"],
                "description":"Kujala AKPS — Anterior Knee Pain Scale — 13 items /100"}

    @classmethod
    def fields(cls):
        return [k for k,*_ in KUJALA_ITEMS]+["kujala_score"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score Kujala (/100)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦵 Kujala AKPS — Genou antérieur</div>', unsafe_allow_html=True)
        collected={}; total=0
        for field,label,opts in KUJALA_ITEMS:
            raw=lv(field,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else None
            except: stored=None
            vals=[o[0] for o in opts]; opts_ext=[None]+vals
            def _fmt(x,o=opts): return "— Non renseigné —" if x is None else next(l for s,l in o if s==x)
            default=(vals.index(stored)+1) if stored in vals else 0
            chosen=st.radio(f"**{label}**",opts_ext,format_func=_fmt,index=default,key=f"{key_prefix}_{field}",horizontal=True)
            collected[field]=chosen if chosen is not None else ""
            if chosen is not None: total+=chosen
        collected["kujala_score"]=total
        color="#388e3c" if total>=85 else "#f57c00" if total>=70 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">Kujala : {total}/100 — {_kujala_interp(total)}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("kujala_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=85 else "#f57c00" if s>=70 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100 — {_kujala_interp(s)}","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("kujala_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("kujala_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Kujala",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        for y,c,l in [(85,"#388e3c","Excellent ≥85"),(70,"#f57c00","Bon ≥70")]:
            fig.add_hline(y=y,line_dash="dot",line_color=c,annotation_text=l,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="Score /100"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Kujala":r.get("kujala_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
