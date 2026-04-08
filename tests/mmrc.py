"""tests/tests_cliniques/mmrc.py — mMRC Dyspnée BPCO (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

MMRC_GRADES = [
    (0,"Grade 0 — Dyspnée seulement lors d'exercice intense"),
    (1,"Grade 1 — Dyspnée en montant une côte ou une légère pente"),
    (2,"Grade 2 — Marche plus lentement que les autres ou s'arrête après ~100 m à plat"),
    (3,"Grade 3 — S'arrête pour souffler après quelques minutes ou ~100 m à plat"),
    (4,"Grade 4 — Trop essoufflé pour quitter la maison ou s'habiller/déshabiller"),
]
MMRC_COLORS = ["#388e3c","#8bc34a","#f57c00","#e64a19","#d32f2f"]

@register_test
class MMRC(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"mmrc","nom":"mMRC Dyspnée","tab_label":"😮‍💨 mMRC",
                "categorie":"test_clinique","tags":["BPCO", "dyspnée", "respiratoire"],"description":"Modified MRC Dyspnoea Scale grade 0–4"}

    @classmethod
    def fields(cls):
        return ["mmrc_grade"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "grade", "label": "Grade mMRC (0-4)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">mMRC — Dyspnée</div>', unsafe_allow_html=True)
        opts = ["— Non renseigné —"] + [d for _,d in MMRC_GRADES]
        stored = lv("mmrc_grade","")
        idx = 0
        if stored != "":
            try: idx = int(float(stored)) + 1
            except: pass
        chosen = st.radio("Grade mMRC", opts, index=idx, key=f"{key_prefix}_mmrc")
        mmrc_val = ""
        if chosen != "— Non renseigné —":
            mmrc_val = int(chosen.split(" ")[1])
            st.markdown(f'<div class="score-box" style="background:{MMRC_COLORS[mmrc_val]};">'
                        f'mMRC Grade {mmrc_val}</div>', unsafe_allow_html=True)
        return {"mmrc_grade": mmrc_val}

    @classmethod
    def is_filled(cls, bilan_data):
        v = str(bilan_data.get("mmrc_grade","")).strip()
        return v not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            v = str(row.get("mmrc_grade","")).strip()
            try: vals.append(int(float(v)) if v not in ("","None","nan") else None)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="mMRC",
                line=dict(color="#C4603A",width=2.5),marker=dict(size=9),
                text=[f"Grade {v}" for v in yp],textposition="top center"))
        fig.update_layout(yaxis=dict(range=[-0.5,4.5],tickvals=[0,1,2,3,4],title="Grade"),
                          height=300,plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('mmrc', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "mMRC Grade", "col_key": "mmrc_grade",
             "values": [r.get("mmrc_grade","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows=[{"Bilan":lbl,"mMRC Grade":row.get("mmrc_grade","—")}
                          for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Échelle mMRC — Dyspnée (Modified Medical Research Council)", styles["section"]))
        story.append(Paragraph("Évaluation de la dyspnée dans les activités quotidiennes. Cocher le grade correspondant.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.4*cm))
        grades = [
            ("0","Essoufflement uniquement lors d'efforts intenses (montée rapide d'escaliers, course)"),
            ("1","Essoufflement en marchant vite sur terrain plat ou en montant une pente légère"),
            ("2","Marche plus lentement que les personnes du même âge sur terrain plat, ou obligé de s'arrêter par essoufflement au rythme normal"),
            ("3","S'arrêter par essoufflement après avoir marché ~100 m ou après quelques minutes sur terrain plat"),
            ("4","Trop essoufflé pour quitter la maison, ou essoufflement lors de la toilette / de l'habillage"),
        ]
        rows = [["Grade","Description","Cocher"]] + [[g, d, "☐"] for g,d in grades]
        t = Table(rows, colWidths=[1.5*cm,13.5*cm,2*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("ALIGN",(0,0),(0,-1),"CENTER"),("ALIGN",(2,0),(2,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        sc = Table([["Grade mMRC retenu : _____"]], colWidths=[17*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),12),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph("Grade ≥ 2 = dyspnée significative  ·  Grade ≥ 3 = sévère  ·  Seuil BPCO symptomatique = ≥ 1", styles["note"]))

