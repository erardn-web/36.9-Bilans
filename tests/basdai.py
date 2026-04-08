"""tests/questionnaires/rhumato_geriatrie.py — HAQ, BASDAI, DAS28, Frailty, FRAIL, Gait Speed"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── HAQ Health Assessment Questionnaire ──────────────────────────────────────
@register_test
class BASDAI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"basdai","nom":"BASDAI — Spondylarthrite","tab_label":"🦴 BASDAI",
                "categorie":"questionnaire","tags":["spondylarthrite","rhumatologie","activité maladie"],
                "description":"Bath Ankylosing Spondylitis Disease Activity Index — 6 questions /10. Seuil ≥ 4 = activité élevée"}
    ITEMS=[
        ("basdai_q1","Fatigue / épuisement"),("basdai_q2","Douleur dans le cou, le dos ou les hanches"),
        ("basdai_q3","Douleur ou gonflement des autres articulations"),
        ("basdai_q4","Gêne dans les zones sensibles au toucher"),
        ("basdai_q5a","Intensité de la raideur matinale"),("basdai_q5b","Durée de la raideur matinale (h) — pondéré"),
    ]
    @classmethod
    def fields(cls): return [k for k,_ in cls.ITEMS]+["basdai_score"]
    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score BASDAI (/10)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦴 BASDAI — Spondylarthrite ankylosante</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = aucun · 10 = maximal. Score ≥ 4 = activité de la maladie élevée.</div>', unsafe_allow_html=True)
        collected={}
        q_labels=["Fatigue/épuisement (0-10)","Douleur cervicale/dorsale/hanches (0-10)",
                  "Douleur/gonflement autres articulations (0-10)","Gêne zones sensibles (0-10)",
                  "Raideur matinale — intensité (0-10)","Raideur matinale — durée (0-10, 0=<30min, 10=≥2h)"]
        vals=[]
        for i,(k,label) in enumerate(self.ITEMS):
            raw=lv(k,None)
            try: v=float(raw) if raw not in (None,"","None") else 0.0
            except: v=0.0
            val=st.slider(q_labels[i],0.0,10.0,v,0.5,key=f"{key_prefix}_{k}")
            collected[k]=val; vals.append(val)
        # BASDAI = moyenne Q1-4 + moyenne(Q5a+Q5b)/2 / 5
        score=round((sum(vals[:4])+(vals[4]+vals[5])/2)/5,1)
        collected["basdai_score"]=score
        color="#d32f2f" if score>=4 else "#f57c00" if score>=2 else "#388e3c"
        msg="Activité élevée" if score>=4 else "Activité modérée" if score>=2 else "Activité faible"
        st.markdown(f'<div class="score-box" style="background:{color}">BASDAI : {score}/10 — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("basdai_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#d32f2f" if s>=4 else "#f57c00" if s>=2 else "#388e3c"
        return {"score":s,"interpretation":f"{s}/10","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("basdai_score",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("basdai_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="BASDAI",line=dict(color="#D85A30",width=2.5),marker=dict(size=9),text=[f"{v:.1f}" for v in yp],textposition="top center"))
        fig.add_hline(y=4,line_dash="dot",line_color="#d32f2f",annotation_text="Activité élevée ≥4")
        fig.update_layout(yaxis=dict(range=[0,11],title="BASDAI /10"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"BASDAI":r.get("basdai_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── Clinical Frailty Scale ────────────────────────────────────────────────────