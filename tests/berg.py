"""tests/tests_cliniques/berg.py — Berg Balance Scale (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import BERG_ITEMS, BERG_KEYS, compute_berg

@register_test
class Berg(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"berg","nom":"Berg Balance Scale","tab_label":"⚖️ Berg",
                "categorie":"test_clinique","tags":["équilibre", "chute", "âgé", "fonctionnel"],"description":"14 items /56, seuils chute ≤20/≤40"}

    @classmethod
    def fields(cls):
        return BERG_KEYS + ["berg_score","berg_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">Berg Balance Scale (0–56)</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">14 items cotés 0–4. '
                    'Seuils : ≤ 20 = risque élevé · 21–40 = risque modéré · ≥ 41 = faible</div>',
                    unsafe_allow_html=True)
        collected = {}
        berg_answers = {}
        for key, label, options in BERG_ITEMS:
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
                berg_answers[key] = score
                collected[key]    = score
            else:
                collected[key] = ""
        berg_r = compute_berg(berg_answers)
        if berg_r["score"] is not None:
            st.markdown("---")
            st.markdown(
                f'<div class="score-box" style="background:{berg_r["color"]};">'
                f'Berg : {berg_r["score"]}/56 — {berg_r["interpretation"]}</div>',
                unsafe_allow_html=True)
        collected.update({"berg_score":berg_r["score"] if berg_r["score"] is not None else "",
                          "berg_interpretation":berg_r["interpretation"]})
        return collected

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("berg_score",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        color = "#d32f2f" if s<=20 else "#f57c00" if s<=40 else "#388e3c"
        return {"score":s,"interpretation":data.get("berg_interpretation",""),"color":color,"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("berg_score","")) >= 0 and str(bilan_data.get("berg_score","")).strip() not in ("","None","nan")
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("berg_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Berg /56",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}/56" for v in yp],textposition="top center"))
        for y,color,label in [(20,"#d32f2f","≤20 risque élevé"),(40,"#f57c00","≤40 risque modéré")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,58],title="Score /56"),height=350,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"Berg /56":row.get("berg_score","—"),
                 "Interprétation":row.get("berg_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from tests.tests_cliniques.shared_data import BERG_ITEMS
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Berg Balance Scale (0–56)", styles["section"]))
        story.append(Paragraph("Évaluation de l'équilibre. Seuil risque de chute : < 45/56", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        for key, label, options in BERG_ITEMS:
            story.append(Paragraph(label, styles["question"]))
            opt_rows = [[f"☐  {s} — {d}"] for s,d in options]
            t = Table(opt_rows, colWidths=[17*cm])
            t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1)]))
            story.append(t)
        story.append(Spacer(1,0.3*cm))
        sc = Table([["Score Total : _____ / 56"]], colWidths=[17*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),11),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph("< 45 → risque de chute  ·  < 36 → risque très élevé  ·  41–56 → risque faible", styles["note"]))

