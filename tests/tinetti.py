"""tests/tinetti.py — Tinetti POMA (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import (
    TINETTI_EQUILIBRE, TINETTI_MARCHE, TINETTI_EQ_KEYS, TINETTI_MA_KEYS,
    TINETTI_EQ_MAX, TINETTI_MA_MAX, compute_tinetti
)

@register_test
class Tinetti(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tinetti","nom":"Tinetti — POMA","tab_label":"🏃 Tinetti",
                "categorie":"test_clinique","tags":["équilibre", "marche", "chute", "âgé"],"description":"Équilibre et marche /28, seuil risque chute < 24"}

    @classmethod
    def fields(cls):
        return (TINETTI_EQ_KEYS + TINETTI_MA_KEYS +
                ["tinetti_eq_score","tinetti_ma_score","tinetti_total","tinetti_interpretation"])

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total",         "label": "Score total (/28)",              "default": True},
            {"key": "score_equilibre",      "label": "Score équilibre (/16)",          "default": True},
            {"key": "score_marche",         "label": "Score marche (/12)",             "default": True},
            {"key": "interpretation",       "label": "Interprétation (risque chute)",  "default": True},
            {"key": "graphique_total",      "label": "Graphique score total",          "default": True},
            {"key": "graphique_sous_scores","label": "Graphiques sous-scores (éq/marche)", "default": False},
            {"key": "detail_items",         "label": "Détail des items",               "default": False},
        ]

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
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=""):
        import plotly.graph_objects as go
        import math, pandas as pd

        def _vals(col):
            out = []
            for _, row in bilans_df.iterrows():
                try:
                    f = float(row.get(col, ""))
                    out.append(None if not math.isfinite(f) else f)
                except: out.append(None)
            return out

        # ── Graphique score total ──────────────────────────────────────────────
        vals = _vals("tinetti_total")
        xp = [labels[i] for i,v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        fig_total = go.Figure()
        if xp:
            fig_total.add_trace(go.Scatter(
                x=xp, y=yp, mode="lines+markers+text", name="Tinetti /28",
                line=dict(color="#2B57A7", width=2.5), marker=dict(size=9),
                text=[f"{v:.0f}/28" for v in yp], textposition="top center"))
        for y, color, lbl in [(19,"#d32f2f","< 19 risque élevé"),(24,"#f57c00","< 24 risque modéré")]:
            fig_total.add_hline(y=y, line_dash="dot", line_color=color,
                                annotation_text=lbl, annotation_position="right")
        fig_total.update_layout(yaxis=dict(range=[0,30], title="Score /28"),
                                height=350, plot_bgcolor="white", paper_bgcolor="white",
                                title="Tinetti — Score total (/28)")
        st.plotly_chart(fig_total, use_container_width=True)
        if show_print_controls:
            key_total = cls._print_chart_key("total", cas_id)
            cls._render_print_checkbox(key_total, "🖨️ Inclure ce graphique dans le PDF")
            cls._store_chart(key_total, fig_total, cas_id)

        # ── Graphiques sous-scores (optionnels) ───────────────────────────────
        vals_eq = _vals("tinetti_eq_score")
        vals_ma = _vals("tinetti_ma_score")
        has_eq = any(v is not None for v in vals_eq)
        has_ma = any(v is not None for v in vals_ma)

        if has_eq or has_ma:
            fig_sub = go.Figure()
            if has_eq:
                xq = [labels[i] for i,v in enumerate(vals_eq) if v is not None]
                yq = [v for v in vals_eq if v is not None]
                fig_sub.add_trace(go.Scatter(
                    x=xq, y=yq, mode="lines+markers+text", name="Équilibre (/16)",
                    line=dict(color="#1D9E75", width=2), marker=dict(size=8),
                    text=[f"{v:.0f}" for v in yq], textposition="top center"))
            if has_ma:
                xm = [labels[i] for i,v in enumerate(vals_ma) if v is not None]
                ym = [v for v in vals_ma if v is not None]
                fig_sub.add_trace(go.Scatter(
                    x=xm, y=ym, mode="lines+markers+text", name="Marche (/12)",
                    line=dict(color="#D85A30", width=2), marker=dict(size=8),
                    text=[f"{v:.0f}" for v in ym], textposition="top center"))
            fig_sub.update_layout(
                height=300, plot_bgcolor="white", paper_bgcolor="white",
                title="Tinetti — Sous-scores",
                legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_sub, use_container_width=True)
            if show_print_controls:
                key_sub = cls._print_chart_key("sous_scores", cas_id)
                cls._render_print_checkbox(key_sub, "🖨️ Inclure les sous-scores dans le PDF",
                                           default=False)
                cls._store_chart(key_sub, fig_sub, cas_id)

        # ── Tableau récap avec checkboxes PDF ─────────────────────────────────
        table_rows = [
            {"label": "Équilibre (/16)", "col_key": "tinetti_eq_score",
             "values": [r.get("tinetti_eq_score","—") for _,r in bilans_df.iterrows()]},
            {"label": "Marche (/12)",    "col_key": "tinetti_ma_score",
             "values": [r.get("tinetti_ma_score","—") for _,r in bilans_df.iterrows()]},
            {"label": "Total (/28)",     "col_key": "tinetti_total",
             "values": [r.get("tinetti_total","—") for _,r in bilans_df.iterrows()]},
            {"label": "Interprétation", "col_key": "tinetti_interpretation",
             "values": [r.get("tinetti_interpretation","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows_df = [{"Bilan": lbl,
                        "Équilibre (/16)": r.get("tinetti_eq_score","—"),
                        "Marche (/12)":    r.get("tinetti_ma_score","—"),
                        "Total (/28)":     r.get("tinetti_total","—"),
                        "Interprétation":  r.get("tinetti_interpretation","—")}
                       for lbl, (_,r) in zip(labels, bilans_df.iterrows())]
            st.dataframe(pd.DataFrame(rows_df), use_container_width=True, hide_index=True)

    @classmethod
    def render_pdf_with_config(cls, story, styles, bilans_df, labels, config=None):
        """Tinetti : respecte la config graphique (total vs sous-scores)."""
        if config is None:
            cls.render_pdf(story, styles, bilans_df, labels)
            return

        n = len(bilans_df)
        show_graphique_total      = config.get("graphique_total", True)
        show_graphique_sous_scores = config.get("graphique_sous_scores", False)

        # Passer les colonnes à exclure selon config
        # On délègue à render_pdf en masquant les colonnes non voulues
        cls.render_pdf(story, styles, bilans_df, labels,
                       show_graphique_total=show_graphique_total and n >= 2,
                       show_graphique_sous_scores=show_graphique_sous_scores and n >= 2)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        story.append(Paragraph("Tinetti — POMA (Performance Oriented Mobility Assessment)", styles["section"]))
        story.append(Paragraph("Seuil risque de chute : < 24/28  |  19–23 : risque modéré  |  < 19 : risque élevé", styles["intro"]))
        story.append(Spacer(1, 0.2*cm))
        hdr = Table([["Patient : " + "_"*28, "Date : " + "_"*14, "Praticien : " + "_"*14]],
                    colWidths=[8*cm, 4.5*cm, 4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
                                  ("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555555"))]))
        story.append(hdr)
        story.append(Spacer(1, 0.3*cm))

        LINE = colors.HexColor("#CCCCCC")
        BLEU = colors.HexColor("#2B57A7")

        def _section(titre, items, max_score):
            story.append(Paragraph(f"{titre} (/{max_score})", styles["subsection"]))
            for key, label, options in items:
                story.append(Paragraph(label, styles["question"]))
                opt_cells = [f"☐  {s} — {d}" for s, d in options]
                if len(opt_cells) == 2:
                    tbl = Table([opt_cells], colWidths=[8.5*cm, 8.5*cm])
                else:
                    tbl = Table([[o] for o in opt_cells], colWidths=[17*cm])
                tbl.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
                    ("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#222")),
                    ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
                story.append(tbl)
            story.append(Spacer(1, 0.15*cm))

        _section("Partie I — Équilibre", TINETTI_EQUILIBRE, TINETTI_EQ_MAX)
        story.append(Spacer(1, 0.2*cm))
        _section("Partie II — Marche", TINETTI_MARCHE, TINETTI_MA_MAX)

        story.append(Spacer(1, 0.3*cm))
        score_tbl = Table([[
            "Score Équilibre : _____ / " + str(TINETTI_EQ_MAX),
            "Score Marche : _____ / " + str(TINETTI_MA_MAX),
            "Score Total : _____ / " + str(TINETTI_EQ_MAX + TINETTI_MA_MAX),
        ]], colWidths=[5.5*cm, 5.5*cm, 6*cm])
        score_tbl.setStyle(TableStyle([
            ("FONTSIZE",(0,0),(-1,-1),10),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),
            ("INNERGRID",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        story.append(score_tbl)
        story.append(Paragraph("< 19 → risque élevé · 19–23 → risque modéré · ≥ 24 → risque faible", styles["note"]))
