"""tests/questionnaires/other_scores.py — IKDC, CSI, QBPDS, ATRS, WOSI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── IKDC ─────────────────────────────────────────────────────────────────────
@register_test
class ATRS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"atrs","nom":"ATRS — Rupture tendon Achille","tab_label":"🦶 ATRS","categorie":"questionnaire",
                "tags":["achille","rupture","tendon","cheville","post-chirurgical"],
                "description":"Achilles Tendon Total Rupture Score — 10 items /100"}
    @classmethod
    def fields(cls): return [f"atrs_q{i}" for i in range(1,11)]+["atrs_score"]
    QUESTIONS=[
        "Limitation en raison de la faiblesse du tendon",
        "Limitation en raison de la fatigue du tendon",
        "Limitation en raison de la raideur du tendon",
        "Limitation en raison de la douleur",
        "Difficulté à marcher sur terrain inégal",
        "Difficulté à courir",
        "Difficulté à prendre le départ en sprint",
        "Difficulté à sauter",
        "Difficulté à pratiquer du sport",
        "Difficulté à pratiquer des activités physiques lourdes",
    ]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score ATRS (/100)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦶 ATRS — Tendon Achille (rupture)</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = limitation maximale · 10 = aucune limitation. Score /100.</div>', unsafe_allow_html=True)
        collected={}; total=0
        for i,q in enumerate(self.QUESTIONS,1):
            k=f"atrs_q{i}"
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 5
            except: v=5
            val=st.slider(q,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["atrs_score"]=total
        color="#388e3c" if total>=80 else "#f57c00" if total>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">ATRS : {total}/100</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("atrs_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s>=80 else "#f57c00" if s>=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("atrs_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("atrs_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="ATRS",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="ATRS /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('atrs', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"ATRS":r.get("atrs_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── WOSI Western Ontario Shoulder Instability ─────────────────────────────────