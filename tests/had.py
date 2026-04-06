"""
tests/questionnaires/had.py — HAD (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import HAD_QUESTIONS, compute_had_scores


def _had_color(s):
    if s <= 7:  return "#388e3c"
    if s <= 10: return "#f57c00"
    return "#d32f2f"


@register_test
class HAD(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"had","nom":"HAD — Anxiété & Dépression","tab_label":"😟 HAD",
                "categorie":"questionnaire","tags":["anxiété", "dépression", "psychologique", "humeur"],
                "description":"Hospital Anxiety and Depression Scale — 14 items /21","has_fixed_pdf":True}

    @classmethod
    def fields(cls):
        return ([f"had_{k}" for k,*_ in HAD_QUESTIONS]
                + ["had_score_anxiete","had_score_depression"])

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">😟 Échelle HAD — Anxiété & Dépression</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Questionnaire auto-rapporté de 14 items. '
            'Score 0–7 : normal · 8–10 : douteux · 11–21 : pathologique</div>',
            unsafe_allow_html=True)

        had_answers = {}
        for key, subscale, question, options in HAD_QUESTIONS:
            label = f"({'A' if subscale == 'A' else 'D'}) {question}"
            val   = lv(f"had_{key}", None)
            scores_list   = [o[0] for o in options]
            opts_extended = [None] + scores_list
            def _fmt_had(x, opts=options):
                if x is None: return "— Non renseigné —"
                return next(l for s,l in opts if s==x)
            try:    stored_int = int(float(val)) if val not in (None,"","None") else None
            except: stored_int = None
            default_idx = opts_extended.index(stored_int) if stored_int in opts_extended else 0
            chosen = st.radio(
                label, options=opts_extended,
                format_func=_fmt_had,
                index=default_idx, horizontal=True,
                key=f"{key_prefix}_had_{key}",
            )
            if chosen is not None:
                had_answers[key] = chosen

        had_scores = compute_had_scores({k: v for k,v in had_answers.items() if v is not None})
        st.markdown("---")
        st.markdown("#### 📊 Résultats HAD")
        ca, cd = st.columns(2)
        with ca:
            st.markdown(
                f'<div class="score-box" style="background:{_had_color(had_scores["score_anxiete"])};">'
                f'Anxiété : {had_scores["score_anxiete"]}/21<br>'
                f'<small style="font-size:.75rem">{had_scores["interp_anxiete"]}</small></div>',
                unsafe_allow_html=True)
        with cd:
            st.markdown(
                f'<div class="score-box" style="background:{_had_color(had_scores["score_depression"])};">'
                f'Dépression : {had_scores["score_depression"]}/21<br>'
                f'<small style="font-size:.75rem">{had_scores["interp_depression"]}</small></div>',
                unsafe_allow_html=True)

        collected = {f"had_{key}": had_answers[key] for key in had_answers}
        collected["had_score_anxiete"]    = had_scores["score_anxiete"]
        collected["had_score_depression"] = had_scores["score_depression"]
        return collected

    @classmethod
    def score(cls, data):
        try:    sa = int(float(data.get("had_score_anxiete","")))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        try:    sd = int(float(data.get("had_score_depression","")))
        except: sd = None
        worst = max(sa, sd or 0)
        return {"score":worst,"interpretation":f"A:{sa}/21  D:{sd}/21",
                "color":_had_color(worst),"details":{"anxiete":sa,"depression":sd}}

    @classmethod
    def is_filled(cls, bilan_data):
        try:
            s = float(bilan_data.get("had_score_anxiete",""))
            return s > 0  # Score 0 = aucune réponse ou tout à 0 explicitement
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key, label, color in [
            ("had_score_anxiete","Anxiété","#f57c00"),
            ("had_score_depression","Dépression","#2B57A7"),
        ]:
            vals = []
            for _, row in bilans_df.iterrows():
                try:    vals.append(float(row.get(key,"")))
                except: vals.append(None)
            xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
            yp = [v for v in vals if v is not None and v==v]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=label,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[f"{v:.0f}/21" for v in yp if v is not None and v==v],textposition="top center"))
        for y,color,label in [(7,"#388e3c","Normal ≤7"),(10,"#f57c00","Douteux ≤10")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,22],title="Score /21"),height=380,
                          legend=dict(orientation="h",y=-0.2),
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"Anxiété /21":row.get("had_score_anxiete","—"),
                 "Dépression /21":row.get("had_score_depression","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
