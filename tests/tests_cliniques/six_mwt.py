"""tests/tests_cliniques/six_mwt.py — Test de marche 6 minutes (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import interpret_6mwt

@register_test
class SixMWT(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"six_mwt","nom":"Test de marche 6 minutes","tab_label":"🚶 6MWT",
                "categorie":"test_clinique","tags":["marche", "aérobie", "BPCO", "effort", "respiratoire"],"description":"Distance parcourue en 6 minutes, seuil ≥ 400 m"}

    @classmethod
    def fields(cls):
        return ["mwt_distance","mwt_spo2_avant","mwt_spo2_apres","mwt_spo2_min",
                "mwt_fc_avant","mwt_fc_apres",
                "mwt_dyspnee_avant","mwt_dyspnee_apres",
                "mwt_fatigue_avant","mwt_fatigue_apres",
                "mwt_aide_technique","mwt_incidents","mwt_interpretation"]

    def render(self, lv, key_prefix):
        def _lf(key):
            v = lv(key,None)
            try: return float(v) if v not in (None,"","None") else None
            except: return None
        def _li(key):
            v = lv(key,None)
            try: return int(float(v)) if v not in (None,"","None") else None
            except: return None

        st.markdown('<div class="section-title">Test de marche de 6 minutes (6MWT)</div>',
                    unsafe_allow_html=True)
        m1,m2 = st.columns(2)
        with m1:
            st.markdown("**Avant**")
            spo2_av = st.number_input("SpO₂ avant (%)",0.0,100.0,_lf("mwt_spo2_avant"),0.1,
                                      key=f"{key_prefix}_mwt_s1")
            fc_av   = st.number_input("FC avant (bpm)",0,250,_li("mwt_fc_avant"),1,
                                      key=f"{key_prefix}_mwt_f1")
            dysp_av = st.select_slider("Dyspnée avant (Borg 0–10)",
                options=[None]+list(range(11)), value=_li("mwt_dyspnee_avant"),
                format_func=lambda x: "—" if x is None else str(x),
                key=f"{key_prefix}_mwt_d1")
            fat_av  = st.select_slider("Fatigue avant (Borg 0–10)",
                options=[None]+list(range(11)), value=_li("mwt_fatigue_avant"),
                format_func=lambda x: "—" if x is None else str(x),
                key=f"{key_prefix}_mwt_fa1")
        with m2:
            st.markdown("**Après**")
            spo2_ap  = st.number_input("SpO₂ après (%)",0.0,100.0,_lf("mwt_spo2_apres"),0.1,
                                       key=f"{key_prefix}_mwt_s2")
            spo2_min = st.number_input("SpO₂ min (%)",0.0,100.0,_lf("mwt_spo2_min"),0.1,
                                       key=f"{key_prefix}_mwt_s3",help="SpO₂ minimale pendant le test")
            fc_ap    = st.number_input("FC après (bpm)",0,250,_li("mwt_fc_apres"),1,
                                       key=f"{key_prefix}_mwt_f2")
            dysp_ap  = st.select_slider("Dyspnée après (Borg 0–10)",
                options=[None]+list(range(11)), value=_li("mwt_dyspnee_apres"),
                format_func=lambda x: "—" if x is None else str(x),
                key=f"{key_prefix}_mwt_d2")
            fat_ap   = st.select_slider("Fatigue après (Borg 0–10)",
                options=[None]+list(range(11)), value=_li("mwt_fatigue_apres"),
                format_func=lambda x: "—" if x is None else str(x),
                key=f"{key_prefix}_mwt_fa2")

        dist = st.number_input("Distance parcourue (mètres)",0,1000,_li("mwt_distance"),1,
                               key=f"{key_prefix}_mwt_dist",help="0 = non réalisé")
        aide_opts = ["Aucune","Canne","Déambulateur","Oxygène","Autre"]
        stored_aide = lv("mwt_aide_technique","")
        default_aide = [x for x in str(stored_aide).split("|") if x in aide_opts] if stored_aide else []
        mwt_aides = st.multiselect("Aide(s) technique(s)", aide_opts,
                                   default=default_aide, key=f"{key_prefix}_mwt_aide")
        mwt_inc = st.text_area("Incidents / arrêts", value=lv("mwt_incidents",""),
                               height=50, key=f"{key_prefix}_mwt_inc")
        mwt_interp = ""
        if dist and dist > 0:
            r6 = interpret_6mwt(dist)
            mwt_interp = r6["interpretation"]
            st.markdown(f'<div class="score-box" style="background:{r6["color"]};">'
                        f'6MWT : {dist} m — {mwt_interp}</div>', unsafe_allow_html=True)
        return {
            "mwt_distance":dist or "","mwt_spo2_avant":spo2_av or "",
            "mwt_spo2_apres":spo2_ap or "","mwt_spo2_min":spo2_min or "",
            "mwt_fc_avant":fc_av or "","mwt_fc_apres":fc_ap or "",
            "mwt_dyspnee_avant":"" if dysp_av is None else dysp_av,
            "mwt_dyspnee_apres":"" if dysp_ap is None else dysp_ap,
            "mwt_fatigue_avant":"" if fat_av is None else fat_av,
            "mwt_fatigue_apres":"" if fat_ap is None else fat_ap,
            "mwt_aide_technique":"|".join(mwt_aides) if mwt_aides else "",
            "mwt_incidents":mwt_inc,"mwt_interpretation":mwt_interp,
        }

    @classmethod
    def score(cls, data):
        try:    d = float(data.get("mwt_distance",""))
        except: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        if d<=0: return {"score":None,"interpretation":"","color":"#888888","details":{}}
        r = interpret_6mwt(d)
        return {"score":d,"interpretation":r["interpretation"],"color":r["color"],"details":{}}

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("mwt_distance","")) > 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("mwt_distance",""))
                vals.append(None if not math.isfinite(f) or f<=0 else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
        yp = [v for v in vals if v is not None and v==v]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="Distance (m)",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}m" for v in yp],textposition="top center"))
        for y,color,label in [(150,"#d32f2f","150m"),(300,"#f57c00","300m"),(400,"#388e3c","400m normal")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis_title="Mètres",height=350,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"Distance (m)":row.get("mwt_distance","—"),
                 "SpO₂ avant":row.get("mwt_spo2_avant","—"),
                 "SpO₂ après":row.get("mwt_spo2_apres","—"),
                 "Interprétation":row.get("mwt_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("6MWT — Test de Marche de 6 Minutes", styles["section"]))
        story.append(Paragraph("Marcher le plus loin possible en 6 minutes sur un couloir de 30 m. Mesurer SpO₂ et FC avant/après.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        headers = ["Paramètre","Avant","Après","Min (si BPCO)"]
        rows = [headers,
                ["SpO₂ (%)","_____","_____","_____"],
                ["FC (bpm)","_____","_____",""],
                ["Dyspnée Borg (0–10)","_____","_____",""],
                ["Fatigue MI Borg (0–10)","_____","_____",""]]
        t = Table(rows, colWidths=[6*cm,3.5*cm,3.5*cm,4*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),10),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),
            ("GRID",(0,0),(-1,-1),0.3,LINE),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        for label in ["Aide technique : ☐ Aucune  ☐ Canne  ☐ Déambulateur",
                      "Incidents / arrêts (durée, raison) : "+"_"*40]:
            story.append(Paragraph(label, styles["normal"])); story.append(Spacer(1,0.2*cm))
        story.append(Spacer(1,0.2*cm))
        sc = Table([["Distance parcourue : _____ mètres"]], colWidths=[17*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),12),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph("Valeur prédite (Enright) = 868 − (2.99×âge) − (74.7×sexeF) ± 139 m", styles["note"]))

