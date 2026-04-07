"""tests/sts.py — STS Sit to Stand 1 minute (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

@register_test
class STS(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"sts","nom":"STS — Sit to Stand 1 min","tab_label":"🪑 STS 1 min",
                "categorie":"test_clinique","tags":["équilibre", "chaise", "force", "âgé", "fonctionnel", "BPCO"],"description":"Levers de chaise en 1 minute"}

    @classmethod
    def fields(cls):
        return ["sts_1min_reps","sts_1min_interpretation"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">STS — Sit to Stand 1 minute</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">Compter le nombre de levers complets en 1 minute '
                    'depuis une chaise standard sans appui-bras.</div>', unsafe_allow_html=True)
        stored = lv("sts_1min_reps",None)
        try:    default = int(float(stored)) if stored not in (None,"","None") else None
        except: default = None
        sts_reps = st.number_input("Nombre de répétitions / minute",
                                   min_value=0, max_value=60, step=1,
                                   value=default, key=f"{key_prefix}_sts_reps",
                                   help="0 = non réalisé")
        sts_interp = ""
        if sts_reps and sts_reps > 0:
            if sts_reps >= 14:   sts_color,sts_interp = "#388e3c","Bonne capacité fonctionnelle (≥ 14)"
            elif sts_reps >= 10: sts_color,sts_interp = "#f57c00","Capacité modérée (10–13)"
            else:                sts_color,sts_interp = "#d32f2f","Capacité limitée (< 10)"
            st.markdown(f'<div class="score-box" style="background:{sts_color};">'
                        f'{sts_reps} rép/min — {sts_interp}</div>', unsafe_allow_html=True)
        return {"sts_1min_reps": sts_reps or "", "sts_1min_interpretation": sts_interp}

    @classmethod
    def score(cls, data):
        try:    s = float(data.get("sts_1min_reps",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        if s<=0: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        color = "#388e3c" if s>=14 else "#f57c00" if s>=10 else "#d32f2f"
        return {"score":s,"interpretation":data.get("sts_1min_interpretation",""),"color":color,"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("sts_1min_reps","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("sts_1min_reps",""))
                vals.append(None if not math.isfinite(f) or f<=0 else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Bar(x=xp,y=yp,marker_color="#2B57A7",
                text=[f"{v:.0f} rép" for v in yp],textposition="outside"))
        for y,color,label in [(10,"#d32f2f","10 seuil bas"),(14,"#388e3c","14 normal")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis_title="Répétitions/min",height=300,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"STS (rép/min)":row.get("sts_1min_reps","—"),
                 "Interprétation":row.get("sts_1min_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("STS — Sit to Stand 1 minute", styles["section"]))
        story.append(Paragraph("Nombre de levers de chaise en 1 minute, sans aide des bras si possible.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.5*cm))
        for label in ["Utilisation des bras : ☐ Non  ☐ Oui (à noter)",
                      "Incidents / arrêts : "+"_"*50,
                      "Nombre de levers en 1 minute : _____"]:
            t = Table([[label]],colWidths=[17*cm])
            t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),10),("LINEBELOW",(0,0),(-1,-1),0.3,LINE),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
            story.append(t); story.append(Spacer(1,0.1*cm))
        story.append(Spacer(1,0.3*cm))
        sc = Table([["Résultat : _____ levers / min"]], colWidths=[17*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),11),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph("Normes (60–69 ans) : F ≥ 12  /  H ≥ 14  ·  (70–79 ans) : F ≥ 11  /  H ≥ 12", styles["note"]))

