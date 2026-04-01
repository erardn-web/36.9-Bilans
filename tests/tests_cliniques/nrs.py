"""tests/tests_cliniques/nrs.py — NRS universel (Numeric Rating Scale douleur)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test


@register_test
class NRS(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id": "nrs", "nom": "NRS — Douleur numérique",
            "tab_label": "🔢 NRS",
            "categorie": "test_clinique",
            "tags": ["douleur", "NRS", "universel", "toutes pathologies"],
            "description": "Numeric Rating Scale — douleur repos/mouvement/nuit, universel",
        }

    @classmethod
    def fields(cls):
        return ["nrs_repos", "nrs_mouvement", "nrs_nuit", "nrs_region", "nrs_notes"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🔢 NRS — Échelle numérique de la douleur</div>',
                    unsafe_allow_html=True)

        def _default(key):
            v = lv(key, None)
            if v is None or str(v).strip() in ("", "None"): return "—"
            try: return int(float(v))
            except: return "—"

        OPTS = ["—"] + list(range(11))

        c1, c2 = st.columns(2)
        with c1:
            nrs_r = st.select_slider("Douleur au repos (0–10)", options=OPTS,
                                     value=_default("nrs_repos"),
                                     format_func=lambda x: "Non renseigné" if x == "—" else str(x),
                                     key=f"{key_prefix}_nrs_r")
            nrs_m = st.select_slider("Douleur au mouvement (0–10)", options=OPTS,
                                     value=_default("nrs_mouvement"),
                                     format_func=lambda x: "Non renseigné" if x == "—" else str(x),
                                     key=f"{key_prefix}_nrs_m")
            nrs_n = st.select_slider("Douleur la nuit (0–10)", options=OPTS,
                                     value=_default("nrs_nuit"),
                                     format_func=lambda x: "Non renseigné" if x == "—" else str(x),
                                     key=f"{key_prefix}_nrs_n")

            def ec(s): return "#388e3c" if s <= 3 else "#f57c00" if s <= 6 else "#d32f2f"
            for lbl, val in [("Repos", nrs_r), ("Mouvement", nrs_m), ("Nuit", nrs_n)]:
                if val != "—":
                    st.markdown(f'<small style="color:{ec(val)}">● NRS {lbl} : <b>{val}/10</b></small>',
                                unsafe_allow_html=True)
        with c2:
            region = st.text_input("Région / localisation",
                                   value=lv("nrs_region", ""),
                                   key=f"{key_prefix}_nrs_region",
                                   placeholder="ex: épaule droite, genou gauche…")
            notes = st.text_area("Observations", value=lv("nrs_notes", ""),
                                 height=120, key=f"{key_prefix}_nrs_notes")

        return {
            "nrs_repos":     "" if nrs_r == "—" else nrs_r,
            "nrs_mouvement": "" if nrs_m == "—" else nrs_m,
            "nrs_nuit":      "" if nrs_n == "—" else nrs_n,
            "nrs_region":    region,
            "nrs_notes":     notes,
        }

    @classmethod
    def score(cls, data):
        vals = []
        for k in ("nrs_repos", "nrs_mouvement", "nrs_nuit"):
            try:
                v = str(data.get(k, "")).strip()
                if v not in ("", "None", "nan", "—"):
                    vals.append(int(float(v)))
            except: pass
        if not vals: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        worst = max(vals)
        def ec(s): return "#388e3c" if s <= 3 else "#f57c00" if s <= 6 else "#d32f2f"
        return {"score": worst, "interpretation": f"Max {worst}/10",
                "color": ec(worst), "details": {}}

    @classmethod
    def is_filled(cls, bilan_data):
        for k in ("nrs_repos", "nrs_mouvement", "nrs_nuit"):
            v = str(bilan_data.get(k, "")).strip()
            if v not in ("", "None", "nan", "—"): return True
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key, label, color in [("nrs_repos", "Repos", "#2B57A7"),
                                    ("nrs_mouvement", "Mouvement", "#C4603A"),
                                    ("nrs_nuit", "Nuit", "#7B1FA2")]:
            vals = []
            for _, row in bilans_df.iterrows():
                v = str(row.get(key, "")).strip()
                try:    vals.append(int(float(v)) if v not in ("", "None", "nan", "—") else None)
                except: vals.append(None)
            xp = [labels[i] for i, v in enumerate(vals) if v is not None]
            yp = [v for v in vals if v is not None]
            if xp:
                fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                    name=label, line=dict(color=color, width=2.5),
                    marker=dict(size=9),
                    text=[f"{v}/10" for v in yp], textposition="top center"))
        for y, color, label in [(4, "#388e3c", "4 léger"), (7, "#f57c00", "7 sévère")]:
            fig.add_hline(y=y, line_dash="dot", line_color=color,
                          annotation_text=label, annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0, 11], title="NRS /10"),
                          height=320, legend=dict(orientation="h", y=-0.2),
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        rows = [{"Bilan": lbl, "Repos": row.get("nrs_repos", "—"),
                 "Mouvement": row.get("nrs_mouvement", "—"), "Nuit": row.get("nrs_nuit", "—")}
                for lbl, (_, row) in zip(labels, bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
