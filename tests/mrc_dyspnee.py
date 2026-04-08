"""
tests/mrc_dyspnee.py — MRC Dyspnée (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import MRC_GRADES


MRC_COLORS = ["#388e3c","#8bc34a","#f57c00","#e64a19","#d32f2f"]


@register_test
class MRCDyspnee(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"mrc_dyspnee","nom":"MRC Dyspnée","tab_label":"🚶 MRC Dyspnée",
                "categorie":"questionnaire","tags":["dyspnée", "respiratoire", "SHV", "BPCO", "essoufflement"],"description":"Échelle MRC dyspnée — 5 grades (0–4)"}

    @classmethod
    def fields(cls):
        return ["mrc_score"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "grade", "label": "Grade MRC (1-5)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🚶 Échelle de dyspnée MRC</div>',
                    unsafe_allow_html=True)

        mrc_opts_display = ["— Non renseigné —"] + [g[1] for g in MRC_GRADES]
        mrc_scores_map   = {g[1]: g[0] for g in MRC_GRADES}
        mrc_stored       = lv("mrc_score", None)
        mrc_stored_label = next(
            (g[1] for g in MRC_GRADES if str(g[0])==str(mrc_stored)), None
        ) if mrc_stored not in (None,"","0") else None
        mrc_default_idx  = mrc_opts_display.index(mrc_stored_label) if mrc_stored_label else 0

        mrc_chosen = st.radio("Grade MRC", mrc_opts_display,
                              index=mrc_default_idx, key=f"{key_prefix}_mrc_radio")

        if mrc_chosen == "— Non renseigné —":
            return {"mrc_score": ""}

        mrc_score_val = mrc_scores_map[mrc_chosen]
        st.markdown(
            f'<div class="score-box" style="background:{MRC_COLORS[mrc_score_val]};">'
            f'MRC Grade {mrc_score_val} / 4</div>',
            unsafe_allow_html=True)
        return {"mrc_score": mrc_score_val}

    @classmethod
    def score(cls, data):
        try:    g = int(float(data.get("mrc_score","")))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        return {"score":g,"interpretation":f"Grade {g}",
                "color":MRC_COLORS[min(g,4)],"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        return str(bilan_data.get("mrc_score","")).strip() not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("mrc_score",""))
                vals.append(None if math.isnan(f) else int(f))
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Bar(x=xp,y=yp,
                marker_color=[MRC_COLORS[min(v,4)] for v in yp],
                text=[f"Grade {v}" for v in yp],textposition="outside"))
        fig.add_hline(y=3,line_dash="dot",line_color="#d32f2f",
                      annotation_text="≥3 invalidité fonctionnelle",annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,5],title="Grade MRC",dtick=1),
                          height=320,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"Grade MRC":row.get("mrc_score","—"),
                 "Description":next((g[1] for g in MRC_GRADES
                     if str(g[0])==str(row.get("mrc_score",""))), "—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
