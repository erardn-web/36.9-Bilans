"""
tests/tests_cliniques/bolt.py — BOLT (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import BOLT_DESCRIPTION, interpret_bolt


def _safe_float(v):
    try: return float(v)
    except: return None


@register_test
class BOLT(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"bolt","nom":"Test BOLT","tab_label":"⏱️ BOLT",
                "categorie":"test_clinique",
                "description":"Body Oxygen Level Test — apnée après expiration normale"}

    @classmethod
    def fields(cls):
        return ["bolt_score","bolt_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">⏱️ BOLT – Body Oxygen Level Test</div>',
                    unsafe_allow_html=True)
        st.markdown(BOLT_DESCRIPTION)

        stored = lv("bolt_score", None)
        try:    default_val = int(float(stored)) if stored not in (None,"","None") else None
        except: default_val = None

        bolt_val = st.number_input(
            "Résultat BOLT (secondes)",
            min_value=0, max_value=120,
            value=default_val,
            help="Laisser à 0 si non réalisé",
            step=1, key=f"{key_prefix}_bolt_input",
        )

        collected = {"bolt_score":"","bolt_interpretation":""}
        if bolt_val is not None and bolt_val > 0:
            interp = interpret_bolt(bolt_val)
            st.markdown(
                f'<div class="score-box" style="background:{interp["color"]};">'
                f'{bolt_val} s — {interp["cat"]}<br>'
                f'<small style="font-size:.8rem">{interp["desc"]}</small></div>',
                unsafe_allow_html=True)
            collected["bolt_score"]          = bolt_val
            collected["bolt_interpretation"] = interp["cat"]

        return collected

    @classmethod
    def score(cls, data):
        try:    s = int(float(data.get("bolt_score","")))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        if s <= 0: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        interp = interpret_bolt(s)
        return {"score":s,"interpretation":interp.get("cat",""),
                "color":interp.get("color","#888"),"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        v = bilan_data.get("bolt_score","")
        try: return int(float(v)) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("bolt_score",""))
                vals.append(None if math.isnan(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v > 0]
        yp = [v for v in vals if v is not None and v > 0]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="BOLT (s)",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}s" for v in yp if v is not None and v==v],textposition="top center"))
        for y,color,label in [(10,"#d32f2f","< 10s très bas"),(20,"#f57c00","20s"),(40,"#388e3c","40s bon")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,max(max(yp or [0])+10,50)],title="Secondes"),
                          height=350,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"BOLT (s)":row.get("bolt_score","—"),
                 "Interprétation":row.get("bolt_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
