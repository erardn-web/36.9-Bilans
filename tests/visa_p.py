"""tests/questionnaires/visa_scales.py — VISA-A, VISA-P, VISA-H, VISA-G (tendinopathies)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


class _VISABase(BaseTest):
    _PREFIX = ""
    _TITLE = ""
    _QUESTIONS = []
    _REGION = ""

    def _q(self, lv, key_prefix, idx, label, qtype, opts=None):
        k = f"{self._PREFIX}_q{idx}"
        raw = lv(k, None)
        if qtype == "slider":
            try: v = int(float(raw)) if raw not in (None, "", "None") else 0
            except: v = 0
            val = st.slider(label, 0, 10, v, key=f"{key_prefix}_{k}")
        elif qtype == "select":
            try: stored = int(float(raw)) if raw not in (None, "", "None") else 0
            except: stored = 0
            opts_full = [None] + list(opts.keys())
            chosen = st.selectbox(label, opts_full,
                format_func=lambda x: "— Choisir —" if x is None else opts[x],
                index=(list(opts.keys()).index(stored)+1) if stored in opts else 0,
                key=f"{key_prefix}_{k}")
            val = chosen if chosen is not None else 0
        return k, val

    @classmethod
    def score(cls, data):
        total = 0
        for i in range(1, len(cls._QUESTIONS)+1):
            try: total += float(data.get(f"{cls._PREFIX}_q{i}", 0) or 0)
            except: pass
        s = round(total)
        color = "#388e3c" if s >= 80 else "#f57c00" if s >= 50 else "#d32f2f"
        return {"score": s, "interpretation": f"{s}/100", "color": color, "details": {}}

    @classmethod
    def is_filled(cls, data):
        try: return float(data.get(f"{cls._PREFIX}_score", "")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go; import pandas as pd
        vals = []
        for _, row in bilans_df.iterrows():
            try: vals.append(float(row.get(f"{cls._PREFIX}_score", "")))
            except: vals.append(None)
        fig = go.Figure()
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]; yp=[v for v in vals if v is not None]
        if xp: fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text", name=cls._PREFIX.upper(),
            line=dict(color="#2B57A7", width=2.5), marker=dict(size=9),
            text=[f"{v:.0f}" for v in yp], textposition="top center"))
        fig.add_hline(y=80, line_dash="dot", line_color="#388e3c", annotation_text="Seuil bon ≥80")
        fig.update_layout(yaxis=dict(range=[0, 105], title="Score /100"), height=300,
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(pd.DataFrame([{"Bilan":l, cls._PREFIX.upper(): r.get(f"{cls._PREFIX}_score","—")}
            for l,(_,r) in zip(labels, bilans_df.iterrows())]), use_container_width=True, hide_index=True)


@register_test
class VISAP(_VISABase):
    _PREFIX = "visa_p"
    @classmethod
    def meta(cls):
        return {"id":"visa_p","nom":"VISA-P — Tendinopathie rotulienne","tab_label":"🦵 VISA-P","categorie":"questionnaire",
                "tags":["genou","rotule","tendinopathie","sport"],
                "description":"VISA-P — Victorian Institute of Sport Assessment Patellar — /100"}
    @classmethod
    def fields(cls):
        return [f"visa_p_q{i}" for i in range(1,9)]+["visa_p_score"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score VISA-P (/100)", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🦵 VISA-P — Tendinopathie rotulienne</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Score 0 = incapacité totale · 100 = asymptomatique</div>', unsafe_allow_html=True)
        collected={}; total=0
        q_labels = [
            "Douleur assise pendant 10 min",
            "Douleur en descendant les escaliers",
            "Douleur complètement accroupi", "Douleur en sautant",
            "Douleur pendant l'activité sportive","Douleur après l'activité",
            "Niveaux d'activité complets","Pratique sportive sans douleur (semaines)",
        ]
        for i,label in enumerate(q_labels,1):
            k=f"visa_p_q{i}"
            raw=lv(k,None)
            try: v=int(float(raw)) if raw not in (None,"","None") else 0
            except: v=0
            val=st.slider(label,0,10,v,key=f"{key_prefix}_{k}")
            collected[k]=val; total+=val
        collected["visa_p_score"]=min(total,100)
        color="#388e3c" if total>=80 else "#f57c00" if total>=50 else "#d32f2f"
        st.markdown(f'<div class="score-box" style="background:{color}">VISA-P : {min(total,100)}/100</div>',unsafe_allow_html=True)
        return collected

