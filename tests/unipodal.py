"""tests/unipodal.py — Équilibre unipodal (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

@register_test
class Unipodal(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"unipodal","nom":"Équilibre unipodal","tab_label":"🦶 Unipodal",
                "categorie":"test_clinique","tags":["équilibre", "unipodal", "chute", "âgé"],"description":"Maintien sur un pied (max 30 sec), seuil < 5 sec"}

    @classmethod
    def fields(cls):
        return ["unipodal_d_ouvert","unipodal_g_ouvert","unipodal_d_ferme","unipodal_g_ferme"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "yeux_ouverts", "label": "Yeux ouverts D/G (s)", "default": True},
            {"key": "yeux_fermes", "label": "Yeux fermés D/G (s)", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">Équilibre unipodal (secondes)</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">Temps de maintien sur un pied (max 30 sec). '
                    'Seuil : &lt; 5 sec = risque de chute élevé.</div>', unsafe_allow_html=True)

        def _load(key):
            v = lv(key,None)
            try: return float(v) if v not in (None,"","None") else None
            except: return None

        u1, u2 = st.columns(2)
        with u1:
            st.markdown("**Yeux ouverts**")
            u_do = st.number_input("Côté droit (sec)",0.0,30.0,_load("unipodal_d_ouvert"),0.5,
                                   key=f"{key_prefix}_udo",help="0 = non mesuré")
            u_go = st.number_input("Côté gauche (sec)",0.0,30.0,_load("unipodal_g_ouvert"),0.5,
                                   key=f"{key_prefix}_ugo",help="0 = non mesuré")
        with u2:
            st.markdown("**Yeux fermés**")
            u_df = st.number_input("Côté droit (sec)",0.0,30.0,_load("unipodal_d_ferme"),0.5,
                                   key=f"{key_prefix}_udf",help="0 = non mesuré")
            u_gf = st.number_input("Côté gauche (sec)",0.0,30.0,_load("unipodal_g_ferme"),0.5,
                                   key=f"{key_prefix}_ugf",help="0 = non mesuré")
        for val,label in [(u_do,"D ouvert"),(u_go,"G ouvert"),(u_df,"D fermé"),(u_gf,"G fermé")]:
            if val and val > 0:
                color = "#388e3c" if val >= 10 else "#f57c00" if val >= 5 else "#d32f2f"
                st.markdown(f'<small style="color:{color}">● {label} : {val}s</small>',
                            unsafe_allow_html=True)
        return {"unipodal_d_ouvert":u_do or "","unipodal_g_ouvert":u_go or "",
                "unipodal_d_ferme":u_df or "","unipodal_g_ferme":u_gf or ""}

    @classmethod
    def is_filled(cls, bilan_data):
        for k in ("unipodal_d_ouvert","unipodal_g_ouvert"):
            try:
                if float(bilan_data.get(k,"")) > 0: return True
            except: pass
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key,label,color in [("unipodal_d_ouvert","D ouvert","#2B57A7"),
                                  ("unipodal_g_ouvert","G ouvert","#C4603A")]:
            vals = []
            for _,row in bilans_df.iterrows():
                try:
                    import math; f=float(row.get(key,""))
                    vals.append(None if not math.isfinite(f) or f<=0 else f)
                except: vals.append(None)
            xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v]
            yp = [v for v in vals if v is not None and v==v]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=label,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[f"{v:.1f}s" for v in yp],textposition="top center"))
        for y,color,label in [(5,"#d32f2f","5s seuil risque"),(10,"#f57c00","10s")]:
            fig.add_hline(y=y,line_dash="dot",line_color=color,
                          annotation_text=label,annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,32],title="Secondes"),height=320,
                          legend=dict(orientation="h",y=-0.2),
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,
                 "D ouvert":row.get("unipodal_d_ouvert","—"),"G ouvert":row.get("unipodal_g_ouvert","—"),
                 "D fermé":row.get("unipodal_d_ferme","—"),"G fermé":row.get("unipodal_g_ferme","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Équilibre Unipodal (secondes)", styles["section"]))
        story.append(Paragraph("Maintenir l'équilibre sur un pied — yeux ouverts puis yeux fermés. 3 essais max par côté.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.4*cm))
        headers = ["Condition", "Pied Droit (s)", "Pied Gauche (s)", "Interprétation"]
        rows = [headers,
                ["Yeux ouverts","___________","___________",""],
                ["Yeux fermés", "___________","___________",""]]
        t = Table(rows, colWidths=[5*cm,4*cm,4*cm,4*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),10),
            ("FONTNAME",(0,0),(3,0),"Helvetica-Bold"),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),
            ("GRID",(0,0),(-1,-1),0.3,LINE),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        story.append(t)
        story.append(Spacer(1,0.3*cm))
        story.append(Paragraph("Normes yeux ouverts : adulte sain > 30 s  ·  > 60 ans : > 10 s  ·  Yeux fermés : > 10 s (adulte)", styles["note"]))
        story.append(Spacer(1,0.3*cm))
        story.append(Paragraph("Observations : "+"_"*60, styles["normal"]))

