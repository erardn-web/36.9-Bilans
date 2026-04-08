"""
tests/gazometrie.py — Gazométrie + Capnographie (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.shared_data import (
    GAZO_FIELDS, interpret_gazo, ETCO2_PATTERNS
)


def _safe_float(v):
    try: return float(v) if v not in (None,"","None") else None
    except: return None


@register_test
class Gazometrie(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"gazometrie","nom":"Gazométrie / Capnographie",
                "tab_label":"🧪 Gazométrie","categorie":"mesure","tags":["gazométrie", "CO2", "respiratoire", "SHV", "capnographie"],
                "description":"Gazométrie artérielle et capnographie ETCO₂"}

    @classmethod
    def fields(cls):
        return (["gazo_type"] + [f[0] for f in GAZO_FIELDS] + ["gazo_notes"]
                + ["etco2_repos","etco2_post_effort","etco2_pattern","etco2_notes"])

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "tableau", "label": "Valeurs gazométriques", "default": True},
        ]

    def render(self, lv, key_prefix):
        # ── Gazométrie ────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">🧪 Gazométrie</div>',unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">Valeurs normales : pH 7.35–7.45 · PaCO₂ 35–45 mmHg · '
            'PaO₂ 75–100 mmHg · HCO₃⁻ 22–26 mmol/L · SatO₂ ≥ 95%</div>',
            unsafe_allow_html=True)

        g_type_opts = ["— Non renseigné —","Artériel","Veineux","Capillaire","Non réalisé"]
        g_type_val  = str(lv("gazo_type","Non réalisé") or "Non réalisé")
        g_type_idx  = g_type_opts.index(g_type_val) if g_type_val in g_type_opts else 3
        gazo_type   = st.selectbox("Type de prélèvement", g_type_opts,
                                   index=g_type_idx, key=f"{key_prefix}_gazo_type")

        gc1, gc2 = st.columns(2)
        gazo_vals = {}
        for i,(fkey,flabel,fref) in enumerate(GAZO_FIELDS):
            col = gc1 if i%2==0 else gc2
            with col:
                raw    = lv(fkey, None)
                val_in = _safe_float(raw)
                entered = st.number_input(f"{flabel} ({fref})", value=val_in,
                                          step=0.1, format="%.2f",
                                          key=f"{key_prefix}_{fkey}")
                gazo_vals[fkey] = entered if entered != 0.0 else ""
                if entered and entered != 0.0:
                    ok, msg = interpret_gazo(fkey, entered)
                    if ok is not None:
                        color = "#388e3c" if ok else "#d32f2f"
                        st.markdown(f'<small style="color:{color}">{msg}</small>',
                                    unsafe_allow_html=True)

        gazo_notes = st.text_area("Notes / contexte", value=str(lv("gazo_notes","") or ""),
                                  height=80, key=f"{key_prefix}_gazo_notes")

        # ── Capnographie ──────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📈 Capnographie — ETCO₂</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">ETCO₂ normal au repos : <strong>35–45 mmHg</strong>. '
            'Valeur abaissée = hypocapnie = argument fort pour le SHV.</div>',
            unsafe_allow_html=True)

        ec1, ec2 = st.columns(2)
        with ec1:
            etco2_repos = st.number_input(
                "ETCO₂ au repos (mmHg)", min_value=0.0, max_value=80.0,
                value=_safe_float(lv("etco2_repos",None)),
                step=0.5, key=f"{key_prefix}_etco2_repos", help="0 = non mesuré")
            if etco2_repos and etco2_repos > 0:
                color = "#388e3c" if 35<=etco2_repos<=45 else "#f57c00" if etco2_repos>=30 else "#d32f2f"
                label = "Normal" if 35<=etco2_repos<=45 else "Hypocapnie" if etco2_repos<35 else "Hypercapnie"
                st.markdown(f'<small style="color:{color}">▶ {label}</small>',unsafe_allow_html=True)
        with ec2:
            etco2_effort = st.number_input(
                "ETCO₂ post-effort (mmHg)", min_value=0.0, max_value=80.0,
                value=_safe_float(lv("etco2_post_effort",None)),
                step=0.5, key=f"{key_prefix}_etco2_effort", help="0 = non mesuré")

        pat_opts  = ["— Non renseigné —"] + list(ETCO2_PATTERNS)
        pat_val   = str(lv("etco2_pattern","") or "")
        pat_idx   = pat_opts.index(pat_val) if pat_val in pat_opts else 0
        etco2_pat = st.selectbox("Pattern capnographique", pat_opts,
                                 index=pat_idx, key=f"{key_prefix}_etco2_pat")
        etco2_notes = st.text_area("Notes", value=str(lv("etco2_notes","") or ""),
                                   height=80, key=f"{key_prefix}_etco2_notes")

        collected = {"gazo_type": gazo_type, **gazo_vals, "gazo_notes": gazo_notes,
                     "etco2_repos": etco2_repos or "",
                     "etco2_post_effort": etco2_effort or "",
                     "etco2_pattern": etco2_pat,
                     "etco2_notes": etco2_notes}
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        for k in ("gazo_paco2","etco2_repos"):
            v = bilan_data.get(k,"")
            if str(v).strip() not in ("","0","0.0","None","nan"): return True
        gt = str(bilan_data.get("gazo_type","")).strip()
        return bool(gt) and gt not in ("— Non renseigné —","Non réalisé")

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go
        import pandas as pd
        fig = go.Figure()
        for key,label,color in [("gazo_paco2","PaCO₂ (mmHg)","#2B57A7"),
                                  ("etco2_repos","ETCO₂ repos (mmHg)","#C4603A")]:
            vals = []
            for _,row in bilans_df.iterrows():
                try:    vals.append(float(row.get(key,"")))
                except: vals.append(None)
            xp = [labels[i] for i,v in enumerate(vals) if v is not None and v==v and v>0]
            yp = [v for v in vals if v is not None and v==v and v>0]
            if xp:
                fig.add_trace(go.Scatter(x=xp,y=yp,mode="lines+markers+text",name=label,
                    line=dict(color=color,width=2.5),marker=dict(size=9),
                    text=[f"{v:.1f}" for v in yp],textposition="top center"))
        fig.add_hrect(y0=35,y1=45,fillcolor="#388e3c",opacity=0.08,
                      annotation_text="Norme ETCO₂ (35–45)")
        fig.update_layout(height=350,yaxis_title="mmHg",
                          plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('gazometrie', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "PaCO₂", "col_key": "gazo_paco2",
             "values": [r.get("gazo_paco2","—") for _,r in bilans_df.iterrows()]},
            {"label": "pH", "col_key": "gazo_ph",
             "values": [r.get("gazo_ph","—") for _,r in bilans_df.iterrows()]},
            {"label": "ETCO₂ repos", "col_key": "etco2_repos",
             "values": [r.get("etco2_repos","—") for _,r in bilans_df.iterrows()]},
            {"label": "Pattern", "col_key": "etco2_pattern",
             "values": [r.get("etco2_pattern","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan":lbl,"PaCO₂":row.get("gazo_paco2","—"),
                             "pH":row.get("gazo_ph","—"),
                 "ETCO₂ repos":row.get("etco2_repos","—"),
                 "Pattern":row.get("etco2_pattern","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Capnographie / Gazométrie", styles["section"]))
        story.append(Paragraph("Mesure du CO₂ expiré (EtCO₂) et paramètres gazométriques. Valeurs normales : EtCO₂ 35–45 mmHg, pH 7.35–7.45.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        rows = [["Paramètre","Valeur","Norme","Interprétation"],
                ["EtCO₂ (mmHg)","_____","35–45",""],
                ["FR (/min)","_____","12–20",""],
                ["SpO₂ (%)","_____","≥ 95",""],
                ["pH","_____","7.35–7.45",""],
                ["PaCO₂ (mmHg)","_____","35–45",""],
                ["PaO₂ (mmHg)","_____","80–100",""],
                ["HCO₃ (mmol/L)","_____","22–26",""]]
        t = Table(rows, colWidths=[4.5*cm,3*cm,3*cm,6.5*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
        story.append(t); story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Contexte (repos / effort / post-HVT) : "+"_"*45, styles["normal"]))
        story.append(Spacer(1,0.2*cm))
        story.append(Paragraph("Notes : "+"_"*70, styles["normal"]))

