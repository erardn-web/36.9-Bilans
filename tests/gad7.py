"""tests/questionnaires/douleur_psy.py — PCS, BPI, PHQ-9, GAD-7, ISI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── PCS Pain Catastrophizing Scale ───────────────────────────────────────────
@register_test
class GAD7(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"gad7","nom":"GAD-7 — Anxiété","tab_label":"😟 GAD-7",
                "categorie":"questionnaire","tags":["anxiété","santé mentale","douleur chronique","psychosocial"],
                "description":"Generalized Anxiety Disorder-7 — dépistage anxiété /21. Seuil modéré ≥ 10"}
    ITEMS=[
        ("gad_q1","Se sentir nerveux(se), anxieux(se) ou à bout"),
        ("gad_q2","Ne pas être capable d'arrêter de vous inquiéter ou de contrôler vos inquiétudes"),
        ("gad_q3","Vous inquiéter trop à propos de sujets variés"),
        ("gad_q4","Avoir du mal à vous détendre"),
        ("gad_q5","Être tellement agité(e) qu'il vous est difficile de rester assis(e) tranquille"),
        ("gad_q6","Devenir facilement contrarié(e) ou irritable"),
        ("gad_q7","Avoir peur que quelque chose de terrible puisse se produire"),
    ]
    OPTS=["0 — Jamais","1 — Plusieurs jours","2 — Plus de la moitié des jours","3 — Presque tous les jours"]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["gad7_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score GAD-7 (/21)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">😟 GAD-7 — Dépistage anxiété généralisée</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Au cours des 2 dernières semaines, à quelle fréquence avez-vous été gêné(e) par les problèmes suivants ?</div>', unsafe_allow_html=True)
        collected={}; total=0
        for k,label in self.ITEMS:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(label,list(range(4)),index=stored,format_func=lambda x:self.OPTS[x],horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["gad7_score"]=total
        color="#388e3c" if total<=4 else "#f57c00" if total<=9 else "#d32f2f"
        msg="Minimale" if total<=4 else "Légère" if total<=9 else "Modérée" if total<=14 else "Sévère"
        st.markdown(f'<div class="score-box" style="background:{color}">GAD-7 : {total}/21 — Anxiété {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("gad7_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=4 else "#f57c00" if s<=9 else "#d32f2f"
        msg="Légère" if s<=9 else "Modérée" if s<=14 else "Sévère"
        return {"score":s,"interpretation":f"{s:.0f}/21 — {msg}","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("gad7_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("gad7_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="GAD-7",line=dict(color="#EF9F27",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=10,line_dash="dot",line_color="#f57c00",annotation_text="Anxiété modérée ≥10")
        fig.update_layout(yaxis=dict(range=[0,22],title="GAD-7 /21"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('gad7', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"GAD-7":r.get("gad7_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── ISI Insomnia Severity Index ───────────────────────────────────────────────