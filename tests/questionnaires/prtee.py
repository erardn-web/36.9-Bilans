"""tests/questionnaires/prtee.py — PRTEE (Patient-Rated Tennis Elbow Evaluation)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

PRTEE_PAIN = [
    ("prtee_p1","Au repos"),("prtee_p2","Lors des activités répétées du bras"),
    ("prtee_p3","Lors d'activités avec l'avant-bras en force"),
    ("prtee_p4","Quand vous portez un sac d'épicerie"),
    ("prtee_p5","Quand la douleur est à son pire"),
]
PRTEE_FUNC = [
    ("prtee_f1","Tourner une poignée de porte ou un couvercle de bocal"),
    ("prtee_f2","Porter un sac d'épicerie ou une mallette"),
    ("prtee_f3","Soulever un café ou un verre d'eau plein"),
    ("prtee_f4","Se laver le dos"),("prtee_f5","Faire des tractions à deux mains"),
    ("prtee_f6","Jardiner, tâches ménagères lourdes"),
    ("prtee_f7","Couper, trancher des aliments"),("prtee_f8","Activités nécessitant la force du bras"),
    ("prtee_f9","Utiliser des outils ou appareils ménagers"),
    ("prtee_f10","Ouvrir des bouteilles ou des bocaux"),
]


@register_test
class PRTEE(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"prtee","nom":"PRTEE — Coude (Tennis Elbow)","tab_label":"🎾 PRTEE","categorie":"questionnaire",
                "tags":["coude","épicondylalgie","tennis elbow","douleur","fonctionnel"],
                "description":"Patient-Rated Tennis Elbow Evaluation — 15 items, douleur + fonction /100"}

    @classmethod
    def fields(cls):
        return [k for k,_ in PRTEE_PAIN+PRTEE_FUNC]+["prtee_pain","prtee_func","prtee_total"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🎾 PRTEE — Évaluation coude (Tennis Elbow)</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = aucune douleur/difficulté · 10 = pire douleur/incapable</div>', unsafe_allow_html=True)
        collected = {}
        def _sec(title, items):
            st.markdown(f"**{title}**")
            for k,label in items:
                raw=lv(k,None)
                try: v=int(float(raw)) if raw not in (None,"","None") else 0
                except: v=0
                val=st.slider(label,0,10,v,key=f"{key_prefix}_{k}")
                collected[k]=val
        _sec("Douleur /50",PRTEE_PAIN)
        _sec("Fonction /50 (chaque item /10, total /100 divisé par 2)",PRTEE_FUNC)
        pain=sum(collected[k] for k,_ in PRTEE_PAIN)
        func=round(sum(collected[k] for k,_ in PRTEE_FUNC)/2,1)
        total=round(pain+func,1)
        collected.update({"prtee_pain":pain,"prtee_func":func,"prtee_total":total})
        color="#388e3c" if total<=20 else "#f57c00" if total<=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">PRTEE : {total}/100 | Douleur:{pain}/50 Fonction:{func}/50</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("prtee_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=20 else "#f57c00" if s<=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("prtee_total",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("prtee_total","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="PRTEE",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="PRTEE /100"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"PRTEE":r.get("prtee_total","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
