"""tests/testing_global.py — Testing musculaire global (tous segments corporels)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

# ── Définition des groupes musculaires ───────────────────────────────────────

ZONES = {
    "mi": {
        "label": "🦵 Membres inférieurs",
        "muscles": [
            ("tg_hip_flex",   "Fléchisseurs hanche",      "Psoas-iliaque — flexion contre résistance"),
            ("tg_hip_ext",    "Extenseurs hanche",         "Grand fessier — extension contre résistance"),
            ("tg_hip_abd",    "Abducteurs hanche",         "Moyen fessier — abduction contre résistance"),
            ("tg_hip_add",    "Adducteurs hanche",         "Adducteurs — adduction contre résistance"),
            ("tg_hip_re",     "Rotateurs ext. hanche",     "Pelvi-trochantériens — rotation externe"),
            ("tg_hip_ri",     "Rotateurs int. hanche",     "TFL/Petit fessier — rotation interne"),
            ("tg_knee_ext",   "Extenseurs genou",          "Quadriceps — extension contre résistance"),
            ("tg_knee_flex",  "Fléchisseurs genou",        "Ischio-jambiers — flexion contre résistance"),
            ("tg_ankle_df",   "Dorsiflexeurs cheville",    "Tibial antérieur — dorsiflexion"),
            ("tg_ankle_pf",   "Fléchisseurs plantaires",   "Triceps sural — flexion plantaire"),
            ("tg_ankle_inv",  "Inverseurs cheville",       "Tibial postérieur — inversion"),
            ("tg_ankle_ev",   "Éverseurs cheville",        "Péroniers — éversion"),
            ("tg_toe_ext",    "Extenseurs orteils",        "Extenseurs orteils — extension"),
        ],
    },
    "ms": {
        "label": "💪 Membres supérieurs",
        "muscles": [
            ("tg_sh_flex",    "Fléchisseurs épaule",       "Deltoïde ant. / Grand pectoral — flexion"),
            ("tg_sh_ext",     "Extenseurs épaule",         "Grand dorsal / Deltoïde post. — extension"),
            ("tg_sh_abd",     "Abducteurs épaule",         "Deltoïde moy. / Supra-épineux — abduction"),
            ("tg_sh_add",     "Adducteurs épaule",         "Grand pectoral / Grand dorsal — adduction"),
            ("tg_sh_re",      "Rotateurs ext. épaule",     "Infra-épineux / Petit rond — rotation ext."),
            ("tg_sh_ri",      "Rotateurs int. épaule",     "Sous-scapulaire — rotation interne"),
            ("tg_elb_flex",   "Fléchisseurs coude",        "Biceps / Brachial — flexion"),
            ("tg_elb_ext",    "Extenseurs coude",          "Triceps — extension"),
            ("tg_pro",        "Pronateurs avant-bras",     "Rond pronateur — pronation"),
            ("tg_sup",        "Supinateurs avant-bras",    "Court supinateur — supination"),
            ("tg_wr_ext",     "Extenseurs poignet",        "Extenseurs radiaux / cubital post."),
            ("tg_wr_flex",    "Fléchisseurs poignet",      "Fléchisseurs radiaux / cubital ant."),
            ("tg_grip",       "Préhension main",           "Force de serrement (dynamomètre)"),
        ],
    },
    "tronc": {
        "label": "🫀 Tronc",
        "muscles": [
            ("tg_tr_flex",    "Fléchisseurs tronc",        "Droit abdominal — flexion du tronc"),
            ("tg_tr_ext",     "Extenseurs tronc",          "Paravertébraux — extension du tronc"),
            ("tg_tr_latd",    "Inclinateurs D",            "Carré des lombes / Obliques D"),
            ("tg_tr_latg",    "Inclinateurs G",            "Carré des lombes / Obliques G"),
            ("tg_tr_rotd",    "Rotateurs D",               "Obliques — rotation droite"),
            ("tg_tr_rotg",    "Rotateurs G",               "Obliques — rotation gauche"),
        ],
    },
    "cerv": {
        "label": "🦴 Cervical",
        "muscles": [
            ("tg_cv_flex",    "Fléchisseurs cerv.",        "Long du cou / SCM — flexion"),
            ("tg_cv_ext",     "Extenseurs cerv.",          "Trapèze sup. / Splénius — extension"),
            ("tg_cv_latd",    "Inclinateurs cerv. D",      "SCM / Scalènes D — inclinaison"),
            ("tg_cv_latg",    "Inclinateurs cerv. G",      "SCM / Scalènes G — inclinaison"),
            ("tg_cv_rotd",    "Rotateurs cerv. D",         "SCM controlatéral / Splénius — rotation D"),
            ("tg_cv_rotg",    "Rotateurs cerv. G",         "SCM controlatéral / Splénius — rotation G"),
        ],
    },
}

MRC_OPTS = [None, 0, 1, 2, 3, 4, 5]
MRC_FMT  = {None: "—", 0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5"}
MRC_COLORS = ["#d32f2f","#e64a19","#f57c00","#f9a825","#8bc34a","#388e3c"]

def _mrc_color(v):
    if v is None: return "#888"
    return MRC_COLORS[min(int(v), 5)]

def _all_fields():
    fields = []
    for zone_id, zone in ZONES.items():
        for key, label, desc in zone["muscles"]:
            fields += [f"{key}_d", f"{key}_g"]
    fields += ["tg_notes"]
    return fields


@register_test
class TestingGlobal(BaseTest):

    @classmethod
    def meta(cls):
        return {
            "id":          "testing_global",
            "nom":         "Testing musculaire global",
            "tab_label":   "🏋️ Testing global",
            "categorie":   "test_clinique",
            "tags":        ["testing", "force", "MRC", "musculaire", "bilan"],
            "description": "Testing musculaire MRC 0–5 par zone : MI, MS, tronc, cervical",
        }

    @classmethod
    def fields(cls):
        return _all_fields()

    @classmethod
    def print_options(cls):
        return [
            {"key": "zone_mi",    "label": "Membres inférieurs",  "default": True},
            {"key": "zone_ms",    "label": "Membres supérieurs",  "default": True},
            {"key": "zone_tronc", "label": "Tronc",               "default": True},
            {"key": "zone_cerv",  "label": "Cervical",            "default": True},
            {"key": "notes",      "label": "Notes",               "default": True},
        ]

    def render(self, lv, key_prefix):

        def _li(k):
            v = lv(k, None)
            if v is None or str(v).strip() in ("", "None"): return None
            try: return int(float(v))
            except: return None

        collected = {}

        for zone_id, zone in ZONES.items():
            with st.expander(zone["label"], expanded=False):
                h0, hd, hg = st.columns([3, 1, 1])
                h0.markdown("**Muscle / Mouvement**")
                hd.markdown("**Droit**")
                hg.markdown("**Gauche**")
                st.markdown("---")

                for key, label, desc in zone["muscles"]:
                    c0, cd, cg = st.columns([3, 1, 1])
                    c0.markdown(f"**{label}**")
                    c0.markdown(
                        f"<small style='color:#888'>{desc}</small>",
                        unsafe_allow_html=True)

                    for side, col in [("d", cd), ("g", cg)]:
                        k = f"{key}_{side}"
                        with col:
                            chosen = st.select_slider(
                                "", options=MRC_OPTS, value=_li(k),
                                format_func=lambda x: MRC_FMT.get(x, str(x)),
                                key=f"{key_prefix}_{k}",
                                label_visibility="collapsed")
                        if chosen is not None:
                            col.markdown(
                                f'<span style="color:{_mrc_color(chosen)};font-weight:600">'
                                f'{chosen}/5</span>',
                                unsafe_allow_html=True)
                        collected[k] = "" if chosen is None else chosen

        collected["tg_notes"] = st.text_area(
            "Notes générales", value=lv("tg_notes", ""),
            height=80, key=f"{key_prefix}_tg_notes")
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        return any(
            str(bilan_data.get(f"{key}_d", "")).strip() not in ("", "None", "nan")
            for zone in ZONES.values()
            for key, _, _ in zone["muscles"]
        )

    @classmethod
    def score(cls, data):
        # Calculer le score moyen global (pour dashboard)
        vals = []
        for zone in ZONES.values():
            for key, _, _ in zone["muscles"]:
                for side in ("d", "g"):
                    v = data.get(f"{key}_{side}", "")
                    try:
                        vals.append(float(v))
                    except: pass
        if not vals: return {"score": None, "interpretation": "", "color": "#888888", "details": {}}
        avg = round(sum(vals) / len(vals), 1)
        color = "#388e3c" if avg >= 4 else "#f57c00" if avg >= 3 else "#d32f2f"
        return {"score": avg, "interpretation": f"Force moyenne : {avg}/5", "color": color, "details": {}}

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=""):
        import plotly.graph_objects as go
        import pandas as pd

        # Graphique : score moyen par zone et par bilan
        zone_scores = {}
        for zone_id, zone in ZONES.items():
            scores = []
            for _, row in bilans_df.iterrows():
                vals = []
                for key, _, _ in zone["muscles"]:
                    for side in ("d", "g"):
                        v = row.get(f"{key}_{side}", "")
                        try: vals.append(float(v))
                        except: pass
                scores.append(round(sum(vals)/len(vals), 1) if vals else None)
            zone_scores[zone_id] = scores

        COLORS = {"mi": "#2B57A7", "ms": "#C4603A", "tronc": "#1D9E75", "cerv": "#7F77DD"}
        fig = go.Figure()
        has_data = False
        for zone_id, scores in zone_scores.items():
            xp = [labels[i] for i, v in enumerate(scores) if v is not None]
            yp = [v for v in scores if v is not None]
            if xp:
                has_data = True
                fig.add_trace(go.Scatter(
                    x=xp, y=yp, mode="lines+markers+text",
                    name=ZONES[zone_id]["label"],
                    line=dict(color=COLORS[zone_id], width=2),
                    marker=dict(size=8),
                    text=[f"{v}" for v in yp],
                    textposition="top center"))

        if has_data:
            fig.add_hline(y=3, line_dash="dot", line_color="#f57c00",
                          annotation_text="3/5 seuil", annotation_position="right")
            fig.update_layout(
                yaxis=dict(range=[0, 5.5], title="MRC moyen /5"),
                height=380, plot_bgcolor="white", paper_bgcolor="white",
                title="Testing musculaire — Score MRC moyen par zone",
                legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)
            if show_print_controls:
                _key = cls._print_chart_key("global", cas_id)
                cls._render_print_checkbox(_key, "🖨️ Inclure ce graphique dans le PDF")
                cls._store_chart(_key, fig, cas_id)

        # Tableau par zone dans accordéons
        st.markdown("---")
        for zone_id, zone in ZONES.items():
            # Vérifier si ce zone a des données
            has_data = any(
                str(r.get(f"{key}_d", "") or "").strip() not in ("", "None", "nan")
                for _, r in bilans_df.iterrows()
                for key, _, _ in zone["muscles"]
            )
            with st.expander(zone["label"] + (" ✅" if has_data else " —"), expanded=False):
                rows = []
                for key, label, _ in zone["muscles"]:
                    row_data = {"Muscle": label}
                    for i, (_, bilan_row) in enumerate(bilans_df.iterrows()):
                        vd = str(bilan_row.get(f"{key}_d", "") or "").strip() or "—"
                        vg = str(bilan_row.get(f"{key}_g", "") or "").strip() or "—"
                        row_data[f"{labels[i]} D"] = vd
                        row_data[f"{labels[i]} G"] = vg
                    rows.append(row_data)

                if show_print_controls:
                    table_rows = []
                    for key, label, _ in zone["muscles"]:
                        for side, side_lbl in [("d", "D"), ("g", "G")]:
                            col_key = f"{key}_{side}"
                            table_rows.append({
                                "label": f"{label} {side_lbl}",
                                "col_key": col_key,
                                "values": [str(r.get(col_key, "") or "—")
                                           for _, r in bilans_df.iterrows()],
                            })
                    cls._render_table_with_checkboxes(table_rows, cas_id + f"_{zone_id}")
                else:
                    st.dataframe(pd.DataFrame(rows),
                                 use_container_width=True, hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        LINE = colors.HexColor("#CCCCCC")
        BLEU = colors.HexColor("#2B57A7")

        story.append(Paragraph("Testing Musculaire Global (MRC 0–5)", styles["section"]))
        story.append(Paragraph(
            "0 = aucune contraction  ·  1 = contraction visible sans mouvement  ·  "
            "2 = actif sans pesanteur  ·  3 = actif contre pesanteur  ·  "
            "4 = résistance réduite  ·  5 = résistance normale",
            styles["intro"]))

        hdr = Table(
            [["Patient : " + "_" * 28, "Date : " + "_" * 14, "Praticien : " + "_" * 14]],
            colWidths=[8*cm, 4.5*cm, 4.5*cm])
        hdr.setStyle(TableStyle([
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#555"))]))
        story.append(hdr)
        story.append(Spacer(1, 0.3*cm))

        for zone_id, zone in ZONES.items():
            story.append(Paragraph(zone["label"], styles["subsection"]))
            rows = [["Muscle / Mouvement", "D (0–5)", "G (0–5)", "Notes"]]
            for key, label, desc in zone["muscles"]:
                rows.append([f"{label}\n{desc}", "_____", "_____", ""])
            t = Table(rows, colWidths=[8*cm, 2*cm, 2*cm, 5*cm])
            t.setStyle(TableStyle([
                ("FONTSIZE",      (0,0), (-1,-1), 8.5),
                ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#E8EEF9")),
                ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
                ("GRID",          (0,0), (-1,-1), 0.3, LINE),
                ("TOPPADDING",    (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                ("ALIGN",         (1,0), (2,-1),  "CENTER"),
                ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.2*cm))
