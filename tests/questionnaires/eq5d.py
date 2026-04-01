"""tests/questionnaires/eq5d.py — EQ-5D-3L (qualité de vie générique)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

EQ5D_DIMS = [
    ("eq5d_mobilite",    "Mobilité",
     ["Aucun problème pour marcher",
      "Quelques problèmes pour marcher",
      "Incapable de marcher"]),
    ("eq5d_autonomie",   "Autonomie de soin",
     ["Aucun problème pour me laver ou m'habiller",
      "Quelques problèmes pour me laver ou m'habiller",
      "Incapable de me laver ou m'habiller"]),
    ("eq5d_activites",   "Activités courantes",
     ["Aucun problème pour mes activités courantes",
      "Quelques problèmes pour mes activités courantes",
      "Incapable de faire mes activités courantes"]),
    ("eq5d_douleur",     "Douleur / gêne",
     ["Aucune douleur ni gêne",
      "Douleur ou gêne modérée",
      "Douleur ou gêne extrême"]),
    ("eq5d_anxiete",     "Anxiété / dépression",
     ["Pas anxieux ni déprimé",
      "Modérément anxieux ou déprimé",
      "Extrêmement anxieux ou déprimé"]),
]


@register_test
class EQ5D(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "eq5d", "nom": "EQ-5D — Qualité de vie",
            "tab_label": "🌡️ EQ-5D",
            "categorie": "questionnaire",
            "tags": ["qualité de vie", "générique", "universel", "santé globale"],
            "description": "EQ-5D-3L — 5 dimensions de santé + VAS 0–100",
        }

    @classmethod
    def fields(cls):
        return [d[0] for d in EQ5D_DIMS] + ["eq5d_vas", "eq5d_index"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🌡️ EQ-5D — Qualité de vie</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Pour chaque domaine, cochez la case qui décrit '
            'le mieux votre état de santé AUJOURD\'HUI.</div>', unsafe_allow_html=True)

        collected = {}
        dim_scores = []
        for field, label, opts in EQ5D_DIMS:
            raw = lv(field, None)
            try:    stored = int(float(raw)) if raw not in (None, "", "None") else 1
            except: stored = 1
            stored = max(1, min(3, stored))
            opts_ext = [None] + list(range(1, 4))
            chosen = st.radio(
                f"**{label}**", options=opts_ext,
                format_func=lambda x, o=opts: "— Non renseigné —" if x is None else f"{x} — {o[x-1]}",
                index=stored, horizontal=False,
                key=f"{key_prefix}_{field}")
            val = chosen if chosen is not None else 1
            collected[field] = val
            dim_scores.append(val)

        st.markdown("---")
        st.markdown("**Votre état de santé AUJOURD'HUI (0 = pire état, 100 = meilleur état imaginable)**")
        raw_vas = lv("eq5d_vas", None)
        try:    default_vas = int(float(raw_vas)) if raw_vas not in (None, "", "None") else 50
        except: default_vas = 50
        vas = st.slider("VAS EQ-5D", 0, 100, default_vas, key=f"{key_prefix}_eq5d_vas")
        collected["eq5d_vas"] = vas

        # Index simple (somme inversée, indicatif)
        idx = round(1 - (sum(dim_scores) - 5) / 10, 2)
        collected["eq5d_index"] = idx

        color = "#388e3c" if idx >= 0.8 else "#f57c00" if idx >= 0.5 else "#d32f2f"
        st.markdown(
            f'<div class="score-box" style="background:{color}">'
            f'Index EQ-5D : {idx:.2f} | VAS : {vas}/100</div>',
            unsafe_allow_html=True)
        return collected

    @classmethod
    def score(cls, data):
        try:    idx = float(data.get("eq5d_index", ""))
        except: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        vas = data.get("eq5d_vas", "—")
        color = "#388e3c" if idx >= 0.8 else "#f57c00" if idx >= 0.5 else "#d32f2f"
        return {"score": idx, "interpretation": f"Index {idx:.2f} | VAS {vas}/100",
                "color": color, "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        try:    return float(bilan_data.get("eq5d_index", "")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key, label, color in [("eq5d_index", "Index EQ-5D", "#2B57A7"),
                                   ("eq5d_vas", "VAS /100 (÷10)", "#1D9E75")]:
            vals = []
            for _, row in bilans_df.iterrows():
                try:
                    v = float(row.get(key, ""))
                    vals.append(v / 10 if key == "eq5d_vas" else v)
                except: vals.append(None)
            xp = [labels[i] for i, v in enumerate(vals) if v is not None]
            yp = [v for v in vals if v is not None]
            if xp:
                fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                    name=label, line=dict(color=color, width=2.5),
                    marker=dict(size=9),
                    text=[f"{v:.2f}" for v in yp], textposition="top center"))
        fig.update_layout(yaxis=dict(range=[0, 1.05], title="Index (0–1)"),
                          height=300, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        rows = [{"Bilan": lbl, "Index": row.get("eq5d_index", "—"), "VAS": row.get("eq5d_vas", "—")}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
