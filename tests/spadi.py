"""tests/questionnaires/spadi.py — SPADI (Shoulder Pain and Disability Index)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

SPADI_PAIN = [
    ("spadi_p1","Quelle intensité la douleur à votre épaule présente-t-elle au pire ?"),
    ("spadi_p2","Quand vous dormez sur le côté atteint ?"),
    ("spadi_p3","Quand vous essayez d'atteindre un objet sur une tablette haute ?"),
    ("spadi_p4","Quand vous touchez la nuque avec la main de l'épaule atteinte ?"),
    ("spadi_p5","Quand vous vous poussez avec le bras atteint ?"),
]
SPADI_DIS = [
    ("spadi_d1","Laver vos cheveux ?"),("spadi_d2","Laver votre dos ?"),
    ("spadi_d3","Mettre un sous-vêtement du type gilet/débardeur ?"),
    ("spadi_d4","Mettre une chemise à boutons devant ?"),
    ("spadi_d5","Mettre votre pantalon ?"),("spadi_d6","Placer un objet sur une tablette haute ?"),
    ("spadi_d7","Porter un objet lourd (plus de 5 kg) ?"),
    ("spadi_d8","Sortir quelque chose de la poche arrière de votre pantalon ?"),
]


@register_test
class SPADI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"spadi","nom":"SPADI — Épaule","tab_label":"💪 SPADI","categorie":"questionnaire",
                "tags":["épaule","douleur","incapacité","fonctionnel"],
                "description":"Shoulder Pain and Disability Index — 13 items, 2 sous-échelles /100"}

    @classmethod
    def fields(cls):
        return [k for k,_ in SPADI_PAIN+SPADI_DIS]+["spadi_pain","spadi_disability","spadi_total"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score SPADI (/100)", "default": True},
            {"key": "sous_scores", "label": "Sous-scores douleur/incapacité", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💪 SPADI — Indice douleur et incapacité épaule</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = aucune douleur/difficulté · 10 = pire douleur/totalement incapable</div>', unsafe_allow_html=True)
        collected = {}
        def _sec(title, items):
            st.markdown(f"**{title}**")
            for k,label in items:
                raw=lv(k,None)
                try: stored=int(float(raw)) if raw not in (None,"","None") else None
                except: stored=None
                val=st.slider(label,0,10,stored if stored is not None else 0,key=f"{key_prefix}_{k}")
                collected[k]=val
        _sec("Douleur",SPADI_PAIN)
        _sec("Incapacité",SPADI_DIS)
        pain_vals=[collected[k] for k,_ in SPADI_PAIN]
        dis_vals=[collected[k] for k,_ in SPADI_DIS]
        pain=round(sum(pain_vals)/len(pain_vals)*10,1)
        dis=round(sum(dis_vals)/len(dis_vals)*10,1)
        total=round((pain+dis)/2,1)
        collected.update({"spadi_pain":pain,"spadi_disability":dis,"spadi_total":total})
        color="#388e3c" if total<=20 else "#f57c00" if total<=50 else "#d32f2f"
        c1,c2=st.columns(2)
        c1.markdown(f'<div class="score-box" style="background:{color}">Douleur : {pain}/100<br>Incapacité : {dis}/100</div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="score-box" style="background:{color}">SPADI total : {total}/100</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls, data):
        try: s=float(data.get("spadi_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=20 else "#f57c00" if s<=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("spadi_total",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        fig=go.Figure()
        for f,l,c in [("spadi_total","Total","#2B57A7"),("spadi_pain","Douleur","#D85A30"),("spadi_disability","Incapacité","#1D9E75")]:
            vals=[]
            for _,row in bilans_df.iterrows():
                try: vals.append(float(row.get(f,"")))
                except: vals.append(None)
            xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
            if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=l,line=dict(color=c,width=2.5),marker=dict(size=8),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="SPADI /100"),height=320,legend=dict(orientation="h",y=-0.2),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"Total":r.get("spadi_total","—"),"Douleur":r.get("spadi_pain","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
