"""tests/questionnaires/fabq.py — FABQ (Fear-Avoidance Beliefs Questionnaire)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

FABQ_PA = [  # Physical Activity subscale
    ("fabq_pa1","Mon activité physique aggrave ma douleur"),
    ("fabq_pa2","L'activité physique pourrait aggraver ma douleur"),
    ("fabq_pa3","L'activité physique pourrait nuire à mon dos"),
    ("fabq_pa4","Je ne devrais pas faire d'activité physique qui aggrave ma douleur"),
]
FABQ_WORK = [  # Work subscale
    ("fabq_w1","Mon travail aggrave ma douleur"),
    ("fabq_w2","Mon travail pourrait aggraver ma douleur"),
    ("fabq_w3","Mon travail peut me faire du mal"),
    ("fabq_w4","Je ne devrais pas faire mon travail normal avec ma douleur"),
    ("fabq_w5","Je ne peux pas faire mon travail normal à cause de ma douleur"),
    ("fabq_w6","Mon travail est trop lourd pour moi"),
    ("fabq_w7","Mon travail aggrave ou a aggravé ma douleur"),
]


@register_test
class FABQ(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"fabq","nom":"FABQ — Peurs et croyances","tab_label":"😨 FABQ","categorie":"questionnaire",
                "tags":["kinésiophobie","peur","croyances","lombalgie","psychosocial"],
                "description":"Fear-Avoidance Beliefs Questionnaire — activité physique /24 + travail /42"}

    @classmethod
    def fields(cls):
        return [k for k,_ in FABQ_PA+FABQ_WORK]+["fabq_pa_score","fabq_work_score"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "sous_scores", "label": "FABQ-PA + FABQ-W", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">😨 FABQ — Croyances de peur-évitement</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = Pas du tout d\'accord · 6 = Complètement d\'accord. Seuil clinique : PA ≥ 15, Travail ≥ 34.</div>', unsafe_allow_html=True)
        collected={}
        def _sec(title,items,label_sfx):
            st.markdown(f"**{title}**")
            for k,question in items:
                raw=lv(k,None)
                try: v=int(float(raw)) if raw not in (None,"","None") else 0
                except: v=0
                val=st.slider(question,0,6,v,key=f"{key_prefix}_{k}")
                collected[k]=val
        _sec("Activité physique",FABQ_PA,"pa")
        _sec("Travail",FABQ_WORK,"work")
        pa=sum(collected[k] for k,_ in FABQ_PA)
        work=sum(collected[k] for k,_ in FABQ_WORK)
        collected.update({"fabq_pa_score":pa,"fabq_work_score":work})
        pa_color="#d32f2f" if pa>=15 else "#f57c00" if pa>=8 else "#388e3c"
        work_color="#d32f2f" if work>=34 else "#f57c00" if work>=20 else "#388e3c"
        c1,c2=st.columns(2)
        c1.markdown(f'<div class="score-box" style="background:{pa_color}">FABQ-PA : {pa}/24{" ⚠️" if pa>=15 else ""}</div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="score-box" style="background:{work_color}">FABQ-W : {work}/42{" ⚠️" if work>=34 else ""}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: w=float(data.get("fabq_work_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        pa=data.get("fabq_pa_score","—")
        color="#d32f2f" if w>=34 else "#f57c00" if w>=20 else "#388e3c"
        return {"score":w,"interpretation":f"PA:{pa}/24 W:{w:.0f}/42","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("fabq_work_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c,mx in [("fabq_pa_score","PA","#2B57A7",24),("fabq_work_score","Travail","#D85A30",42)]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=f"{l} /{mx}",line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(title="Score"),height=300,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"FABQ-PA":r.get("fabq_pa_score","—"),"FABQ-W":r.get("fabq_work_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
