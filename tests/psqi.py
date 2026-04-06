"""tests/questionnaires/cardiopulmonaire.py — SGRQ, CRQ, LCADL, PCFS, Borg RPE, PSQI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── Borg RPE ─────────────────────────────────────────────────────────────────
@register_test
class PSQI(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"psqi","nom":"PSQI — Qualité du sommeil","tab_label":"😴 PSQI",
                "categorie":"questionnaire","tags":["sommeil","qualité de vie","douleur chronique","BPCO"],
                "description":"Pittsburgh Sleep Quality Index — 7 composantes /21. Seuil mauvaise qualité > 5"}
    @classmethod
    def fields(cls): return [f"psqi_c{i}" for i in range(1,8)]+["psqi_total"]
    COMPS=["Qualité subjective du sommeil","Latence du sommeil","Durée du sommeil",
           "Efficacité habituelle du sommeil","Perturbations du sommeil",
           "Utilisation de somnifères","Dysfonctionnement diurne"]
    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">😴 PSQI — Qualité du sommeil</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Saisie directe des scores des 7 composantes (questionnaire papier PSQI). Chaque composante 0-3. Score ≤ 5 = bonne qualité.</div>', unsafe_allow_html=True)
        collected={}; total=0
        cols=st.columns(2)
        for i,comp in enumerate(self.COMPS):
            k=f"psqi_c{i+1}"
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=cols[i%2].selectbox(comp,[0,1,2,3],index=stored,
                format_func=lambda x:["0 — Très bon","1 — Assez bon","2 — Assez mauvais","3 — Très mauvais"][x],
                key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["psqi_total"]=total
        color="#388e3c" if total<=5 else "#d32f2f"
        msg="Bonne qualité" if total<=5 else "Mauvaise qualité"
        st.markdown(f'<div class="score-box" style="background:{color}">PSQI : {total}/21 — {msg}</div>',unsafe_allow_html=True)
        return collected
    @classmethod
    def score(cls,data):
        try: s=float(data.get("psqi_total",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=5 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/21","color":color,"details":{}}
    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("psqi_total",""))>=0
        except: return False
    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("psqi_total","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="PSQI",line=dict(color="#7F77DD",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=5,line_dash="dot",line_color="#d32f2f",annotation_text="Seuil mauvaise qualité >5")
        fig.update_layout(yaxis=dict(range=[0,22],title="PSQI /21"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l,"PSQI":r.get("psqi_total","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)
