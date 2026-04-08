"""tests/tests_cliniques/classification_lombaire.py — Classification clinique SIN/ROM/EOR/MOM + Raisonnement (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

GROUPES_CLINIQUES = [
    ("—",  "— Non classifié —", ""),
    ("SIN","🔴 Groupe SIN",
     "Douleur intense (EVA > 7/10), haute irritabilité. La douleur persiste longtemps après l'arrêt du stimulus. "
     "→ Soulagement, techniques douces Grades I-II, éducation neuro-centrée."),
    ("ROM","🟠 Groupe ROM",
     "Douleur durant le mouvement, limitation marquée de la mobilité. "
     "→ Focus sur la récupération d'amplitude, favoriser le glissement tissulaire."),
    ("EOR","🟡 Groupe EOR",
     "Douleur uniquement en fin d'amplitude (End of Range). Faible irritabilité. "
     "→ Mobilisation intensive (dans la douleur), Grades III-IV pour la prolifération tissulaire."),
    ("MOM","🟢 Groupe MOM",
     "Momentary Pain : douleur brève lors d'une charge spécifique, disparaît instantanément. "
     "→ Renforcement fonctionnel, tests de provocation et désensibilisation."),
]
GROUPES_OPTIONS = [g[1] for g in GROUPES_CLINIQUES]
GROUPES_CODES   = [g[0] for g in GROUPES_CLINIQUES]
GROUPES_DESC    = {g[0]: g[2] for g in GROUPES_CLINIQUES}
GROUPES_COLORS  = {"SIN":"#d32f2f","ROM":"#f57c00","EOR":"#fbc02d","MOM":"#388e3c","—":"#888"}

@register_test
class ClassificationLombaire(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"classification_lombaire","nom":"Classification lombaire & Raisonnement",
                "tab_label":"🩺 Classification lombaire","categorie":"test_clinique","tags":["lombalgie", "classification", "SIN", "ROM", "raisonnement"],
                "description":"Classification SIN/ROM/EOR/MOM + raisonnement clinique + pronostic + plan"}

    @classmethod
    def fields(cls):
        return ["groupe_clinique","diag_notes","a_appreciation",
                "p_objectifs","p_traitement","p_frequence","p_duree","p_education","p_autogestion"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "classification", "label": "Classification", "default": True},
            {"key": "drapeaux", "label": "Drapeaux rouges", "default": True},
            {"key": "plan", "label": "Plan thérapeutique", "default": True},
        ]

    def render(self, lv, key_prefix):
        collected={}

        # ── Classification ────────────────────────────────────────────────────
        st.markdown('<div class="section-title">🩺 Classification clinique</div>', unsafe_allow_html=True)
        stored_g=lv("groupe_clinique","—")
        idx_g=GROUPES_OPTIONS.index(stored_g) if stored_g in GROUPES_OPTIONS else 0
        chosen_g=st.radio("Groupe clinique",GROUPES_OPTIONS,index=idx_g,
                           key=f"{key_prefix}_groupe",horizontal=True)
        code=GROUPES_CODES[GROUPES_OPTIONS.index(chosen_g)]
        if code!="—" and GROUPES_DESC.get(code):
            color=GROUPES_COLORS[code]
            st.markdown(f'<div class="info-box" style="border-left:4px solid {color};">'
                        f'{GROUPES_DESC[code]}</div>',unsafe_allow_html=True)
        collected["groupe_clinique"]=chosen_g

        st.markdown("---")

        # ── Raisonnement ──────────────────────────────────────────────────────
        st.markdown('<div class="section-title">Raisonnement clinique</div>', unsafe_allow_html=True)
        collected["diag_notes"]=st.text_area("Hypothèses / diagnostics différentiels",
            value=lv("diag_notes",""),height=200,key=f"{key_prefix}_diag",
            placeholder="Ex : Arguments en faveur d'un syndrome facettaire : extension plus douloureuse que flexion...")

        st.markdown("---")

        # ── Pronostic (A) ─────────────────────────────────────────────────────
        st.markdown('<div class="section-title">A — Pronostic</div>', unsafe_allow_html=True)
        collected["a_appreciation"]=st.text_area("Appréciation clinique",
            value=lv("a_appreciation",""),height=150,key=f"{key_prefix}_appr",
            placeholder="Pronostic favorable / réservé / défavorable... Facteurs favorables : ... Facteurs défavorables : ...")

        st.markdown("---")

        # ── Plan (P) ──────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">P — Plan thérapeutique</div>', unsafe_allow_html=True)
        pc1,pc2=st.columns(2)
        with pc1:
            collected["p_objectifs"]=st.text_area("Objectifs thérapeutiques",
                value=lv("p_objectifs",""),height=100,key=f"{key_prefix}_obj")
            collected["p_traitement"]=st.text_area("Modalités de traitement",
                value=lv("p_traitement",""),height=100,key=f"{key_prefix}_trait")
        with pc2:
            collected["p_frequence"]=st.text_input("Fréquence des séances",
                value=lv("p_frequence",""),key=f"{key_prefix}_freq")
            collected["p_duree"]=st.text_input("Durée prévue",
                value=lv("p_duree",""),key=f"{key_prefix}_duree")
            collected["p_education"]=st.text_area("Éducation du patient",
                value=lv("p_education",""),height=80,key=f"{key_prefix}_edu")
            collected["p_autogestion"]=st.text_area("Autogestion / exercices à domicile",
                value=lv("p_autogestion",""),height=80,key=f"{key_prefix}_auto")
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        g=bilan_data.get("groupe_clinique","")
        return bool(g and g not in ("—","— Non classifié —",""))

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import pandas as pd
        table_rows = [
            {"label": "Groupe", "col_key": "groupe_clinique",
             "values": [r.get("groupe_clinique","—") for _,r in bilans_df.iterrows()]},
        ]
        if show_print_controls:
            cls._render_table_with_checkboxes(table_rows, cas_id)
        else:
            rows=[{"Bilan":lbl,
                           "Groupe":row.get("groupe_clinique","—"),
               "Pronostic":str(row.get("a_appreciation",""))[:80]+"..." if len(str(row.get("a_appreciation","")))>80 else row.get("a_appreciation","—")}
              for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Classification Lombaire & Raisonnement Clinique", styles["section"]))
        story.append(Paragraph("SIN — ROM — EOR : Classification du comportement de la douleur et orientation thérapeutique.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        for section_title, items in [
            ("SIN — Sévérité, Irritabilité, Nature", [
                "Sévérité (EVN repos / effort) : _____ / _____",
                "Irritabilité : ☐ Faible  ☐ Modérée  ☐ Élevée",
                "Nature : ☐ Nociceptive  ☐ Neuropathique  ☐ Centrale  ☐ Mixte",
                "Facteur aggravant principal : "+"_"*40,
                "Facteur soulageant principal : "+"_"*40]),
            ("ROM — Comportement des mouvements", [
                "Direction préférentielle : ☐ Flexion  ☐ Extension  ☐ Latéroflexion  ☐ Aucune",
                "Centralisation / périphérisation : ☐ Centralise  ☐ Périphérise  ☐ Neutre",
                "Mouvement le plus limitant : "+"_"*40]),
            ("EOR — End of Range / résistance", [
                "Résistance en fin d'amplitude : ☐ Dur  ☐ Mou  ☐ Vide  ☐ Spasme",
                "Douleur en fin d'amplitude : ☐ Oui  ☐ Non"]),
            ("Raisonnement & Plan de traitement", [
                "Hypothèse principale : "+"_"*50,
                "Objectif prioritaire : "+"_"*50,
                "Approche thérapeutique : "+"_"*50])]:
            story.append(Paragraph(section_title, styles["subsection"]))
            for item in items:
                t = Table([[item]], colWidths=[17*cm])
                t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
                    ("LINEBELOW",(0,0),(-1,-1),0.3,LINE),("BOTTOMPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),3)]))
                story.append(t)
            story.append(Spacer(1,0.1*cm))

