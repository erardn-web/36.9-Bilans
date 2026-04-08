"""
tests/snif_pimax_pemax.py — SNIF/PImax/PEmax (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import interpret_mip_mep


def _safe_float(v):
    try: return float(v) if v not in (None,"","None") else None
    except: return None


@register_test
class SNIFPimaxPemax(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"snif_pimax_pemax","nom":"SNIF / PImax / PEmax",
                "tab_label":"💪 SNIF / PImax / PEmax","categorie":"test_clinique","tags":["respiratoire", "SHV", "force", "pression", "inspiration"],
                "description":"Forces musculaires respiratoires — mesurées et % prédit"}

    @classmethod
    def fields(cls):
        return ["snif_val","snif_pred","snif_pct",
                "pimax_val","pimax_pred","pimax_pct",
                "pemax_val","pemax_pred","pemax_pct",
                "snif_pimax_pemax_notes"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "tableau", "label": "SNIF / PImax / PEmax", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">💪 SNIF Test · PImax · PEmax</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">'
            '<strong>SNIF</strong> : Sniff Nasal Inspiratory Pressure. '
            '<strong>PImax</strong> : Pression Inspiratoire Maximale (MIP). '
            '<strong>PEmax</strong> : Pression Expiratoire Maximale (MEP). '
            'Valeur normale : ≥ 80% de la valeur prédite.</div>',
            unsafe_allow_html=True)

        collected = {}

        def muscle_row(label, key_val, key_pred, key_pct):
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                v = st.number_input(f"{label} — Mesuré (cmH₂O)",
                    value=_safe_float(lv(key_val,None)),
                    step=1.0, key=f"{key_prefix}_{key_val}")
            with sc2:
                p = st.number_input(f"{label} — Prédit (cmH₂O)",
                    value=_safe_float(lv(key_pred,None)),
                    step=1.0, key=f"{key_prefix}_{key_pred}")
            with sc3:
                if v and p:
                    pct, interp_txt, color = interpret_mip_mep(v, p)
                    st.metric(f"{label} % prédit", f"{pct:.0f}%" if pct else "—")
                    st.markdown(f'<small style="color:{color}">{interp_txt}</small>',
                                unsafe_allow_html=True)
                    collected[key_pct] = round(pct,1) if pct else ""
                else:
                    collected[key_pct] = ""
            collected[key_val]  = v or ""
            collected[key_pred] = p or ""

        muscle_row("SNIF",  "snif_val",  "snif_pred",  "snif_pct")
        st.markdown("---")
        muscle_row("PImax", "pimax_val", "pimax_pred", "pimax_pct")
        st.markdown("---")
        muscle_row("PEmax", "pemax_val", "pemax_pred", "pemax_pct")

        notes = st.text_area("Notes", value=str(lv("snif_pimax_pemax_notes","") or ""),
                             height=80, key=f"{key_prefix}_snif_notes")
        collected["snif_pimax_pemax_notes"] = notes
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        for k in ("snif_pct","pimax_pct","pemax_pct"):
            v = bilan_data.get(k,"")
            if str(v).strip() not in ("","0","0.0","None","nan"): return True
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key,label,color in [("snif_pct","SNIF % prédit","#2B57A7"),
                                  ("pimax_pct","PImax % prédit","#C4603A"),
                                  ("pemax_pct","PEmax % prédit","#388e3c")]:
            vals = []
            for _,row in bilans_df.iterrows():
                try:    vals.append(float(row.get(key,"")))
                except: vals.append(None)
            xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v and v>0]
            yp = [v for v in vals if v is not None and v==v and v>0]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=label,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[f"{v if v==v else 0}%" for v in yp if v==v],textposition="top center"))
        fig.add_hline(y=80,line_dash="dot",line_color="#388e3c",
                      annotation_text="80% normal",annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,130],title="% valeur prédite"),
                          height=350,legend=dict(orientation="h",y=-0.2),
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('snif_pimax_pemax', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "SNIF (cmH₂O)", "col_key": "snif_val",
             "values": [r.get("snif_val","—") for _,r in bilans_df.iterrows()]},
            {"label": "SNIF %", "col_key": "snif_pct",
             "values": [r.get("snif_pct","—") for _,r in bilans_df.iterrows()]},
            {"label": "PImax (cmH₂O)", "col_key": "pimax_val",
             "values": [r.get("pimax_val","—") for _,r in bilans_df.iterrows()]},
            {"label": "PImax %", "col_key": "pimax_pct",
             "values": [r.get("pimax_pct","—") for _,r in bilans_df.iterrows()]},
            {"label": "PEmax (cmH₂O)", "col_key": "pemax_val",
             "values": [r.get("pemax_val","—") for _,r in bilans_df.iterrows()]},
            {"label": "PEmax %", "col_key": "pemax_pct",
             "values": [r.get("pemax_pct","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan":lbl,
                             "SNIF (cmH₂O)":row.get("snif_val","—"),"SNIF %":row.get("snif_pct","—"),
                 "PImax (cmH₂O)":row.get("pimax_val","—"),"PImax %":row.get("pimax_pct","—"),
                 "PEmax (cmH₂O)":row.get("pemax_val","—"),"PEmax %":row.get("pemax_pct","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("SNIF — PiMax — PeMax : Force Musculaire Respiratoire", styles["section"]))
        story.append(Paragraph("Évaluation de la force inspiratoire et expiratoire maximale. 3 essais par mesure, retenir le meilleur.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        rows = [["Test","Essai 1","Essai 2","Essai 3","Retenu","Prédit","% Prédit"],
                ["SNIF (cmH₂O)","_____","_____","_____","_____","_____","_____ %"],
                ["PiMax (cmH₂O)","_____","_____","_____","_____","_____","_____ %"],
                ["PeMax (cmH₂O)","_____","_____","_____","_____","_____","_____ %"]]
        t = Table(rows, colWidths=[3.5*cm,2*cm,2*cm,2*cm,2*cm,2.5*cm,3*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        story.append(Paragraph("Valeurs de référence :", styles["subsection"]))
        ref_rows = [["Mesure","Femmes (cmH₂O)","Hommes (cmH₂O)","Seuil pathologique"],
                    ["SNIF","70 ± 24","122 ± 27","< 70 cmH₂O"],
                    ["PiMax","70–80","100–120","< 70 (F) / < 80 (H)"],
                    ["PeMax","90–100","150–160","< 80 (F) / < 100 (H)"]]
        t2 = Table(ref_rows, colWidths=[4.25*cm]*4)
        t2.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),8.5),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
        story.append(t2); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Notes / conditions de mesure : "+"_"*55, styles["normal"]))

