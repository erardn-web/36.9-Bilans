"""
tests/questionnaires/nijmegen.py — Nijmegen (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import (
    NIJMEGEN_ITEMS, NIJMEGEN_OPTIONS, NIJMEGEN_KEYS, compute_nijmegen
)


@register_test
class Nijmegen(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"nijmegen","nom":"Questionnaire de Nijmegen","tab_label":"📋 Nijmegen",
                "categorie":"questionnaire","tags":["hyperventilation", "SHV", "respiratoire", "dyspnée", "anxiété"],
                "description":"16 items /64, seuil SHV ≥ 23"}

    @classmethod
    def fields(cls):
        return NIJMEGEN_KEYS + ["nij_score","nij_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📋 Questionnaire de Nijmegen</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">16 symptômes cotés de 0 (jamais) à 4 (très souvent). '
            'Score ≥ 23 : SHV probable · 15–22 : borderline · &lt; 15 : peu probable.</div>',
            unsafe_allow_html=True)

        nij_answers = {}
        opts_extended = [None] + [o[0] for o in NIJMEGEN_OPTIONS]

        def _nij_fmt(x, opts=NIJMEGEN_OPTIONS):
            if x is None: return "— Non renseigné —"
            return next(l for s,l in opts if s==x)

        for i, item in enumerate(NIJMEGEN_ITEMS):
            key = f"nij_{i+1}"
            val = lv(key, None)
            try:    stored_score = int(float(val)) if val not in (None,"","None") else None
            except: stored_score = None
            default_idx = opts_extended.index(stored_score) if stored_score in opts_extended else 0
            chosen = st.radio(
                f"{i+1}. {item}", options=opts_extended,
                format_func=_nij_fmt,
                index=default_idx, horizontal=True,
                key=f"{key_prefix}_nij_{i+1}",
            )
            if chosen is not None:
                nij_answers[key] = chosen

        nij_result = compute_nijmegen(nij_answers)
        st.markdown("---")
        if nij_result["score"] is not None:
            st.markdown(
                f'<div class="score-box" style="background:{nij_result["color"]};">'
                f'Score Nijmegen : {nij_result["score"]} / 64<br>'
                f'<small style="font-size:.8rem">{nij_result["interpretation"]}</small></div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">Remplissez les items pour calculer le score.</div>',
                        unsafe_allow_html=True)

        collected = {}
        for k,v in nij_answers.items():
            collected[k] = v
        for k in NIJMEGEN_KEYS:
            if k not in collected:
                collected[k] = ""
        collected["nij_score"]          = nij_result["score"] if nij_result["score"] is not None else ""
        collected["nij_interpretation"] = nij_result["interpretation"]
        return collected

    @classmethod
    def score(cls, data):
        try:    s = int(float(data.get("nij_score","")))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        color = "#d32f2f" if s>=23 else "#f57c00" if s>=15 else "#388e3c"
        interp = ("Positif ≥ 23" if s>=23 else "Borderline 15–22" if s>=15 else "Négatif < 15")
        return {"score":s,"interpretation":interp,"color":color,"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        try:
            s = float(bilan_data.get("nij_score",""))
            return s > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("nij_score",""))
                vals.append(None if math.isnan(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Nijmegen /64",
                line=dict(color="#C4603A",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}/64" for v in yp if v is not None and v==v],textposition="top center"))
        fig.add_hline(y=23,line_dash="dot",line_color="#f57c00",
                      annotation_text="Seuil SHV (23)",annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,66],title="Score /64"),height=350,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"Score /64":row.get("nij_score","—"),
                 "Interprétation":row.get("nij_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
