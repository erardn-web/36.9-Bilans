"""tests/tests_cliniques/mmrc.py — mMRC Dyspnée BPCO (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

MMRC_GRADES = [
    (0,"Grade 0 — Dyspnée seulement lors d'exercice intense"),
    (1,"Grade 1 — Dyspnée en montant une côte ou une légère pente"),
    (2,"Grade 2 — Marche plus lentement que les autres ou s'arrête après ~100 m à plat"),
    (3,"Grade 3 — S'arrête pour souffler après quelques minutes ou ~100 m à plat"),
    (4,"Grade 4 — Trop essoufflé pour quitter la maison ou s'habiller/déshabiller"),
]
MMRC_COLORS = ["#388e3c","#8bc34a","#f57c00","#e64a19","#d32f2f"]

@register_test
class MMRC(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"mmrc","nom":"mMRC Dyspnée","tab_label":"😮‍💨 mMRC",
                "categorie":"test_clinique","tags":["BPCO", "dyspnée", "respiratoire"],"description":"Modified MRC Dyspnoea Scale grade 0–4"}

    @classmethod
    def fields(cls):
        return ["mmrc_grade"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">mMRC — Dyspnée</div>', unsafe_allow_html=True)
        opts = ["— Non renseigné —"] + [d for _,d in MMRC_GRADES]
        stored = lv("mmrc_grade","")
        idx = 0
        if stored != "":
            try: idx = int(float(stored)) + 1
            except: pass
        chosen = st.radio("Grade mMRC", opts, index=idx, key=f"{key_prefix}_mmrc")
        mmrc_val = ""
        if chosen != "— Non renseigné —":
            mmrc_val = int(chosen.split(" ")[1])
            st.markdown(f'<div class="score-box" style="background:{MMRC_COLORS[mmrc_val]};">'
                        f'mMRC Grade {mmrc_val}</div>', unsafe_allow_html=True)
        return {"mmrc_grade": mmrc_val}

    @classmethod
    def is_filled(cls, bilan_data):
        v = str(bilan_data.get("mmrc_grade","")).strip()
        return v not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            v = str(row.get("mmrc_grade","")).strip()
            try: vals.append(int(float(v)) if v not in ("","None","nan") else None)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="mMRC",
                line=dict(color="#C4603A",width=2.5),marker=dict(size=9),
                text=[f"Grade {v}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[-0.5,4.5],tickvals=[0,1,2,3,4],title="Grade"),
                          height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows=[{"Bilan":lbl,"mMRC Grade":row.get("mmrc_grade","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
