"""tests/questionnaires/psfs.py — PSFS (Patient-Specific Functional Scale)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


@register_test
class PSFS(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "psfs", "nom": "PSFS — Échelle fonctionnelle spécifique",
            "tab_label": "🎯 PSFS",
            "categorie": "questionnaire",
            "tags": ["fonctionnel", "spécifique patient", "universel", "activité"],
            "description": "Patient-Specific Functional Scale — 3 à 5 activités limitées, cotées 0–10",
        }

    @classmethod
    def fields(cls):
        fields = []
        for i in range(1, 6):
            fields += [f"psfs_activite_{i}", f"psfs_score_{i}"]
        return fields + ["psfs_score_moyen"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_moyen", "label": "Score moyen (/10)", "default": True},
            {"key": "activites", "label": "Activités et scores", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🎯 PSFS — Échelle fonctionnelle spécifique</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Demandez au patient de nommer 3 à 5 activités difficiles à réaliser. '
            'Coter chaque activité de 0 (incapable) à 10 (niveau habituel).</div>',
            unsafe_allow_html=True)

        collected = {}
        scores = []
        for i in range(1, 6):
            act_key   = f"psfs_activite_{i}"
            score_key = f"psfs_score_{i}"
            c1, c2 = st.columns([3, 1])
            act = c1.text_input(f"Activité {i}", value=lv(act_key, ""),
                                key=f"{key_prefix}_psfs_act_{i}",
                                placeholder=f"ex: monter les escaliers" if i == 1 else "")
            raw = lv(score_key, None)
            try:    default_score = int(float(raw)) if raw not in (None, "", "None") else None
            except: default_score = None
            score = c2.number_input(f"Score {i}", min_value=0, max_value=10,
                                    value=default_score, step=1,
                                    key=f"{key_prefix}_psfs_score_{i}",
                                    label_visibility="collapsed")
            collected[act_key]   = act
            collected[score_key] = score if score is not None else ""
            if act.strip() and score is not None:
                scores.append(score)

        if scores:
            moyen = round(sum(scores) / len(scores), 1)
            collected["psfs_score_moyen"] = moyen
            color = "#388e3c" if moyen >= 7 else "#f57c00" if moyen >= 4 else "#d32f2f"
            st.markdown(
                f'<div class="score-box" style="background:{color}">'
                f'Score PSFS moyen : {moyen}/10<br>'
                f'<small style="font-size:.75rem">{len(scores)} activité(s) évaluée(s)</small></div>',
                unsafe_allow_html=True)
        else:
            collected["psfs_score_moyen"] = ""

        return collected

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("psfs_score_moyen", ""))
        except: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        color = "#388e3c" if s >= 7 else "#f57c00" if s >= 4 else "#d32f2f"
        return {"score": s, "interpretation": f"{s}/10", "color": color, "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        try:    return float(bilan_data.get("psfs_score_moyen", "")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        vals = []
        for _, row in bilans_df.iterrows():
            try:    vals.append(float(row.get("psfs_score_moyen", "")))
            except: vals.append(None)
        xp = [labels[i] for i, v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                name="PSFS", line=dict(color="#2B57A7", width=2.5),
                marker=dict(size=9),
                text=[f"{v}/10" for v in yp], textposition="top center"))
        fig.add_hline(y=6, line_dash="dot", line_color="#f57c00",
                      annotation_text="Seuil minimal détectable", annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0, 11], title="Score /10"),
                          height=300, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('psfs', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "PSFS moyen", "col_key": "psfs_score_moyen",
             "values": [r.get("psfs_score_moyen","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan": lbl, "PSFS moyen": row.get("psfs_score_moyen", "—")}
                            for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
