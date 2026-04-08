"""
tests/questionnaires/sf12.py — SF-12 (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import (
    SF12_QUESTIONS, SF12_DIMENSIONS, compute_sf12_scores, interpret_pcs_mcs
)


def _pcs_mcs_color(s):
    if s is None: return "#888"
    if s >= 55:   return "#388e3c"
    if s >= 45:   return "#2196f3"
    if s >= 35:   return "#f57c00"
    return "#d32f2f"


def _sb(label, options, default, key):
    """Selectbox avec option vide en premier."""
    opts_labels = ["— Non renseigné —"] + [l for _,l in options]
    opts_scores = [None] + [s for s,_ in options]
    try:    stored = int(float(default)) if default not in (None,"","None") else None
    except: stored = None
    idx = opts_scores.index(stored) if stored in opts_scores else 0
    chosen_label = st.selectbox(label, opts_labels, index=idx, key=key)
    chosen_idx   = opts_labels.index(chosen_label)
    return opts_scores[chosen_idx]


@register_test
class SF12(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"sf12","nom":"SF-12","tab_label":"📊 SF-12",
                "categorie":"questionnaire","tags":["qualité de vie", "fonctionnel", "santé", "générique"],
                "description":"SF-12 Health Survey — PCS et MCS /100, référence population = 50",
                "has_fixed_pdf": True}

    @classmethod
    def fields(cls):
        return ([f"sf12_{q['key']}" for q in SF12_QUESTIONS]
                + [f"sf12_{k}" for k in SF12_DIMENSIONS.keys()])

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "pcs", "label": "PCS — Santé physique", "default": True},
            {"key": "mcs", "label": "MCS — Santé mentale", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">📊 SF-12 — Qualité de vie</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">12 questions mesurant 8 dimensions de la qualité de vie, '
            'et deux scores composites : <strong>PCS-12</strong> (physique) et <strong>MCS-12</strong> (mental). '
            'Score de référence = 50 (moyenne population générale).</div>',
            unsafe_allow_html=True)

        sf_ans    = {}
        last_intro = None
        for q in SF12_QUESTIONS:
            key     = q["key"]
            options = q["options"]
            intro   = q.get("intro")
            if intro and intro != last_intro:
                st.markdown(f"---\n*{intro}*")
                last_intro = intro
            sf_ans[key] = _sb(q["texte"], options,
                               default=lv(f"sf12_{key}", None),
                               key=f"{key_prefix}_sf12_{key}")

        sf_scores = compute_sf12_scores(sf_ans)
        st.markdown("---")
        st.markdown("#### 📊 Résultats SF-12")
        cp1, cp2 = st.columns(2)
        with cp1:
            pcs = sf_scores.get("pcs")
            st.markdown(
                f'<div class="score-box" style="background:{_pcs_mcs_color(pcs)};">'
                f'PCS-12 : {pcs if pcs is not None else "—"}<br>'
                f'<small style="font-size:.75rem">Score composite physique<br>'
                f'{interpret_pcs_mcs(pcs)}</small></div>',
                unsafe_allow_html=True)
        with cp2:
            mcs = sf_scores.get("mcs")
            st.markdown(
                f'<div class="score-box" style="background:{_pcs_mcs_color(mcs)};">'
                f'MCS-12 : {mcs if mcs is not None else "—"}<br>'
                f'<small style="font-size:.75rem">Score composite mental<br>'
                f'{interpret_pcs_mcs(mcs)}</small></div>',
                unsafe_allow_html=True)

        # Graphique 8 dimensions
        import plotly.graph_objects as go
        dim_keys  = ["pf","rp","bp","gh","vt","sf","re","mh"]
        dim_labels = [SF12_DIMENSIONS[k] for k in dim_keys]
        scores_vals = [sf_scores.get(k) or 0 for k in dim_keys]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dim_labels, y=scores_vals,
            marker_color=["#388e3c" if s>=66 else "#f57c00" if s>=33 else "#d32f2f"
                          for s in scores_vals],
            text=[f"{s}" for s in scores_vals], textposition="outside"))
        fig.update_layout(yaxis=dict(range=[0,115],title="Score (0–100)"),
                          xaxis_tickangle=-30, height=360,
                          margin=dict(t=20,b=80), plot_bgcolor="white")
        fig.add_hline(y=50, line_dash="dot", line_color="grey",
                      annotation_text="50 (référence)", annotation_position="right")
        st.plotly_chart(fig, use_container_width=True)

        collected = {f"sf12_{k}": v if v is not None else "" for k,v in sf_ans.items()}
        for k,v in sf_scores.items():
            collected[f"sf12_{k}"] = v if v is not None else ""
        return collected

    @classmethod
    def score(cls, data):
        try:    pcs = float(data.get("sf12_pcs",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        try:    mcs = float(data.get("sf12_mcs",""))
        except: mcs = None
        return {"score":pcs,"interpretation":f"PCS:{pcs}  MCS:{mcs}",
                "color":_pcs_mcs_color(pcs),"details":{"pcs":pcs,"mcs":mcs}}

    @classmethod
    def is_filled(cls, bilan_data):
        return str(bilan_data.get("sf12_pcs","")).strip() not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key, label, color in [
            ("sf12_pcs","PCS — Physique","#2B57A7"),
            ("sf12_mcs","MCS — Mental","#C4603A"),
        ]:
            vals = []
            for _,row in bilans_df.iterrows():
                try:    vals.append(float(row.get(key,"")))
                except: vals.append(None)
            xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
            yp = [v for v in vals if v is not None and v==v]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=label,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[f"{v:.0f}" for v in yp],textposition="top center"))
        fig.add_hline(y=50,line_dash="dot",line_color="#388e3c",
                      annotation_text="Moyenne population (50)",annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="Score /100"),height=350,
                          legend=dict(orientation="h",y=-0.2),
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"PCS /100":row.get("sf12_pcs","—"),"MCS /100":row.get("sf12_mcs","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
