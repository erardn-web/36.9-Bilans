"""tests/tests_cliniques/spirometrie.py — Spirométrie BPCO (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

@register_test
class Spirometrie(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"spirometrie","nom":"Spirométrie","tab_label":"💨 Spirométrie",
                "categorie":"test_clinique","tags":["BPCO", "respiratoire", "poumon", "VEMS", "CVF"],"description":"VEMS, CVF, ratio, stade GOLD"}

    @classmethod
    def fields(cls):
        return ["spiro_vems","spiro_cvf","spiro_ratio","spiro_vems_pct","spiro_cvf_pct",
                "spiro_gold","spiro_notes"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "vems", "label": "VEMS (% prédit)", "default": True},
            {"key": "cvf", "label": "CVF (L)", "default": True},
            {"key": "rapport", "label": "Rapport VEMS/CVF", "default": True},
            {"key": "gold", "label": "Stade GOLD", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
        ]

    def render(self, lv, key_prefix):
        def _lf(k):
            v=lv(k,None)
            try: return float(v) if v not in (None,"","None") else None
            except: return None

        st.markdown('<div class="section-title">Spirométrie</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Valeurs post-bronchodilatateur si disponibles.</div>',
                    unsafe_allow_html=True)
        s1,s2 = st.columns(2)
        with s1:
            vems  = st.number_input("VEMS (L)",0.0,8.0,_lf("spiro_vems"),0.01,
                                    key=f"{key_prefix}_vems",help="Volume Expiratoire Maximal Seconde")
            cvf   = st.number_input("CVF (L)",0.0,10.0,_lf("spiro_cvf"),0.01,
                                    key=f"{key_prefix}_cvf",help="Capacité Vitale Forcée")
            ratio = st.number_input("VEMS/CVF (%)",0.0,100.0,_lf("spiro_ratio"),0.1,
                                    key=f"{key_prefix}_ratio")
        with s2:
            vems_pct = st.number_input("VEMS % prédit",0.0,200.0,_lf("spiro_vems_pct"),0.1,
                                       key=f"{key_prefix}_vems_pct")
            cvf_pct  = st.number_input("CVF % prédit",0.0,200.0,_lf("spiro_cvf_pct"),0.1,
                                       key=f"{key_prefix}_cvf_pct")
            gold_opts = ["— Non renseigné —","GOLD 1 (léger ≥ 80%)","GOLD 2 (modéré 50–79%)",
                         "GOLD 3 (sévère 30–49%)","GOLD 4 (très sévère < 30%)"]
            stored_gold = lv("spiro_gold","— Non renseigné —")
            gold = st.selectbox("Stade GOLD", gold_opts,
                index=gold_opts.index(stored_gold) if stored_gold in gold_opts else 0,
                key=f"{key_prefix}_gold")

        if vems_pct and vems_pct > 0:
            if vems_pct>=80:   gc,gi = "#388e3c","GOLD 1 — Léger"
            elif vems_pct>=50: gc,gi = "#f57c00","GOLD 2 — Modéré"
            elif vems_pct>=30: gc,gi = "#e64a19","GOLD 3 — Sévère"
            else:              gc,gi = "#d32f2f","GOLD 4 — Très sévère"
            st.markdown(f'<div class="score-box" style="background:{gc};">'
                        f'VEMS {vems_pct}% prédit → {gi}</div>', unsafe_allow_html=True)

        spiro_notes = st.text_area("Notes",value=lv("spiro_notes",""),height=60,
                                   key=f"{key_prefix}_notes")
        return {"spiro_vems":vems or "","spiro_cvf":cvf or "","spiro_ratio":ratio or "",
                "spiro_vems_pct":vems_pct or "","spiro_cvf_pct":cvf_pct or "",
                "spiro_gold":"" if gold=="— Non renseigné —" else gold,
                "spiro_notes":spiro_notes}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("spiro_vems_pct","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("spiro_vems_pct",""))
                vals.append(None if not math.isfinite(f) or f<=0 else f)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="VEMS % prédit",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}%" for v in yp],textposition="top center"))
        for y,color,label in [(80,"#388e3c","GOLD 1"),(50,"#f57c00","GOLD 2"),(30,"#d32f2f","GOLD 3")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis_title="VEMS % prédit",height=320,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('spirometrie', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "VEMS (L)", "col_key": "spiro_vems",
             "values": [r.get("spiro_vems","—") for _,r in bilans_df.iterrows()]},
            {"label": "CVF (L)", "col_key": "spiro_cvf",
             "values": [r.get("spiro_cvf","—") for _,r in bilans_df.iterrows()]},
            {"label": "VEMS %", "col_key": "spiro_vems_pct",
             "values": [r.get("spiro_vems_pct","—") for _,r in bilans_df.iterrows()]},
            {"label": "GOLD", "col_key": "spiro_gold",
             "values": [r.get("spiro_gold","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows=[{"Bilan":lbl,"VEMS (L)":row.get("spiro_vems","—"),"CVF (L)":row.get("spiro_cvf","—"),
                           "VEMS %":row.get("spiro_vems_pct","—"),"GOLD":row.get("spiro_gold","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Spirométrie", styles["section"]))
        story.append(Paragraph("Mesure des volumes et débits pulmonaires. À réaliser avec spiromètre homologué.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        rows = [["Paramètre","Mesuré","Prédit","% Prédit","Interprétation"],
                ["VEMS (L)","_____","_____","_____ %",""],
                ["CVF (L)","_____","_____","_____ %",""],
                ["VEMS/CVF (%)","_____","","",""],
                ["DEP (L/s)","_____","_____","_____ %",""],
                ["CRF (L)","_____","_____","_____ %",""]]
        t = Table(rows, colWidths=[3.5*cm,3*cm,3*cm,3*cm,4.5*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        story.append(Paragraph("Classification GOLD (obstruction) :", styles["normal"]))
        gold = Table([["☐ GOLD 1 — VEMS ≥ 80%","☐ GOLD 2 — VEMS 50–79%","☐ GOLD 3 — VEMS 30–49%","☐ GOLD 4 — VEMS < 30%"]],
                     colWidths=[4.25*cm]*4)
        gold.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),0.3,LINE),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(gold); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Notes : "+"_"*70, styles["normal"]))

