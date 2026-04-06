"""tests/questionnaires/other_scores.py — IKDC, CSI, QBPDS, ATRS, WOSI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── IKDC ─────────────────────────────────────────────────────────────────────
@register_test
class WOSI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"wosi","nom":"WOSI — Instabilité épaule","tab_label":"💪 WOSI","categorie":"questionnaire",
                "tags":["épaule","instabilité","sport","fonctionnel"],
                "description":"Western Ontario Shoulder Instability Index — 21 items, impact instabilité épaule"}
    @classmethod
    def fields(cls): return [f"wosi_q{i}" for i in range(1,22)]+["wosi_score","wosi_pct"]
    QUESTIONS=[
        "Douleur physique lors d'activités au-dessus de la tête","Douleur lors d'activités avec force",
        "Douleur lors d'activités de sport ou loisirs","Faiblesse musculaire",
        "Fatigue à l'épaule","Cliquet ou craquements","Instabilité/sensation d'épaule qui cède",
        "Compensation d'autres muscles","Perte d'amplitude","Raideur matinale",
        "Gêne pour travailler","Peur de tomber sur l'épaule","Peur de se réinstabiliser",
        "Difficulté à dormir","Difficulté à soulever des objets lourds","Difficulté à soulever des objets légers",
        "Difficulté à pratiquer votre sport","Pas au niveau habituel","Conscience du problème",
        "Impact sur confiance","Impact vie quotidienne",
    ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💪 WOSI — Instabilité épaule</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Évaluez l\'impact de votre épaule sur chaque item (0 = aucun impact · 100 = impact maximal).</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.QUESTIONS,1):
            k=f"wosi_q{i}"
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            val=st.slider(q,0,100,v,step=5,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        pct=round((1-(total/2100))*100,1)
        collected.update({"wosi_score":total,"wosi_pct":pct})
        color="#388e3c" if pct>=75 else "#f57c00" if pct>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">WOSI : {pct:.0f}% (score brut: {total}/2100)</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("wosi_pct",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=75 else "#f57c00" if s>=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}%","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("wosi_pct",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("wosi_pct","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="WOSI",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}%" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="WOSI %"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"WOSI %":r.get("wosi_pct","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
