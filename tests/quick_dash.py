"""tests/quick_dash.py — QuickDASH (11 items)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

QDASH_ITEMS = [
    ("qd_1",  "Ouvrir un pot ou un bocal"),
    ("qd_2",  "Faire des tâches ménagères lourdes (laver les murs, les planchers)"),
    ("qd_3",  "Porter un sac à provisions ou une mallette"),
    ("qd_4",  "Se laver le dos"),
    ("qd_5",  "Utiliser un couteau pour couper des aliments"),
    ("qd_6",  "Activités de loisirs nécessitant peu d'effort (jouer aux cartes, tricoter)"),
    ("qd_7",  "Activités de loisirs provoquant des douleurs à votre bras, épaule ou main"),
    ("qd_8",  "Activités de loisirs nécessitant des mouvements libres du bras, épaule ou main"),
    ("qd_9",  "Difficultés à dormir à cause de douleurs de votre bras, épaule ou main"),
    ("qd_10", "Engourdissements ou picotements de votre bras, épaule ou main"),
    ("qd_11", "Difficultés dans votre travail ou activités quotidiennes habituelles"),
]
QDASH_OPTS = ["— Non renseigné —",
              "1 — Aucune difficulté",
              "2 — Légère difficulté",
              "3 — Difficulté modérée",
              "4 — Difficulté importante",
              "5 — Incapable"]

def _compute_qdash(answers):
    vals = [answers[k] for k in [i[0] for i in QDASH_ITEMS] if k in answers]
    if len(vals) < 10: return None
    return round((sum(vals)/len(vals) - 1) * 25, 1)

@register_test
class QuickDASH(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"quick_dash","nom":"QuickDASH","tab_label":"✋ QuickDASH",
                "categorie":"questionnaire","tags":["épaule", "coude", "poignet", "membre supérieur", "incapacité"],
                "description":"Disabilities of the Arm, Shoulder and Hand — épaule, coude, poignet — version courte 11 items /100"}

    @classmethod
    def fields(cls):
        return [i[0] for i in QDASH_ITEMS] + ["qdash_score","qdash_interpretation"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score total (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
            {"key": "detail_items", "label": "Détail des items", "default": False},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">QuickDASH — Incapacité du membre supérieur</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">11 questions sur la difficulté à réaliser des activités. '
                    'Seuil clinique significatif : > 10/100</div>', unsafe_allow_html=True)
        answers = {}; collected = {}
        for key, text in QDASH_ITEMS:
            stored = lv(key, "")
            idx = 0
            if stored not in ("", None):
                try: idx = int(float(stored))
                except: idx = 0
            chosen = st.radio(f"**{text}**", QDASH_OPTS, index=idx,
                              horizontal=True, key=f"{key_prefix}_{key}")
            if chosen == "— Non renseigné —":
                collected[key] = ""
            else:
                v = int(chosen.split(" — ")[0]); answers[key] = v; collected[key] = v

        score = _compute_qdash(answers)
        if score is not None:
            color = "#388e3c" if score <= 20 else "#f57c00" if score <= 40 else "#d32f2f"
            interp = ("Incapacité légère" if score <= 20
                      else "Incapacité modérée" if score <= 40
                      else "Incapacité sévère")
            st.markdown(f'<div class="score-box" style="background:{color};">'
                        f'QuickDASH : {score}/100 — {interp}</div>', unsafe_allow_html=True)
        collected.update({"qdash_score": score if score is not None else "",
                          "qdash_interpretation": interp if score is not None else ""})
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("qdash_score","")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import plotly.graph_objects as go, pandas as pd
        vals = []
        for _, row in bilans_df.iterrows():
            try:
                import math; f = float(row.get("qdash_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                line=dict(color="#2B57A7",width=2.5), marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp], textposition="top center"))
        for y,c,l in [(10,"#388e3c","10 légère"),(40,"#f57c00","40 modérée")]:
            fig.add_hline(y=y, line_dash="dot", line_color=c,
                          annotation_text=l, annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="QuickDASH /100"),
                          height=300, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_print_controls:
            _key = cls._print_chart_key('quick_dash', cas_id)
            cls._render_print_checkbox(_key)
            cls._store_chart(_key, fig, cas_id)
        table_rows = [
            {"label": "QuickDASH", "col_key": "qdash_score",
             "values": [r.get("qdash_score","—") for _,r in bilans_df.iterrows()]},
            {"label": "Incapacité", "col_key": "qdash_interpretation",
             "values": [r.get("qdash_interpretation","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows = [{"Bilan":lbl,"QuickDASH":row.get("qdash_score","—"),
                             "Incapacité":row.get("qdash_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("QuickDASH — Disabilities of the Arm, Shoulder and Hand", styles["section"]))
        story.append(Paragraph(
            "11 questions sur les difficultes fonctionnelles du membre superieur durant la semaine "
            "ecoule. Score 0-100 (100 = incapacite maximale).", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],
                    colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
                                  ("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        questions = [
            "1. Ouvrir un pot hermetique neuf ou visse",
            "2. Effectuer des taches menageres lourdes (laver planchers, murs)",
            "3. Porter un sac de provisions ou une mallette",
            "4. Se laver le dos",
            "5. Utiliser un couteau pour couper la nourriture",
            "6. Loisirs necessitant effort ou chocs au bras, epaule, main",
            "7. Douleur au bras, epaule ou main",
            "8. Fourmillements dans bras, epaule ou main",
            "9. Faiblesse dans bras, epaule ou main",
            "10. Raideur dans bras, epaule ou main",
            "11. Difficulte a dormir a cause des douleurs",
        ]
        cols_hdr = ["Question","1 Aucune","2 Peu","3 Moderee","4 Grande","5 Incapable"]
        rows = [cols_hdr]
        for q in questions:
            rows.append([q,"O","O","O","O","O"])
        t = Table(rows, colWidths=[7.5*cm,1.85*cm,1.85*cm,1.85*cm,1.85*cm,2.1*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
            ("ALIGN",(1,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        sc = Table([["Score QuickDASH = [(Somme/11) - 1] x 25 = _____ / 100"]], colWidths=[17*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),11),
            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph(
            "Formule : Score = [(Somme des 11 items / 11) - 1] x 25  |  >= 1 item manquant = invalide",
            styles["note"]))

