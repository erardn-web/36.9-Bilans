"""tests/tests_cliniques/bode.py — BODE Index BPCO (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

def compute_bode(fev1_pct, mmrc, dist_6mwt, bmi):
    score=0
    if fev1_pct is not None:
        if fev1_pct>=65:   score+=0
        elif fev1_pct>=50: score+=1
        elif fev1_pct>=36: score+=2
        else:              score+=3
    if mmrc is not None:
        if mmrc<=1:   score+=0
        elif mmrc==2: score+=1
        elif mmrc==3: score+=2
        else:         score+=3
    if dist_6mwt is not None:
        if dist_6mwt>=350:   score+=0
        elif dist_6mwt>=250: score+=1
        elif dist_6mwt>=150: score+=2
        else:                score+=3
    if bmi is not None:
        score+=0 if bmi>21 else 1
    if score<=2:   color,interp,survival="#388e3c","Quartile 1 — Bon pronostic (0–2)","~80% survie 4 ans"
    elif score<=4: color,interp,survival="#f57c00","Quartile 2 — Pronostic modéré (3–4)","~67%"
    elif score<=6: color,interp,survival="#e64a19","Quartile 3 — Pronostic réservé (5–6)","~57%"
    else:          color,interp,survival="#d32f2f","Quartile 4 — Pronostic sévère (7–10)","~18%"
    return {"score":score,"color":color,"interpretation":interp,"survival":survival}

@register_test
class BODE(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"bode","nom":"BODE Index","tab_label":"📊 BODE",
                "categorie":"test_clinique","tags":["BPCO", "respiratoire", "pronostic", "mortalité"],"description":"Index pronostic BPCO /10 (VEMS, mMRC, 6MWT, IMC)"}

    @classmethod
    def fields(cls):
        return ["bode_score","bode_interpretation"]

    def render(self, lv, key_prefix):
        def _lf(k):
            v=lv(k,None)
            try: return float(v) if v not in (None,"","None") else None
            except: return None
        def _li(k):
            v=lv(k,None)
            try: return int(float(v)) if v not in (None,"","None") else None
            except: return None

        st.markdown('<div class="section-title">BODE Index (0–10)</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Calculé à partir du VEMS%, mMRC, 6MWT et IMC. '
                    'Remplissez les onglets correspondants d\'abord.</div>', unsafe_allow_html=True)

        # IMC depuis onglet général (bmi calculé, ou recalcul depuis poids_kg/taille_cm)
        bmi_val = _lf("bmi")
        if not bmi_val:
            p = _lf("poids_kg"); t = _lf("taille_cm")
            if p and t and p > 0 and t > 0:
                bmi_val = round(p / (t/100)**2, 1)
        if bmi_val:
            st.info(f"IMC (onglet Général) : **{bmi_val} kg/m²**")
        else:
            st.warning("⚠️ Renseignez le poids et la taille dans l'onglet Général pour calculer l'IMC.")

        # Lire les valeurs des autres tests depuis bilan_data via lv
        fev1_val = _lf("spiro_vems_pct")
        mmrc_val = _li("mmrc_grade")
        dist_val = _li("mwt_distance")

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("VEMS % prédit", f"{fev1_val}%" if fev1_val else "—")
        with c2: st.metric("mMRC", str(mmrc_val) if mmrc_val is not None else "—")
        with c3: st.metric("6MWT", f"{dist_val} m" if dist_val else "—")
        with c4: st.metric("IMC", f"{bmi_val}" if bmi_val else "—")

        bode_score=""; bode_interp=""
        if any(v is not None for v in [fev1_val,mmrc_val,dist_val,bmi_val]):
            bode_r = compute_bode(fev1_val,mmrc_val,dist_val,bmi_val)
            st.markdown(f'<div class="score-box" style="background:{bode_r["color"]};">'
                        f'BODE : {bode_r["score"]}/10 — {bode_r["interpretation"]}'
                        f'  <small>({bode_r["survival"]})</small></div>', unsafe_allow_html=True)
            bode_score=bode_r["score"]; bode_interp=bode_r["interpretation"]

        return {"bmi":bmi_val or "",
                "bode_score":bode_score,"bode_interpretation":bode_interp}

    @classmethod
    def is_filled(cls, bilan_data):
        v = str(bilan_data.get("bode_score","")).strip()
        return v not in ("","None","nan")

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals=[]
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("bode_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp=[labels[i] for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        fig=go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="BODE /10",
                line=dict(color="#C4603A",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}/10" for v in yp],textposition="top center"))
        for y,color,label in [(2,"#388e3c","Q1"),(4,"#f57c00","Q2"),(6,"#e64a19","Q3")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,11],title="Score /10"),height=300,
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows=[{"Bilan":lbl,"BODE /10":row.get("bode_score","—"),
               "IMC":row.get("bmi","—"),"Pronostic":row.get("bode_interpretation","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("BODE Index — Pronostic BPCO (0–10)", styles["section"]))
        story.append(Paragraph("B=IMC · O=Obstruction (VEMS%) · D=Dyspnée (mMRC) · E=Exercice (6MWT)", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        # Tableau de cotation
        rows = [
            ["Composante","Valeur mesurée","Points 0","Points 1","Points 2","Points 3","Score"],
            ["B — IMC (kg/m²)","_____","> 21","≤ 21","","","_____"],
            ["O — VEMS % prédit","_____","≥ 65","50–64","36–49","≤ 35","_____"],
            ["D — mMRC dyspnée","_____","0–1","2","3","4","_____"],
            ["E — 6MWT (mètres)","_____","≥ 350","250–349","150–249","≤ 149","_____"],
        ]
        t = Table(rows, colWidths=[3.8*cm,2.8*cm,2*cm,2*cm,2*cm,2*cm,2.4*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        sc = Table([["BODE Score Total : _____ / 10"]], colWidths=[17*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),12),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph("0–2 : survie 80% à 4 ans  ·  3–4 : 67%  ·  5–6 : 57%  ·  7–10 : 18%", styles["note"]))

