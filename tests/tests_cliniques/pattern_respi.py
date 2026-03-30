"""
tests/tests_cliniques/pattern_respi.py — Pattern respiratoire (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import (
    PATTERN_MODES, PATTERN_AMPLITUDES, PATTERN_RYTHMES
)


@register_test
class PatternRespi(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"pattern_respi","nom":"Pattern respiratoire",
                "tab_label":"🔬 Pattern respi.","categorie":"mesure","tags":["respiratoire", "SHV", "pattern", "rythme", "mode"],
                "description":"FR, amplitude, mode ventilatoire, rythme"}

    @classmethod
    def fields(cls):
        return ["pattern_frequence","pattern_amplitude","pattern_mode",
                "pattern_rythme","pattern_notes"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🔬 Pattern respiratoire</div>',
                    unsafe_allow_html=True)

        def radio_load(label, opts, data_key, widget_key):
            opts_with_empty = ["— Non renseigné —"] + list(opts)
            val = str(lv(data_key,"") or "")
            idx = opts_with_empty.index(val) if val in opts_with_empty else 0
            chosen = st.radio(label, opts_with_empty, index=idx, key=widget_key)
            return "" if chosen == "— Non renseigné —" else chosen

        pc1, pc2 = st.columns(2)
        with pc1:
            stored_freq = lv("pattern_frequence",None)
            try:    default_freq = int(float(stored_freq)) if stored_freq not in (None,"","None") else None
            except: default_freq = None
            pat_freq = st.number_input(
                "Fréquence respiratoire (cycles/min)", min_value=0, max_value=60,
                value=default_freq, step=1, key=f"{key_prefix}_pat_freq",
                help="Laisser à 0 si non mesuré")
            if pat_freq is not None and pat_freq > 0:
                color = "#388e3c" if 12<=pat_freq<=18 else "#f57c00" if pat_freq<=20 else "#d32f2f"
                st.markdown(f'<small style="color:{color}">Normale : 12–18 · Tachypnée : &gt; 20</small>',
                            unsafe_allow_html=True)
            pat_amp = radio_load("Amplitude", PATTERN_AMPLITUDES,
                                 "pattern_amplitude", f"{key_prefix}_pat_amp")
        with pc2:
            pat_mode = radio_load("Mode ventilatoire", PATTERN_MODES,
                                  "pattern_mode", f"{key_prefix}_pat_mode")
            pat_ryt  = radio_load("Rythme", PATTERN_RYTHMES,
                                  "pattern_rythme", f"{key_prefix}_pat_ryt")

        pat_notes = st.text_area("Observations cliniques",
                                 value=str(lv("pattern_notes","") or ""),
                                 height=100, key=f"{key_prefix}_pat_notes")

        return {
            "pattern_frequence": pat_freq if pat_freq else "",
            "pattern_amplitude": pat_amp,
            "pattern_mode":      pat_mode,
            "pattern_rythme":    pat_ryt,
            "pattern_notes":     pat_notes,
        }

    @classmethod
    def is_filled(cls, bilan_data):
        for k in ("pattern_frequence","pattern_mode","pattern_amplitude"):
            v = bilan_data.get(k,"")
            if str(v).strip() not in ("","0","None","nan"): return True
        return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go
        import pandas as pd
        vals = []
        for _,row in bilans_df.iterrows():
            try:
                import math; f=float(row.get("pattern_frequence",""))
                vals.append(None if math.isnan(f) else f)
            except: vals.append(None)
        fig = go.Figure()
        xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v and v>0]
        yp = [v for v in vals if v is not None and v==v and v>0]
        if xp:
            fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name="FR (cycles/min)",
                line=dict(color="#2B57A7",width=2.5),marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp if v==v],textposition="top center"))
        fig.add_hrect(y0=12,y1=18,fillcolor="#388e3c",opacity=0.1,annotation_text="Normale 12–18")
        fig.update_layout(height=300,yaxis=dict(range=[0,35],title="Cycles/min"),
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        rows = [{"Bilan":lbl,"FR (cyc/min)":row.get("pattern_frequence","—"),
                 "Mode":row.get("pattern_mode","—"),
                 "Amplitude":row.get("pattern_amplitude","—"),
                 "Rythme":row.get("pattern_rythme","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Pattern Respiratoire — Observation Clinique", styles["section"]))
        story.append(Paragraph("Évaluation du mode et rythme respiratoire au repos et à l'effort.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        for label, opts in [
            ("Mode respiratoire :", ["☐ Costal supérieur  ☐ Diaphragmatique  ☐ Mixte  ☐ Paradoxal"]),
            ("Rythme au repos :", ["☐ Régulier  ☐ Irrégulier  ·  FR : _____ /min"]),
            ("Durée du cycle :", ["Inspiration : _____ s  ·  Pause : _____ s  ·  Expiration : _____ s"]),
            ("Signes d'hyperventilation :", ["☐ Soupirs fréquents  ☐ Respiration buccale  ☐ Apnées  ☐ Tension musculaire cervicale"]),
            ("Symétrie thoracique :", ["☐ Symétrique  ☐ Asymétrique (préciser) : "+"_"*30]),
            ("Respiration à l'effort :", ["Mode : ☐ Nasal  ☐ Buccal  ·  Adaptation : ☐ Adéquate  ☐ Inadéquate"])]:
            story.append(Paragraph(label, styles["normal"]))
            for opt in opts:
                t = Table([[opt]], colWidths=[17*cm])
                t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
                    ("LINEBELOW",(0,0),(-1,-1),0.3,LINE),("BOTTOMPADDING",(0,0),(-1,-1),6),
                    ("TOPPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),12)]))
                story.append(t)
            story.append(Spacer(1,0.1*cm))
        story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Observations complémentaires : "+"_"*55, styles["normal"]))

