"""tests/ases.py — ASES (American Shoulder and Elbow Surgeons)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

ASES_ACTIVITES = [
    ("ases_a1","Mettre un manteau"),
    ("ases_a2","Dormir du côté atteint"),
    ("ases_a3","Laver le dos / attacher le soutien-gorge"),
    ("ases_a4","Gérer l'hygiène personnelle (toilette)"),
    ("ases_a5","Se coiffer"),
    ("ases_a6","Atteindre une étagère haute"),
    ("ases_a7","Soulever 4,5 kg au-dessus de l'épaule"),
    ("ases_a8","Lancer un objet par-dessus la tête"),
    ("ases_a9","Faire son travail habituel"),
    ("ases_a10","Pratiquer son sport habituel"),
]
ASES_OPTS = ["— Non renseigné —",
             "0 — Incapable","1 — Très difficile","2 — Difficile","3 — Sans difficulté"]

@register_test
class ASES(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"ases","nom":"ASES","tab_label":"🏆 ASES",
                "categorie":"questionnaire","tags":["épaule", "membre supérieur", "fonctionnel", "douleur"],
                "description":"American Shoulder and Elbow Surgeons score /100 — douleur + fonction épaule"}

    @classmethod
    def fields(cls):
        return ["ases_eva_pain"] + [a[0] for a in ASES_ACTIVITES] + ["ases_score","ases_interpretation"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "score_total", "label": "Score ASES (/100)", "default": True},
            {"key": "interpretation", "label": "Interprétation", "default": True},
            {"key": "graphique", "label": "Graphique d'évolution", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">ASES — Score fonctionnel de l\'épaule</div>',
                    unsafe_allow_html=True)
        # Douleur EVA
        st.markdown("**Douleur (EVA 0–10)**")
        stored_pain = lv("ases_eva_pain","")
        try: default_pain = int(float(stored_pain)) if stored_pain not in ("","None") else None
        except: default_pain = None
        pain = st.select_slider("Douleur actuelle",
            options=[None]+list(range(11)),
            value=default_pain,
            format_func=lambda x: "— Non renseigné —" if x is None else str(x),
            key=f"{key_prefix}_ases_pain")

        st.markdown("**Activités fonctionnelles**")
        st.markdown('<div class="info-box"><small>0 = incapable · 1 = très difficile · '
                    '2 = difficile · 3 = sans difficulté</small></div>', unsafe_allow_html=True)

        answers = {}; collected = {"ases_eva_pain": pain if pain is not None else ""}
        a1, a2 = st.columns(2)
        for i, (key, text) in enumerate(ASES_ACTIVITES):
            stored = lv(key,"")
            idx = 0
            if stored not in ("","None"):
                try: idx = int(float(stored)) + 1
                except: pass
            with (a1 if i%2==0 else a2):
                chosen = st.selectbox(text, ASES_OPTS, index=idx,
                                      key=f"{key_prefix}_{key}")
            if chosen == "— Non renseigné —": collected[key] = ""
            else:
                v = int(chosen.split(" — ")[0]); answers[key] = v; collected[key] = v

        # Score ASES = (10 - EVA)/10*50 + (somme activités)/30*50
        score = None; interp = ""
        if pain is not None and len(answers) >= 8:
            pain_score = (10 - pain) / 10 * 50
            func_score = sum(answers.values()) / 30 * 50
            score = round(pain_score + func_score, 1)
            interp = ("Bon résultat" if score >= 70
                      else "Résultat modéré" if score >= 40
                      else "Mauvais résultat")
            color = "#388e3c" if score>=70 else "#f57c00" if score>=40 else "#d32f2f"
            st.markdown(f'<div class="score-box" style="background:{color};">'
                        f'ASES : {score}/100 — {interp}</div>', unsafe_allow_html=True)
        collected.update({"ases_score": score if score is not None else "",
                          "ases_interpretation": interp})
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        try: return float(bilan_data.get("ases_score","")) >= 0
        except: return False

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import plotly.graph_objects as go, pandas as pd
        vals = []
        for _, row in bilans_df.iterrows():
            try:
                import math; f = float(row.get("ases_score",""))
                vals.append(None if not math.isfinite(f) else f)
            except: vals.append(None)
        xp = [labels[i] for i,v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        fig = go.Figure()
        if xp:
            fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                line=dict(color="#C4603A",width=2.5), marker=dict(size=9),
                text=[f"{v:.0f}" for v in yp], textposition="top center"))
        for y,c,l in [(40,"#d32f2f","40 mauvais"),(70,"#388e3c","70 bon")]:
            fig.add_hline(y=y, line_dash="dot", line_color=c,
                          annotation_text=l, annotation_position="right")
        fig.update_layout(yaxis=dict(range=[0,105],title="ASES /100"),
                          height=300, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        rows = [{"Bilan":lbl,"ASES":row.get("ases_score","—"),
                 "Résultat":row.get("ases_interpretation","—")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("ASES — American Shoulder and Elbow Surgeons Score", styles["section"]))
        story.append(Paragraph("Score /100 : 50% douleur (EVA ×5) + 50% fonction (10 activités × 3 pts max).", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        # Douleur
        story.append(Paragraph("Partie 1 — Douleur", styles["subsection"]))
        story.append(Paragraph("Entourez le chiffre correspondant à votre douleur habituelle :", styles["normal"]))
        scale = Table([[" 0 "," 1 "," 2 "," 3 "," 4 "," 5 "," 6 "," 7 "," 8 "," 9 "," 10 "]],colWidths=[1.55*cm]*11)
        scale.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),13),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),("GRID",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
        story.append(scale)
        story.append(Paragraph("0 = aucune douleur   10 = douleur maximale imaginable", styles["note"]))
        story.append(Spacer(1,0.3*cm))
        # Fonction
        story.append(Paragraph("Partie 2 — Fonction (0 = incapable · 1 = difficile · 2 = avec difficulté · 3 = normal)", styles["subsection"]))
        activites = [
            "Mettre un manteau",
            "Dormir sur le côté atteint",
            "Se laver le dos / attacher le soutien-gorge dans le dos",
            "Utiliser les toilettes",
            "Se peigner les cheveux",
            "Atteindre une étagère haute",
            "Soulever 500 g au-dessus de l'épaule",
            "Lancer une balle en dessus (overarm)",
            "Effectuer son travail habituel",
            "Pratiquer son sport habituel",
        ]
        rows = [["#","Activité","0","1","2","3"]]
        for i, a in enumerate(activites, 1):
            rows.append([str(i), a, "☐","☐","☐","☐"])
        t = Table(rows, colWidths=[0.8*cm,10.7*cm,1.25*cm,1.25*cm,1.25*cm,1.75*cm])
        t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),8.5),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
            ("ALIGN",(2,0),(5,-1),"CENTER")]))
        story.append(t); story.append(Spacer(1,0.3*cm))
        sc = Table([["Score Douleur (EVA×5) : _____ / 50","Score Fonction (Σ×1.67) : _____ / 50","ASES Total : _____ / 100"]],
                   colWidths=[5.7*cm,5.7*cm,5.6*cm])
        sc.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),10),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,0),(-1,-1),BLEU),("BOX",(0,0),(-1,-1),0.5,LINE),("INNERGRID",(0,0),(-1,-1),0.5,LINE),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
        story.append(sc)
        story.append(Paragraph("Score douleur = (10 − EVA) × 5  ·  Score fonction = Σ activités × 1.6667", styles["note"]))

