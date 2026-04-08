"""tests/questionnaires/other_scores.py — IKDC, CSI, QBPDS, ATRS, WOSI"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


# ── IKDC ─────────────────────────────────────────────────────────────────────
@register_test
class QBPDS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"qbpds","nom":"QBPDS — Incapacité lombaire","tab_label":"📋 QBPDS","categorie":"questionnaire",
                "tags":["lombalgie","incapacité","dos","fonctionnel"],
                "description":"Quebec Back Pain Disability Scale — 20 items /100"}
    @classmethod
    def fields(cls): return [f"qbpds_q{i}" for i in range(1,21)]+["qbpds_score"]
    QBPDS_QUESTIONS=[
        "Se lever du lit","Rester au lit toute la nuit","Se retourner dans le lit",
        "Aller en voiture","Se tenir debout 20-30 min","S'asseoir dans une chaise 1h",
        "Monter une volée d'escaliers","Marcher 300-400 m","Marcher plusieurs kilomètres",
        "Atteindre les hautes étagères","Lancer un ballon","Courir 100 m",
        "Enlever la nourriture du réfrigérateur","Faire son lit","Mettre des chaussettes",
        "Se plier pour ramasser un objet","Tirer/pousser une porte","Porter deux sacs d'épicerie",
        "Soulever et porter une valise lourde","Porter un enfant",
    ]
    OPTS=["0 — Pas difficile","1 — Minimum","2 — Peu","3 — Modérément","4 — Très","5 — Extrêmement"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score QBPDS (/100)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📋 QBPDS — Incapacité lombaire</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">0 = pas difficile · 5 = extrêmement difficile. Score /100.</div>', unsafe_allow_html=True)
        collected={}; total=0
        cols=st.columns(2)
        for i,q in enumerate(self.QBPDS_QUESTIONS,1):
            k=f"qbpds_q{i}"
            raw=lv(k,None)
            try: stored=int(float(raw)) if raw not in (None,"","None") else 0
            except: stored=0
            val=cols[(i-1)%2].selectbox(q,list(range(6)),index=stored,format_func=lambda x:self.OPTS[x],key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["qbpds_score"]=total
        color="#388e3c" if total<=20 else "#f57c00" if total<=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">QBPDS : {total}/100</div>',unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls,data):
        try: s=float(data.get("qbpds_score",""))
        except: return {"score":None,"interpretation":"","color":"#888","details":{}}
        color="#388e3c" if s<=20 else "#f57c00" if s<=50 else "#d32f2f"
        return {"score":s,"interpretation":f"{s:.0f}/100","color":color,"details":{}}

    @classmethod
    def is_filled(cls,data):
        try: return float(data.get("qbpds_score",""))>=0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go; import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try: vals.append(float(row.get("qbpds_score","")))
            except: vals.append(None)
        fig=go.Figure(); xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="QBPDS",line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0,105],title="QBPDS /100"),height=280,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('qbpds', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        st.dataframe(pd.DataFrame([{"Bilan":l,"QBPDS":r.get("qbpds_score","—")} for l,(_,r) in zip(labels,bilans_df.iterrows())]),use_container_width=True,hide_index=True)


# ── ATRS Achilles Tendon Total Rupture Score ──────────────────────────────────