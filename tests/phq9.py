"""tests/questionnaires/douleur_psy.py — PCS, BPI, PHQ-9, GAD-7, ISI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── PCS Pain Catastrophizing Scale ───────────────────────────────────────────
@register_test
class PHQ9(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"phq9","nom":"PHQ-9 — Dépression","tab_label":"🫀 PHQ-9",
                "categorie":"questionnaire","tags":["dépression","santé mentale","douleur chronique","psychosocial"],
                "description":"Patient Health Questionnaire-9 — dépistage dépression /27. Seuil modéré ≥ 10"}
    ITEMS=[
        ("phq_q1","Peu d'intérêt ou de plaisir à faire les choses"),
        ("phq_q2","Sentiment de tristesse, déprime ou désespoir"),
        ("phq_q3","Difficultés à dormir ou dormez trop"),
        ("phq_q4","Sentiment de fatigue ou peu d'énergie"),
        ("phq_q5","Peu d'appétit ou manger trop"),
        ("phq_q6","Mauvaise opinion de vous-même, sentiment d'être nul"),
        ("phq_q7","Difficultés à vous concentrer"),
        ("phq_q8","Bougez ou parlez tellement lentement que les autres le remarquent"),
        ("phq_q9","Pensées que vous seriez mieux mort(e) ou idées de vous faire du mal"),
    ]
    OPTS=["0 — Jamais","1 — Plusieurs jours","2 — Plus de la moitié des jours","3 — Presque tous les jours"]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["phq9_score"]
    def _interp(self,s):
        if s<=4: return "Aucune/Minimale"
        if s<=9: return "Légère"
        if s<=14: return "Modérée"
        if s<=19: return "Modérément sévère"
        return "Sévère"
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score PHQ-9 (/27)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🫀 PHQ-9 — Dépistage dépression</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Au cours des 2 dernières semaines, à quelle fréquence avez-vous été gêné(e) par les problèmes suivants ?</div>', unsafe_allow_html=True)
        collected={}; total=0
        for k,label in self.ITEMS:
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=st.radio(label,list(range(4)),index=stored,format_func=lambda x:self.OPTS[x],horizontal=True,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
            if k=="phq_q9" and val>0:
                st.warning("⚠️ Question sur les idées de mort — évaluation clinique approfondie recommandée.")
        collected["phq9_score"]=total
        color="#388e3c" if total<=4 else "#f57c00" if total<=9 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">PHQ-9 : {total}/27 — {self._interp(total)}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("phq9_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=4 else "#f57c00" if s<=9 else "#d32f2f"
        interps=[(20,"Sévère"),(15,"Mod. sévère"),(10,"Modérée"),(5,"Légère"),(0,"Minimale")]
        interp=next(l for t,l in interps if s>=t)
        return {"score":s,"interpretation":f"{s:.0f}/27 — {interp}","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("phq9_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("phq9_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="PHQ-9",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=10,line_dash="dot",line_color="#f57c00",annotation_text="Dépression modérée ≥10")
        fig.update_layout(yaxis=dict(range=[0,28],title="PHQ-9 /27"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('phq9', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"PHQ-9":r.get("phq9_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── GAD-7 Anxiety ─────────────────────────────────────────────────────────────