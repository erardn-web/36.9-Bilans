"""tests/amplitudes_epaule.py — Amplitudes articulaires épaule"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

AMPLITUDES = [
    ("ep_flex",   "Flexion",              "0–180°",  0, 180),
    ("ep_ext",    "Extension",            "0–60°",   0, 90),
    ("ep_abd",    "Abduction",            "0–180°",  0, 180),
    ("ep_add",    "Adduction",            "0–50°",   0, 70),
    ("ep_re",     "Rotation externe",     "0–90°",   0, 120),
    ("ep_ri",     "Rotation interne",     "0–80°",   0, 100),
    ("ep_apley_d","Apley — Dos (cm)",     "cm",      0, 40),
    ("ep_apley_t","Apley — Tête (cm)",    "cm",      0, 40),
]
NORMAL_VALUES = {
    "ep_flex":60,"ep_ext":180,"ep_abd":180,"ep_add":50,
    "ep_re":90,"ep_ri":80,
}
SIDES = ["Droit","Gauche"]

@register_test
class AmplitudesEpaule(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"amplitudes_epaule","nom":"Amplitudes épaule","tab_label":"📐 Amplitudes épaule",
                "categorie":"test_clinique","tags":["épaule", "membre supérieur", "mobilité", "amplitude", "ROM"],
                "description":"Amplitudes articulaires épaule D/G (goniométrie) + Apley"}

    @classmethod
    def fields(cls):
        return [f"{k}_{s}" for k,_,_,_,_ in AMPLITUDES for s in ("d","g")] + ["ep_notes"]

    def render(self, lv, key_prefix):
        def _lf(k):
            v = lv(k, None)
            try: return float(v) if v not in (None,"","None") else None
            except: return None

        st.markdown('<div class="section-title">Amplitudes articulaires — Épaule</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box"><small>Valeurs normales entre parenthèses. '
                    'D = côté droit · G = côté gauche</small></div>', unsafe_allow_html=True)

        collected = {}
        h0, hd, hg = st.columns([3,1,1])
        h0.markdown("**Mouvement**"); hd.markdown("**Droit**"); hg.markdown("**Gauche**")
        st.markdown("---")

        for key, label, norms, min_v, max_v in AMPLITUDES:
            c0, cd, cg = st.columns([3,1,1])
            c0.markdown(f"**{label}** <small style='color:#888'>({norms})</small>",
                        unsafe_allow_html=True)
            for side, col in [("d", cd), ("g", cg)]:
                k = f"{key}_{side}"
                with col:
                    val = st.number_input("", min_value=float(min_v), max_value=float(max_v),
                        value=_lf(k), step=5.0 if "apley" not in key else 0.5,
                        key=f"{key_prefix}_{k}", label_visibility="collapsed")
                collected[k] = val if val is not None else ""

        notes = st.text_area("Notes", value=lv("ep_notes",""), height=60,
                             key=f"{key_prefix}_ep_notes")
        collected["ep_notes"] = notes
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        return any(str(bilan_data.get(f"{k}_d","")).strip() not in ("","None","nan","0.0","0")
                   for k,_,_,_,_ in AMPLITUDES[:4])

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go, pandas as pd
        move_keys = [("ep_flex","Flexion",180),("ep_abd","Abduction",180),
                     ("ep_re","Rot. ext.",90),("ep_ri","Rot. int.",80)]
        colors = {"d":"#2B57A7","g":"#C4603A"}
        for key, label, normal in move_keys:
            vals_d=[]; vals_g=[]
            for _,row in bilans_df.iterrows():
                try: vals_d.append(float(row.get(f"{key}_d",0) or 0))
                except: vals_d.append(0)
                try: vals_g.append(float(row.get(f"{key}_g",0) or 0))
                except: vals_g.append(0)
            if any(v>0 for v in vals_d+vals_g):
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Droit",x=labels,y=vals_d,
                    marker_color=colors["d"],text=[f"{v:.0f}°" if v>0 else "" for v in vals_d],
                    textposition="outside"))
                fig.add_trace(go.Bar(name="Gauche",x=labels,y=vals_g,
                    marker_color=colors["g"],text=[f"{v:.0f}°" if v>0 else "" for v in vals_g],
                    textposition="outside"))
                fig.add_hline(y=normal,line_dash="dot",line_color="#388e3c",
                              annotation_text=f"{normal}° normal",annotation_position="right")
                fig.update_layout(title=label,barmode="group",yaxis_title="°",
                                  height=280,plot_bgcolor="white",paper_bgcolor="white")
                st.plotly_chart(fig,use_container_width=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Amplitudes Articulaires — Épaule", styles["section"]))
        story.append(Paragraph("Mesure goniométrique des amplitudes articulaires. D = côté douloureux / G = côté sain.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        rows = [["Mouvement","Côté D (°)","Côté G (°)","Norme (°)","Douleur (0–10)"],
                ["Flexion","_____","_____","0–180","_____"],
                ["Extension","_____","_____","0–60","_____"],
                ["Abduction","_____","_____","0–180","_____"],
                ["Adduction","_____","_____","0–30","_____"],
                ["Rotation interne (bras au corps)","_____","_____","0–80","_____"],
                ["Rotation externe (bras au corps)","_____","_____","0–90","_____"],
                ["Rotation interne (ABD 90°)","_____","_____","0–70","_____"],
                ["Rotation externe (ABD 90°)","_____","_____","0–90","_____"],
                ["Élévation plan scapulaire","_____","_____","0–180","_____"],
                ["Main dans le dos (vertèbre)","_____","_____","T6–T8","_____"]]
        t = Table(rows, colWidths=[5.5*cm,2.2*cm,2.2*cm,2.2*cm,2.9*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
        story.append(t); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Arc douloureux : ☐ Absent  ☐ Présent (de _____ ° à _____ °)", styles["normal"]))
        story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Notes : "+"_"*70, styles["normal"]))

