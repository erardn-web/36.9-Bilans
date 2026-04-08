"""tests/sppb.py — SPPB Short Physical Performance Battery (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import (
    SPPB_BALANCE_OPTS, SPPB_WALK_OPTS, SPPB_CHAIR_OPTS, compute_sppb
)

@register_test
class SPPB(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"sppb","nom":"SPPB","tab_label":"📊 SPPB",
                "categorie":"test_clinique","tags":["équilibre", "marche", "âgé", "fonctionnel"],"description":"Short Physical Performance Battery /12"}

    @classmethod
    def fields(cls):
        return ["sppb_balance","sppb_walk_time","sppb_walk_score",
                "sppb_chair_time","sppb_chair_score","sppb_score","sppb_interpretation"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score total (/12)", "default": True},
            {"key": "sous_scores", "label": "Sous-scores (équilibre, marche, lever)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">SPPB — Short Physical Performance Battery (0–12)</div>',
                    unsafe_allow_html=True)
        collected = {}

        def _sppb_radio(label, opts, key):
            stored = lv(key,"")
            opt_labels = ["— Non évalué —"] + [f"{s} — {d}" for s,d in opts]
            idx = 0
            if stored != "":
                try:
                    sv = int(float(stored))
                    idx = next((i+1 for i,(s,_) in enumerate(opts) if s==sv), 0)
                except: pass
            chosen = st.radio(label, opt_labels, index=idx,
                              key=f"{key_prefix}_{key}", horizontal=False)
            if chosen == "— Non évalué —":
                collected[key] = ""; return None
            else:
                v = int(chosen.split(" — ")[0]); collected[key] = v; return v

        st.markdown("**1. Équilibre statique**")
        bal  = _sppb_radio("Équilibre", SPPB_BALANCE_OPTS, "sppb_balance")
        st.markdown("**2. Vitesse de marche (4 mètres)**")
        walk_time = st.number_input("Temps de marche (sec)", 0.0, 60.0,
            (float(lv("sppb_walk_time","0") or 0) or None), 0.1,
            key=f"{key_prefix}_sppb_wt", help="0 = non mesuré")
        walk = _sppb_radio("Score vitesse de marche", SPPB_WALK_OPTS, "sppb_walk_score")
        collected["sppb_walk_time"] = walk_time or ""
        st.markdown("**3. Levers de chaise (5 fois)**")
        chair_time = st.number_input("Temps 5 levers (sec)", 0.0, 60.0,
            (float(lv("sppb_chair_time","0") or 0) or None), 0.1,
            key=f"{key_prefix}_sppb_ct", help="0 = non mesuré")
        chair = _sppb_radio("Score levers de chaise", SPPB_CHAIR_OPTS, "sppb_chair_score")
        collected["sppb_chair_time"] = chair_time or ""

        result = compute_sppb(bal, walk, chair)
        if result["score"] is not None:
            st.markdown("---")
            st.markdown(
                f'<div class="score-box" style="background:{result["color"]};">'
                f'SPPB : {result["score"]}/12 — {result["interpretation"]}</div>',
                unsafe_allow_html=True)
        collected.update({"sppb_score": result["score"] if result["score"] is not None else "",
                          "sppb_interpretation": result["interpretation"]})
        return collected

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("sppb_score",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        color = "#d32f2f" if s<=6 else "#f57c00" if s<=9 else "#388e3c"
        return {"score":s,"interpretation":data.get("sppb_interpretation",""),"color":color,"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("sppb_score","")) >= 0 and str(bilan_data.get("sppb_score","")).strip() not in ("","None","nan")
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("sppb_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="SPPB /12",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}/12" for v in yp],textposition="top center"))
        for y,color,label in [(6,"#d32f2f","≤6 sévère"),(9,"#f57c00","≤9 modéré")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,13],title="Score /12"),height=320,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"SPPB /12":row.get("sppb_score","—"),
                 "Interprétation":row.get("sppb_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("SPPB — Short Physical Performance Battery (0–12)", styles["section"]))
        story.append(Paragraph("Trois épreuves : équilibre statique, vitesse de marche 4 m, lever de chaise ×5.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        # Équilibre
        story.append(Paragraph("1. Équilibre statique", styles["subsection"]))
        eq_rows = [["Position","Tenu ≥ 10 s ?","Score"],
                   ["Pieds joints","☐ Oui  ☐ Non","0 ou 1"],
                   ["Semi-tandem","☐ Oui  ☐ Non","0 ou 1"],
                   ["Tandem","☐ Oui  ☐ Non","0, 1 ou 2"]]
        t = Table(eq_rows, colWidths=[6*cm,6*cm,5*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Score équilibre : _____ / 4", styles["normal"]))
        story.append(Spacer(1,0.3*cm))
        # Marche
        story.append(Paragraph("2. Vitesse de marche (4 mètres)", styles["subsection"]))
        t2 = Table([["Temps (s)","Score (0–4)"],["_____","_____"]], colWidths=[8.5*cm,8.5*cm])
        t2.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),10),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t2); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("≤ 4.82 s → 4  ·  4.83–6.20 s → 3  ·  6.21–8.70 s → 2  ·  > 8.70 s → 1  ·  incapable → 0", styles["note"]))
        story.append(Spacer(1,0.3*cm))
        # Lever chaise
        story.append(Paragraph("3. Lever de chaise × 5 (sans les bras)", styles["subsection"]))
        t3 = Table([["Temps (s)","Score (0–4)"],["_____","_____"]], colWidths=[8.5*cm,8.5*cm])
        t3.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),10),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t3); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("≤ 11.19 s → 4  ·  11.20–13.69 s → 3  ·  13.70–16.69 s → 2  ·  > 16.70 s → 1  ·  incapable → 0", styles["note"]))
        story.append(Spacer(1,0.3*cm))
        sc = Table([["Score SPPB Total : _____ / 12"]], colWidths=[17*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),12),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph("0–3 : limitation sévère  ·  4–6 : modérée  ·  7–9 : légère  ·  10–12 : normale", styles["note"]))

