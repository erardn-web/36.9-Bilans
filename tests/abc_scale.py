"""tests/questionnaires/vestibulaire.py — ABC Scale, Mini-BESTest, VADL"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── ABC Scale Activities-specific Balance Confidence ─────────────────────────
@register_test
class ABCScale(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"abc_scale","nom":"ABC Scale — Confiance équilibre","tab_label":"⚖️ ABC",
                "categorie":"questionnaire","tags":["équilibre","confiance","chutes","vestibulaire","gériatrie"],
                "description":"Activities-specific Balance Confidence Scale — 16 activités, confiance en l'équilibre /100"}
    ITEMS=[
        ("abc_q1","Marcher dans la maison"),("abc_q2","Monter/descendre les escaliers"),
        ("abc_q3","Se baisser pour ramasser une chaussure"),("abc_q4","Atteindre une étagère à hauteur des yeux"),
        ("abc_q5","Se lever sur la pointe des pieds pour atteindre quelque chose"),("abc_q6","Monter sur une chaise"),
        ("abc_q7","Balayer le sol"),("abc_q8","Sortir de la voiture"),
        ("abc_q9","Entrer/sortir d'une voiture"),("abc_q10","Traverser un parking"),
        ("abc_q11","Monter/descendre une rampe"),("abc_q12","Marcher dans une foule"),
        ("abc_q13","Être bousculé en marchant"),("abc_q14","Monter/descendre un escalier roulant"),
        ("abc_q15","Marcher sur un trottoir glissant"),("abc_q16","Prendre un bus"),
    ]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["abc_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score moyen (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des activités", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">⚖️ ABC Scale — Confiance dans l\'équilibre</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0% = aucune confiance · 100% = confiance totale. Score ≥ 80% = bonne confiance. Seuil risque chutes < 67%.</div>', unsafe_allow_html=True)
        collected={}; total=0; n=0
        for k,label in self.ITEMS:
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 50
            except: v=50
            val=st.slider(label,0,100,v,step=10,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val; n+=1
        avg=round(total/n) if n else 0
        collected["abc_score"]=avg
        color="#388e3c" if avg>=80 else "#f57c00" if avg>=67 else "#d32f2f"
        msg="Bonne confiance" if avg>=80 else "Risque modéré" if avg>=67 else "Risque élevé de chutes"
        st.markdown(f'<div class="score-box" style="background:{color}">ABC : {avg}% — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("abc_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=80 else "#f57c00" if s>=67 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}%","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("abc_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("abc_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="ABC",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}%" for v in yp],textposition="top center"))
        fig.add_hline(y=67,line_dash="dot",line_color="#d32f2f",annotation_text="Risque chutes <67%")
        fig.add_hline(y=80,line_dash="dot",line_color="#388e3c",annotation_text="Bonne confiance ≥80%")
        fig.update_layout(yaxis=dict(range=[0,105],title="ABC %"),height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"ABC %":r.get("abc_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── Mini-BESTest ──────────────────────────────────────────────────────────────