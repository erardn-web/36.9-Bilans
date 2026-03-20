"""
Questionnaires imprimables — Bilan Lombalgie
ODI, Tampa Scale, Örebro
"""
import sys, os as _os
_here = _os.path.dirname(_os.path.abspath(__file__))
_root = _os.path.dirname(_here)
if _root not in sys.path: sys.path.insert(0, _root)


import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from datetime import date

from pdf_theme import (
    TERRA, BLEU, BLEU_LIGHT, GRIS, GRIS_BORD, BLANC, NOIR, GRIS_TEXTE,
    BLEU, ORANGE, ROUGE, USEFUL_W, MARGIN, make_header_footer, get_logo,
)
GRIS_CLAIR = GRIS
BLEU_CLAIR = BLEU_LIGHT
BLEU_FONCE = BLEU
BLEU_CLAIR = BLEU_LIGHT
W = USEFUL_W
CHECKBOX = "☐"

def make_styles():
    base = getSampleStyleSheet()
    return {
        "question": ParagraphStyle("q", fontSize=10, fontName="Helvetica-Bold",
                                   textColor=NOIR, spaceBefore=8, spaceAfter=3),
        "option":   ParagraphStyle("o", fontSize=9, fontName="Helvetica",
                                   textColor=NOIR, spaceAfter=2, leftIndent=20),
        "intro":    ParagraphStyle("i", fontSize=9, fontName="Helvetica-Oblique",
                                   textColor=colors.HexColor("#444"), spaceAfter=6),
        "small":    ParagraphStyle("sm", fontSize=8, fontName="Helvetica",
                                   textColor=colors.HexColor("#666")),
    }

def section_header(title, subtitle=""):
    tbl = Table([[Paragraph(title, ParagraphStyle("th", fontSize=13,
        fontName="Helvetica-Bold", textColor=BLANC))]], colWidths=[W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    items = [tbl]
    if subtitle:
        items.append(Paragraph(subtitle, ParagraphStyle("ts", fontSize=8,
            fontName="Helvetica-Oblique", textColor=colors.HexColor("#555"), spaceAfter=4)))
    return items


def radio_v(num, question, options, styles):
    q_text = f"{num}. {question}" if question else str(num)
    items = [Paragraph(q_text, styles["question"])]
    rows = [[Paragraph(f"{CHECKBOX}  {lbl}", styles["option"])] for lbl in options]
    tbl = Table(rows, colWidths=[W])
    tbl.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),20),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[BLANC, GRIS_CLAIR]),
        ("GRID",(0,0),(-1,-1),0.3,GRIS_BORD),
    ]))
    items.append(tbl)
    return KeepTogether(items)

def score_footer(label, max_score, guide):
    rows = [[f"Score : _______ / {max_score}", ""]]
    tbl = Table(rows, colWidths=[W/2, W/2])
    tbl.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("TEXTCOLOR",(0,0),(0,0),BLEU),
        ("BACKGROUND",(0,0),(-1,-1),BLEU_CLAIR),
        ("BOX",(0,0),(-1,-1),1,BLEU),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    return [tbl, Paragraph(guide, ParagraphStyle("ig", fontSize=7,
        fontName="Helvetica", textColor=colors.HexColor("#666"), spaceBefore=3))]

def build_odi(story, styles):
    story += section_header("Oswestry Disability Index (ODI)",
        "Fairbank & Pynsent, 2000 — Version française — 10 sections, score 0–100%")
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Cochez UNE SEULE case par section — celle qui décrit le mieux votre situation aujourd'hui.",
        styles["intro"]))
    sections = [
        ("1. Intensité de la douleur", [
            "Pas de douleur actuellement",
            "La douleur est très légère",
            "La douleur est modérée",
            "La douleur est assez sévère",
            "La douleur est très sévère",
            "La douleur est la pire imaginable",
        ]),
        ("2. Soins personnels (se laver, s'habiller)", [
            "Je me prends en charge normalement sans douleur supplémentaire",
            "Je me prends en charge normalement mais c'est très douloureux",
            "Se prendre en charge est douloureux — je suis lent(e) et prudent(e)",
            "J'ai besoin d'aide mais j'arrive à gérer la plupart de mes soins",
            "J'ai besoin d'aide chaque jour pour la plupart de mes soins",
            "Je ne m'habille pas, me lave avec difficulté et reste au lit",
        ]),
        ("3. Soulever des charges", [
            "Je peux soulever des charges lourdes sans douleur",
            "Je peux soulever des charges lourdes mais avec douleur",
            "La douleur m'empêche de soulever des charges lourdes du sol",
            "La douleur m'empêche de soulever des charges lourdes — je peux soulever du léger si bien placé",
            "Je peux soulever des charges très légères uniquement",
            "Je ne peux rien soulever ni porter",
        ]),
        ("4. Marche", [
            "La douleur ne m'empêche pas de marcher",
            "La douleur m'empêche de marcher plus d'un kilomètre",
            "La douleur m'empêche de marcher plus de 500 mètres",
            "La douleur m'empêche de marcher plus de 100 mètres",
            "Je ne marche qu'avec une canne ou des béquilles",
            "Je suis au lit et dois me traîner pour aller aux toilettes",
        ]),
        ("5. Position assise", [
            "Je peux rester assis(e) aussi longtemps que je veux sans douleur",
            "Je peux rester assis(e) aussi longtemps que je veux avec légère douleur",
            "La douleur m'empêche de rester assis(e) plus d'une heure",
            "La douleur m'empêche de rester assis(e) plus de 30 minutes",
            "La douleur m'empêche de rester assis(e) plus de 10 minutes",
            "La douleur m'empêche totalement de m'asseoir",
        ]),
        ("6. Position debout", [
            "Je peux rester debout aussi longtemps que je veux sans douleur",
            "Je peux rester debout aussi longtemps que je veux mais avec douleur",
            "La douleur m'empêche de rester debout plus d'une heure",
            "La douleur m'empêche de rester debout plus de 30 minutes",
            "La douleur m'empêche de rester debout plus de 10 minutes",
            "La douleur m'empêche totalement de rester debout",
        ]),
        ("7. Sommeil", [
            "Mon sommeil n'est jamais perturbé par la douleur",
            "Mon sommeil est parfois perturbé",
            "Je dors moins de 6 heures à cause de la douleur",
            "Je dors moins de 4 heures à cause de la douleur",
            "Je dors moins de 2 heures à cause de la douleur",
            "La douleur m'empêche totalement de dormir",
        ]),
        ("8. Vie sexuelle (si applicable)", [
            "Ma vie sexuelle est normale, sans douleur",
            "Ma vie sexuelle est normale mais douloureuse",
            "Ma vie sexuelle est presque normale mais très douloureuse",
            "Ma vie sexuelle est sévèrement limitée par la douleur",
            "Ma vie sexuelle est presque absente",
            "La douleur empêche toute vie sexuelle",
        ]),
        ("9. Vie sociale", [
            "Ma vie sociale est normale sans douleur supplémentaire",
            "Ma vie sociale est normale mais augmente ma douleur",
            "La douleur n'affecte pas les activités légères mais limite les activités énergiques",
            "La douleur a limité ma vie sociale — je sors moins souvent",
            "La douleur a limité ma vie sociale à ma maison",
            "Je n'ai pas de vie sociale à cause de la douleur",
        ]),
        ("10. Voyages / transports", [
            "Je peux voyager n'importe où sans douleur",
            "Je peux voyager n'importe où mais avec douleur",
            "La douleur est sévère mais je gère les trajets > 2 heures",
            "La douleur me limite à des trajets < 1 heure",
            "La douleur me limite à des trajets courts < 30 minutes",
            "La douleur m'empêche de voyager sauf pour des soins médicaux",
        ]),
    ]
    for title, options in sections:
        story.append(radio_v(title, "", options, styles))
        story.append(Spacer(1, 0.1*cm))
    story.append(Spacer(1, 0.4*cm))
    story += score_footer("ODI", 100,
        "0–20% : incapacité minimale  ·  21–40% : modérée  ·  41–60% : sévère  ·  61–80% : très sévère  ·  >80% : grabataire")

def build_tampa(story, styles):
    story += section_header("Tampa Scale for Kinesiophobia (TSK-17)",
        "Miller et al., 1991 — Version française — Score 17–68")
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Indiquez dans quelle mesure vous êtes en accord avec chaque affirmation. "
        "1 = Pas du tout d'accord  ·  2 = Plutôt pas d'accord  ·  3 = Plutôt d'accord  ·  4 = Tout à fait d'accord",
        styles["intro"]))
    scale = ["1 — Pas du tout d'accord","2 — Plutôt pas d'accord","3 — Plutôt d'accord","4 — Tout à fait d'accord"]
    items_text = [
        "J'ai peur de me blesser si je fais de l'exercice.",
        "Si j'essayais de surmonter ma douleur, celle-ci augmenterait.",
        "Mon corps me dit que quelque chose ne va pas vraiment.",
        "Ma blessure a mis mon corps en danger toute ma vie.",
        "Les gens ne prennent pas ma condition médicale assez au sérieux.",
        "Ma blessure a mis mon corps en danger de façon permanente.",
        "La douleur signifie toujours que j'ai subi une blessure.",
        "Simplement parce que quelque chose aggrave ma douleur ne signifie pas qu'elle est dangereuse. (R)",
        "J'ai peur de me blesser accidentellement.",
        "Le plus sûr est de faire attention à ne pas faire de mouvements inutiles.",
        "Je n'aurais pas autant de douleur si quelque chose de grave ne se passait pas.",
        "Bien que ma condition soit douloureuse, je me sentirais mieux si j'étais plus actif(ve). (R)",
        "La douleur me signale que je dois arrêter pour ne pas me blesser.",
        "Ce n'est pas sûr pour quelqu'un avec ma condition d'être physiquement actif(ve).",
        "Je risque trop facilement de me blesser.",
        "Même si quelque chose me fait très mal, je ne pense pas que ce soit dangereux. (R)",
        "Personne ne devrait faire d'exercice quand il souffre de douleur.",
    ]
    for i, txt in enumerate(items_text):
        story.append(radio_v(str(i+1), txt, scale, styles))
        story.append(Spacer(1, 0.1*cm))
    story.append(Spacer(1, 0.4*cm))
    story += score_footer("TSK-17", 68,
        "≤ 37 : kinésiophobie faible  ·  38–44 : modérée  ·  > 44 : élevée  (R) = items inversés")

def build_orebro(story, styles):
    story += section_header("Örebro Musculoskeletal Pain Questionnaire",
        "Linton & Hallden, 1998 — Dépistage du risque de chronicisation")
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Ce questionnaire évalue les facteurs pouvant influencer l'évolution de votre douleur. "
        "Pour les questions avec une échelle de 0 à 10, entourez le chiffre correspondant.",
        styles["intro"]))

    def scale_row(num, question):
        story.append(Paragraph(f"{num}. {question}", styles["question"]))
        nums = ["0","1","2","3","4","5","6","7","8","9","10"]
        tbl = Table([nums], colWidths=[(W)/11]*11)
        tbl.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
            ("FONTSIZE",(0,0),(-1,-1),10),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("GRID",(0,0),(-1,-1),0.5,GRIS_BORD),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[GRIS_CLAIR]),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.1*cm))

    scale_row("1","Quelle est l'intensité de votre douleur en ce moment ? (0 = pas de douleur, 10 = insupportable)")
    scale_row("2","Dans quelle mesure votre douleur est-elle permanente ? (0 = jamais, 10 = toujours)")
    scale_row("3","La douleur perturbe-t-elle votre sommeil ? (0 = pas du tout, 10 = complètement)")
    scale_row("4","Avez-vous peur que l'activité aggrave votre douleur ? (0 = pas du tout, 10 = extrêmement)")
    scale_row("5","Pensez-vous que votre douleur va disparaître ? (0 = pas du tout, 10 = complètement)")
    scale_row("6","Quelle confiance avez-vous dans le fait de retourner au travail dans 3 mois ? (0 = aucune, 10 = totale)")
    scale_row("7","Dans quelle mesure pensez-vous pouvoir travailler malgré la douleur ? (0 = pas du tout, 10 = totalement)")

    story.append(Paragraph("Pour les activités suivantes, dans quelle mesure la douleur affecte-t-elle votre capacité ? (0 = pas d'effet, 10 = incapable)", styles["intro"]))
    activites = [
        "8. Activités légères à la maison (cuisiner, ranger)",
        "9. Activités lourdes (nettoyer, jardiner)",
        "10. Activités sociales (conversations, visites)",
        "11. Déplacements (transports, conduire)",
        "12. Loisirs légers",
        "13. Travail ou études",
    ]
    act_header = [["Activité"] + list(range(11))]
    act_rows   = [[act] + [CHECKBOX]*11 for act in activites]
    col_w = [7*cm] + [0.75*cm]*11
    act_tbl = Table(act_header + act_rows, colWidths=col_w)
    act_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),BLEU),
        ("TEXTCOLOR",(0,0),(-1,0),BLANC),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),7),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.3,GRIS_BORD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[BLANC,GRIS_CLAIR]),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(act_tbl)
    story.append(Spacer(1, 0.4*cm))
    story += score_footer("Örebro", 100,
        "≤ 50 : risque faible  ·  51–74 : risque moyen  ·  ≥ 75 : risque élevé de chronicisation")

QUESTIONNAIRES_LOMB = {
    "odi":    ("Oswestry Disability Index",   build_odi),
    "tampa":  ("Tampa Scale (kinésiophobie)",  build_tampa),
    "orebro": ("Örebro",                      build_orebro),
}

def generate_questionnaires_lombalgie_pdf(selected, patient_info=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2*cm, bottomMargin=1.8*cm)
    styles = make_styles()
    story  = []
    hf = make_header_footer("36.9 Bilans — Questionnaires", f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else "")

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Questionnaires — Bilan Lombalgie",
        ParagraphStyle("gt", fontSize=22, fontName="Helvetica-Bold",
                       textColor=BLEU, alignment=TA_CENTER, spaceAfter=6)))
    if patient_info:
        story.append(Paragraph(
            f"Patient : {patient_info.get('nom','')} {patient_info.get('prenom','')}",
            ParagraphStyle("gs", fontSize=12, fontName="Helvetica",
                           textColor=colors.HexColor("#555"), alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLEU))
    story.append(Spacer(1, 0.4*cm))
    for key in selected:
        if key in QUESTIONNAIRES_LOMB:
            story.append(Paragraph(f"  ▸  {QUESTIONNAIRES_LOMB[key][0]}",
                ParagraphStyle("li", fontSize=10, fontName="Helvetica",
                               textColor=NOIR, spaceAfter=3)))
    story.append(PageBreak())

    for i, key in enumerate(selected):
        if key not in QUESTIONNAIRES_LOMB: continue
        QUESTIONNAIRES_LOMB[key][1](story, styles)
        if i < len(selected)-1: story.append(PageBreak())

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return buffer.getvalue()
"""
Questionnaires complets pour saisie in-app — Lombalgie
ODI, Tampa Scale (TSK-17), Örebro
Avec calcul automatique des scores.
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  OSWESTRY DISABILITY INDEX (ODI) — 10 sections, score 0–5 par section
# ═══════════════════════════════════════════════════════════════════════════════

ODI_SECTIONS = [
    ("odi_s1", "1. Intensité de la douleur", [
        "Pas de douleur actuellement",
        "La douleur est très légère actuellement",
        "La douleur est modérée actuellement",
        "La douleur est assez sévère actuellement",
        "La douleur est très sévère actuellement",
        "La douleur est la pire imaginable actuellement",
    ]),
    ("odi_s2", "2. Soins personnels (se laver, s'habiller…)", [
        "Je me prends en charge normalement sans douleur supplémentaire",
        "Je me prends en charge normalement mais c'est très douloureux",
        "Se prendre en charge est douloureux — je suis lent(e) et prudent(e)",
        "J'ai besoin d'aide mais j'arrive à gérer la plupart de mes soins",
        "J'ai besoin d'aide chaque jour pour la plupart de mes soins",
        "Je ne m'habille pas, me lave avec difficulté et reste au lit",
    ]),
    ("odi_s3", "3. Soulever des charges", [
        "Je peux soulever des charges lourdes sans douleur",
        "Je peux soulever des charges lourdes mais avec douleur supplémentaire",
        "La douleur m'empêche de soulever des charges lourdes du sol",
        "La douleur m'empêche de soulever des charges lourdes (je peux soulever du léger si bien placé)",
        "Je peux soulever des charges très légères uniquement",
        "Je ne peux rien soulever ni porter",
    ]),
    ("odi_s4", "4. Marche", [
        "La douleur ne m'empêche pas de marcher quelle que soit la distance",
        "La douleur m'empêche de marcher plus d'un kilomètre",
        "La douleur m'empêche de marcher plus de 500 mètres",
        "La douleur m'empêche de marcher plus de 100 mètres",
        "Je ne marche qu'avec une canne ou des béquilles",
        "Je suis au lit la plupart du temps et dois me traîner pour aller aux toilettes",
    ]),
    ("odi_s5", "5. Position assise", [
        "Je peux rester assis(e) aussi longtemps que je veux sans douleur",
        "Je peux rester assis(e) aussi longtemps que je veux avec légère douleur",
        "La douleur m'empêche de rester assis(e) plus d'une heure",
        "La douleur m'empêche de rester assis(e) plus de 30 minutes",
        "La douleur m'empêche de rester assis(e) plus de 10 minutes",
        "La douleur m'empêche totalement de m'asseoir",
    ]),
    ("odi_s6", "6. Position debout", [
        "Je peux rester debout aussi longtemps que je veux sans douleur",
        "Je peux rester debout aussi longtemps que je veux mais avec douleur",
        "La douleur m'empêche de rester debout plus d'une heure",
        "La douleur m'empêche de rester debout plus de 30 minutes",
        "La douleur m'empêche de rester debout plus de 10 minutes",
        "La douleur m'empêche totalement de rester debout",
    ]),
    ("odi_s7", "7. Sommeil", [
        "Mon sommeil n'est jamais perturbé par la douleur",
        "Mon sommeil est parfois perturbé par la douleur",
        "Je dors moins de 6 heures à cause de la douleur",
        "Je dors moins de 4 heures à cause de la douleur",
        "Je dors moins de 2 heures à cause de la douleur",
        "La douleur m'empêche totalement de dormir",
    ]),
    ("odi_s8", "8. Vie sexuelle (si applicable)", [
        "Ma vie sexuelle est normale sans douleur supplémentaire",
        "Ma vie sexuelle est normale mais provoque une douleur supplémentaire",
        "Ma vie sexuelle est presque normale mais est très douloureuse",
        "Ma vie sexuelle est sévèrement limitée par la douleur",
        "Ma vie sexuelle est presque absente en raison de la douleur",
        "La douleur empêche toute vie sexuelle",
    ]),
    ("odi_s9", "9. Vie sociale", [
        "Ma vie sociale est normale sans douleur supplémentaire",
        "Ma vie sociale est normale mais augmente le degré de douleur",
        "La douleur n'affecte pas les activités légères mais limite les activités énergiques",
        "La douleur a limité ma vie sociale — je sors moins souvent",
        "La douleur a limité ma vie sociale à ma maison",
        "Je n'ai pas de vie sociale à cause de la douleur",
    ]),
    ("odi_s10", "10. Voyages / transports", [
        "Je peux voyager n'importe où sans douleur supplémentaire",
        "Je peux voyager n'importe où mais avec douleur",
        "La douleur est sévère mais je gère les trajets de plus de 2 heures",
        "La douleur me restreint à des trajets de moins d'une heure",
        "La douleur me restreint à des trajets courts de moins de 30 minutes",
        "La douleur m'empêche de voyager sauf pour des soins médicaux",
    ]),
]

ODI_KEYS = [s[0] for s in ODI_SECTIONS]


def compute_odi(answers: dict) -> dict:
    """answers = {"odi_s1": 2, "odi_s2": 0, ...} (0–5 par section)"""
    scores = []
    for key, _, _ in ODI_SECTIONS:
        v = answers.get(key)
        if v is not None:
            scores.append(int(v))
    if not scores:
        return {"score": None, "interpretation": "", "color": "#888"}
    total = sum(scores)
    max_possible = len(scores) * 5
    pct = round(total / max_possible * 100)
    if pct <= 20:
        interp, color = "Incapacité minimale (0–20%)", "#388e3c"
    elif pct <= 40:
        interp, color = "Incapacité modérée (21–40%)", "#8bc34a"
    elif pct <= 60:
        interp, color = "Incapacité sévère (41–60%)", "#f57c00"
    elif pct <= 80:
        interp, color = "Incapacité très sévère (61–80%)", "#e64a19"
    else:
        interp, color = "Grabataire / exagération (>80%)", "#d32f2f"
    return {"score": pct, "interpretation": interp, "color": color, "raw": total}


# ═══════════════════════════════════════════════════════════════════════════════
#  TAMPA SCALE FOR KINESIOPHOBIA (TSK-17) — 17 items, score 1–4
# ═══════════════════════════════════════════════════════════════════════════════

TAMPA_SCALE = ["1 — Pas du tout d'accord", "2 — Plutôt pas d'accord",
               "3 — Plutôt d'accord", "4 — Tout à fait d'accord"]
TAMPA_SCALE_VALUES = [1, 2, 3, 4]

# Items inversés (R) : scores inversés pour le calcul (1→4, 2→3, 3→2, 4→1)
TAMPA_REVERSED = {8, 12, 16}  # indices 1-based

TAMPA_ITEMS = [
    ("tampa_1",  False, "J'ai peur de me blesser si je fais de l'exercice."),
    ("tampa_2",  False, "Si j'essayais de surmonter ma douleur, celle-ci augmenterait."),
    ("tampa_3",  False, "Mon corps me dit que quelque chose ne va pas vraiment."),
    ("tampa_4",  False, "Ma blessure a mis mon corps en danger toute ma vie."),
    ("tampa_5",  False, "Les gens ne prennent pas ma condition médicale assez au sérieux."),
    ("tampa_6",  False, "Ma blessure a mis mon corps en danger de façon permanente."),
    ("tampa_7",  False, "La douleur signifie toujours que j'ai subi une blessure corporelle."),
    ("tampa_8",  True,  "Simplement parce que quelque chose aggrave ma douleur ne signifie pas qu'elle est dangereuse."),
    ("tampa_9",  False, "J'ai peur de me blesser accidentellement."),
    ("tampa_10", False, "Le plus sûr est de faire attention à ne pas faire de mouvements inutiles."),
    ("tampa_11", False, "Je n'aurais pas autant de douleur si quelque chose de potentiellement grave ne se passait pas."),
    ("tampa_12", True,  "Bien que ma condition soit douloureuse, je me sentirais mieux si j'étais plus actif(ve)."),
    ("tampa_13", False, "La douleur me signale que je dois arrêter ce que je fais pour ne pas me blesser."),
    ("tampa_14", False, "Ce n'est pas vraiment sûr pour quelqu'un avec ma condition d'être physiquement actif(ve)."),
    ("tampa_15", False, "Je risque trop facilement de me blesser."),
    ("tampa_16", True,  "Même si quelque chose me fait très mal, je ne pense pas que ce soit dangereux."),
    ("tampa_17", False, "Personne ne devrait faire de l'exercice physique quand il souffre de douleur."),
]

TAMPA_KEYS = [t[0] for t in TAMPA_ITEMS]


def compute_tampa(answers: dict) -> dict:
    """answers = {"tampa_1": 3, "tampa_2": 1, ...} (1–4)"""
    total = 0
    count = 0
    for i, (key, reversed_item, _) in enumerate(TAMPA_ITEMS):
        v = answers.get(key)
        if v is not None:
            score = int(v)
            if reversed_item:
                score = 5 - score  # inversion : 1→4, 2→3, 3→2, 4→1
            total += score
            count += 1
    if count == 0:
        return {"score": None, "interpretation": "", "color": "#888"}
    if count < 17:
        # Extrapolation si items manquants
        total = round(total / count * 17)
    if total <= 37:
        interp, color = "Kinésiophobie faible (≤ 37)", "#388e3c"
    elif total <= 44:
        interp, color = "Kinésiophobie modérée (38–44)", "#f57c00"
    else:
        interp, color = "Kinésiophobie élevée (> 44)", "#d32f2f"
    return {"score": total, "interpretation": interp, "color": color}


# ═══════════════════════════════════════════════════════════════════════════════
#  ÖREBRO — items sur échelle 0–10
# ═══════════════════════════════════════════════════════════════════════════════

OREBRO_ITEMS = [
    ("orebro_1",
     "Quelle est l'intensité de votre douleur en ce moment ?",
     "0 = pas de douleur  ·  10 = douleur insupportable"),
    ("orebro_2",
     "Dans quelle mesure votre douleur est-elle présente en permanence pendant vos heures d'éveil ?",
     "0 = jamais  ·  10 = toujours"),
    ("orebro_3",
     "Dans quelle mesure la douleur perturbe-t-elle votre sommeil ?",
     "0 = pas du tout  ·  10 = complètement"),
    ("orebro_4",
     "Dans quelle mesure avez-vous peur que l'activité physique aggrave votre douleur ?",
     "0 = pas du tout  ·  10 = extrêmement"),
    ("orebro_5",
     "Dans quelle mesure pensez-vous que votre douleur disparaîtra ?",
     "0 = pas du tout  ·  10 = complètement"),
    ("orebro_6",
     "Quelle confiance avez-vous dans le fait de retourner au travail dans les 3 prochains mois ?",
     "0 = aucune confiance  ·  10 = très confiant(e)"),
    ("orebro_7",
     "Dans quelle mesure pensez-vous que vous pouvez effectuer un travail malgré la douleur ?",
     "0 = pas du tout  ·  10 = totalement"),
    ("orebro_8",
     "Activités légères à la maison (cuisiner, ranger) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_9",
     "Activités lourdes à la maison (nettoyer, jardiner) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_10",
     "Activités sociales (conversations, visites) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_11",
     "Déplacements (transports en commun, conduire) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_12",
     "Loisirs légers — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_13",
     "Travail ou études — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
]

# Items à inverser pour le scoring (5, 6, 7 : plus = mieux → on inverse)
OREBRO_INBLEUED = {"orebro_5", "orebro_6", "orebro_7"}

OREBRO_KEYS = [o[0] for o in OREBRO_ITEMS]


def compute_orebro(answers: dict) -> dict:
    """answers = {"orebro_1": 6, "orebro_2": 4, ...} (0–10)"""
    total = 0
    count = 0
    for key, _, _ in OREBRO_ITEMS:
        v = answers.get(key)
        if v is not None:
            score = int(v)
            if key in OREBRO_INBLEUED:
                score = 10 - score
            total += score
            count += 1
    if count == 0:
        return {"score": None, "interpretation": "", "color": "#888"}
    # Normalisation sur 100
    pct = round(total / (count * 10) * 100)
    if pct <= 50:
        interp, color = "Risque faible de chronicisation (≤ 50)", "#388e3c"
    elif pct <= 74:
        interp, color = "Risque moyen de chronicisation (51–74)", "#f57c00"
    else:
        interp, color = "Risque élevé de chronicisation (≥ 75)", "#d32f2f"
    return {"score": pct, "interpretation": interp, "color": color, "raw": total}
