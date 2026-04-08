"""tests/questionnaires/acl_rsi.py — ACL-RSI (Anterior Cruciate Ligament — Return to Sport after Injury)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

ACL_RSI_ITEMS = [
    ("acl_q1","Je suis inquiet(e) de me blesser à nouveau le genou en pratiquant mon sport"),
    ("acl_q2","Je suis frustré(e) de devoir prendre en compte mon genou dans mes activités sportives"),
    ("acl_q3","J'ai peur de performer à pleine capacité dans mon sport"),
    ("acl_q4","Il m'est difficile d'envisager la reprise sportive"),
    ("acl_q5","Je suis confiant(e) de pouvoir performer à mon niveau d'avant la blessure"),
    ("acl_q6","Je m'inquiète de la performance de mon genou lors de la reprise sportive"),
    ("acl_q7","Je ne pense pas être assez fort(e) mentalement pour retourner au sport"),
    ("acl_q8","Je pense que mon genou ne sera pas aussi stable qu'avant la blessure"),
    ("acl_q9","Je suis déterminé(e) à reprendre mon sport le plus tôt possible"),
    ("acl_q10","Je suis confiant(e) dans la capacité de mon genou à répondre aux exigences sportives"),
    ("acl_q11","Ma blessure au LCA a eu un impact négatif sur mon identité sportive"),
    ("acl_q12","Je pense avoir une bonne récupération de mon genou"),
]


@register_test
class ACLRSI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"acl_rsi","nom":"ACL-RSI — Retour au sport","tab_label":"🏃 ACL-RSI","categorie":"questionnaire",
                "tags":["LCA","genou","retour sport","psychologique","confiance"],
                "description":"ACL Return to Sport after Injury — 12 items, préparation psychologique au retour sport"}

    @classmethod
    def fields(cls):
        return [k for k,_ in ACL_RSI_ITEMS]+["acl_rsi_score"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score ACL-RSI (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🏃 ACL-RSI — Préparation psychologique retour sport</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = Pas du tout d\'accord · 100 = Tout à fait d\'accord. Score élevé = bonne préparation psychologique.</div>', unsafe_allow_html=True)
        collected={}; vals=[]
        for k,label in ACL_RSI_ITEMS:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 50
            except: v=50
            val=st.slider(label,0,100,v,step=10,key=f"{key_prefix}_{k}")
            collected[k]=val; vals.append(val)
        score=round(sum(vals)/len(vals))
        collected["acl_rsi_score"]=score
        color="#388e3c" if score>=56 else "#f57c00" if score>=28 else "#d32f2f"
        msg="Prêt psychologiquement" if score>=56 else "Préparation en cours" if score>=28 else "Pas encore prêt"
        st.markdown(f'<div class="score-box" style="background:{color}">ACL-RSI : {score}/100 — {msg}</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("acl_rsi_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=56 else "#f57c00" if s>=28 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("acl_rsi_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("acl_rsi_score","")))
            except: vals.append(None)
        fig=go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="ACL-RSI",line=dict(color="#1D9E75",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=56,line_dash="dot",line_color="#388e3c",annotation_text="Seuil retour sport ≥56")
        fig.update_layout(yaxis=dict(range=[0,105],title="Score /100"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"ACL-RSI":r.get("acl_rsi_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
