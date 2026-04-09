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
            {"key": "graphique_sous_scores","label": "Graphiques sous-scores (éq/marche)", "default": True},
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
        for y, color in [(19,"#d32f2f"),(24,"#f57c00")]:
            fig_total.add_hline(y=y, line_dash="dot", line_color=color)
        fig_total.update_layout(
            yaxis=dict(range=[0,30], title="Score /28"),
            height=350, plot_bgcolor="white", paper_bgcolor="white",
            title="Tinetti — Score total (/28)",
            margin=dict(t=40, r=20, b=60),
            annotations=[
                dict(x=1, y=19, xref="paper", yref="y",
                     text="< 19 risque élevé", showarrow=False,
                     xanchor="right", yanchor="top",
                     font=dict(size=9, color="#d32f2f"), bgcolor="white"),
                dict(x=1, y=24, xref="paper", yref="y",
                     text="< 24 risque modéré", showarrow=False,
                     xanchor="right", yanchor="top",
                     font=dict(size=9, color="#f57c00"), bgcolor="white"),
            ])
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
                margin=dict(t=40, r=20, b=60),
                legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fig_sub, use_container_width=True)
            if show_print_controls:
                key_sub = cls._print_chart_key("sous_scores", cas_id)
                cls._render_print_checkbox(key_sub, "🖨️ Inclure les sous-scores dans le PDF",
                                           default=True)
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
        from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle,
                                        PageBreak, Flowable)
        from reportlab.lib.units import cm, mm
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.graphics.shapes import Drawing, Rect

        LINE = colors.HexColor("#CCCCCC")
        BLEU = colors.HexColor("#2B57A7")
        GREY = colors.HexColor("#555555")

        # Checkbox dessinée (vrai carré vide)
        class Checkbox(Flowable):
            def __init__(self, size=8):
                self.size = size
                self.width = size
                self.height = size
            def draw(self):
                self.canv.setStrokeColor(colors.HexColor("#333"))
                self.canv.setLineWidth(0.6)
                self.canv.rect(0, 0, self.size, self.size, fill=0)

        def _cb():
            return Checkbox(7)

        # Styles locaux — taille réduite pour tenir sur une page
        ctx_style = ParagraphStyle("ctx", fontName="Helvetica-BoldOblique",
                                   fontSize=8, textColor=GREY,
                                   spaceBefore=5, spaceAfter=2,
                                   borderPad=3, backColor=colors.HexColor("#F5F5F5"),
                                   borderWidth=0.5, borderColor=LINE,
                                   leftIndent=2, rightIndent=2)
        q_style = ParagraphStyle("q2", fontName="Helvetica-Bold",
                                 fontSize=8.5, spaceBefore=4, spaceAfter=1)
        opt_style = ParagraphStyle("opt", fontName="Helvetica",
                                   fontSize=8, leftIndent=10,
                                   spaceBefore=0, spaceAfter=0)

        story.append(Paragraph("Tinetti — POMA (Performance Oriented Mobility Assessment)",
                                styles["section"]))
        story.append(Paragraph(
            "Seuil risque de chute : &lt; 24/28  |  19–23 : risque modéré  |  &lt; 19 : risque élevé",
            styles["intro"]))
        story.append(Spacer(1, 0.15*cm))
        hdr = Table([["Patient : " + "_"*28, "Date : " + "_"*14, "Praticien : " + "_"*14]],
                    colWidths=[8*cm, 4.5*cm, 4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
                                  ("TEXTCOLOR",(0,0),(-1,-1),GREY)]))
        story.append(hdr)
        story.append(Spacer(1, 0.25*cm))

        def _context_band(text):
            story.append(Paragraph(text, ctx_style))

        def _item(label, options):
            story.append(Paragraph(label, q_style))
            if len(options) == 2:
                # 2 colonnes côte à côte
                row = []
                for s, d in options:
                    row.append(Table(
                        [[_cb(), Paragraph(f" {s} — {d}", opt_style)]],
                        colWidths=[0.35*cm, 8*cm],
                        style=[("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                               ("LEFTPADDING",(0,0),(-1,-1),0),
                               ("RIGHTPADDING",(0,0),(-1,-1),2),
                               ("TOPPADDING",(0,0),(-1,-1),1),
                               ("BOTTOMPADDING",(0,0),(-1,-1),1)]))
                tbl = Table([row], colWidths=[8.5*cm, 8.5*cm])
                tbl.setStyle(TableStyle([
                    ("VALIGN",(0,0),(-1,-1),"TOP"),
                    ("LEFTPADDING",(0,0),(-1,-1),0),
                    ("TOPPADDING",(0,0),(-1,-1),0),
                    ("BOTTOMPADDING",(0,0),(-1,-1),1)]))
            else:
                rows = []
                for s, d in options:
                    rows.append([_cb(), Paragraph(f" {s} — {d}", opt_style)])
                tbl = Table(rows, colWidths=[0.35*cm, 16.65*cm])
                tbl.setStyle(TableStyle([
                    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                    ("LEFTPADDING",(0,0),(-1,-1),0),
                    ("TOPPADDING",(0,0),(-1,-1),1),
                    ("BOTTOMPADDING",(0,0),(-1,-1),1)]))
            story.append(tbl)

        # ── PARTIE I — ÉQUILIBRE ──────────────────────────────────────────────
        story.append(Paragraph(f"Partie I — Équilibre (/{TINETTI_EQ_MAX})",
                                styles["subsection"]))

        eq_items = list(TINETTI_EQUILIBRE)
        _context_band("Le patient est assis sur une chaise sans accoudoirs :")
        _item(eq_items[0][1], eq_items[0][2])

        _context_band("On demande au patient de se lever, si possible sans s'appuyer sur les accoudoirs :")
        _item(eq_items[1][1], eq_items[1][2])
        _item(eq_items[2][1], eq_items[2][2])

        _context_band("Test d'équilibre en position debout :")
        for item in eq_items[3:]:
            _item(item[1], item[2])

        story.append(Spacer(1, 0.15*cm))
        eq_score = Table([["Score Équilibre : _____ / " + str(TINETTI_EQ_MAX)]],
                         colWidths=[17*cm])
        eq_score.setStyle(TableStyle([
            ("FONTSIZE",  (0,0),(-1,-1), 10),
            ("FONTNAME",  (0,0),(-1,-1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0,0),(-1,-1), BLEU),
            ("BOX",       (0,0),(-1,-1), 0.5, LINE),
            ("TOPPADDING",(0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ]))
        story.append(eq_score)

        # ── PARTIE II — MARCHE (nouvelle page) ───────────────────────────────
        story.append(PageBreak())
        story.append(Paragraph(f"Partie II — Marche (/{TINETTI_MA_MAX})",
                                styles["subsection"]))
        story.append(Spacer(1, 0.1*cm))
        _context_band(
            "Le patient doit marcher au moins 3 mètres, faire demi-tour et revenir. "
            "Il utilise son aide technique habituelle (canne, déambulateur) :")

        for item in TINETTI_MARCHE:
            _item(item[1], item[2])

        story.append(Spacer(1, 0.25*cm))
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
