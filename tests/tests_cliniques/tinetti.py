"""tests/tests_partages/tinetti.py — Tinetti POMA (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import (
    TINETTI_EQUILIBRE, TINETTI_MARCHE, TINETTI_EQ_KEYS, TINETTI_MA_KEYS,
    TINETTI_EQ_MAX, TINETTI_MA_MAX, compute_tinetti
)

@register_test
class Tinetti(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tinetti","nom":"Tinetti — POMA","tab_label":"🏃 Tinetti",
                "categorie":"test_clinique","description":"Équilibre et marche /28, seuil risque chute < 24"}

    @classmethod
    def fields(cls):
        return (TINETTI_EQ_KEYS + TINETTI_MA_KEYS +
                ["tinetti_eq_score","tinetti_ma_score","tinetti_total","tinetti_interpretation"])

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">Tinetti — POMA</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Évaluation de l\'équilibre et de la marche. '
                    'Seuil de risque de chute : &lt; 24/28</div>', unsafe_allow_html=True)

        collected = {}
        tin_answers = {}

        def _radio_items(items, prefix):
            for key, label, options in items:
                stored = lv(key, "")
                opts_ext = ["— Non évalué —"] + [f"{s} — {d}" for s,d in options]
                stored_idx = 0
                if stored != "":
                    try:
                        s_int = int(float(stored))
                        stored_idx = next((i+1 for i,(s,_) in enumerate(options) if s==s_int), 0)
                    except: pass
                chosen = st.radio(label, opts_ext, index=stored_idx,
                                  key=f"{key_prefix}_{key}", horizontal=False)
                if chosen != "— Non évalué —":
                    score = int(chosen.split(" — ")[0])
                    tin_answers[key] = score
                    collected[key]   = score
                else:
                    collected[key] = ""

        st.markdown("**Partie A — Équilibre (0–16)**")
        _radio_items(TINETTI_EQUILIBRE, "eq")
        st.markdown("---")
        st.markdown("**Partie B — Marche (0–12)**")
        _radio_items(TINETTI_MARCHE, "ma")

        result = compute_tinetti(tin_answers)
        if result["total"] is not None:
            st.markdown("---")
            eq_s = f"{result['eq']}/{TINETTI_EQ_MAX}" if result['eq'] is not None else "—"
            ma_s = f"{result['ma']}/{TINETTI_MA_MAX}" if result['ma'] is not None else "—"
            st.markdown(
                f'<div class="score-box" style="background:{result["color"]};">'
                f'Tinetti : {result["total"]}/28 — {result["interpretation"]}'
                f'  <small>(Équilibre : {eq_s} · Marche : {ma_s})</small></div>',
                unsafe_allow_html=True)
        collected.update({
            "tinetti_eq_score":      result["eq"] if result["eq"] is not None else "",
            "tinetti_ma_score":      result["ma"] if result["ma"] is not None else "",
            "tinetti_total":         result["total"] if result["total"] is not None else "",
            "tinetti_interpretation":result["interpretation"],
        })
        return collected

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("tinetti_total",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        color = "#d32f2f" if s<19 else "#f57c00" if s<24 else "#388e3c"
        return {"score":s,"interpretation":data.get("tinetti_interpretation",""),
                "color":color,"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("tinetti_total","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("tinetti_total",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Tinetti /28",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}/28" for v in yp],textposition="top center"))
        for y,color,label in [(19,"#d32f2f","< 19 risque élevé"),(24,"#f57c00","< 24 risque modéré")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,30],title="Score /28"),height=350,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"Tinetti /28":row.get("tinetti_total","—"),
                 "Interprétation":row.get("tinetti_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
