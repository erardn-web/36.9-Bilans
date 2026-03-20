"""
Génération des questionnaires papier imprimables (version patient).
HAD, SF-12, Test HV, BOLT — mise en page soignée pour impression A4.
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

# ─── Couleurs ─────────────────────────────────────────────────────────────────
from pdf_theme import (
    TERRA, BLEU, BLEU_LIGHT, GRIS, GRIS_BORD, BLANC, NOIR, GRIS_TEXTE,
    VERT, ORANGE, ROUGE, USEFUL_W, MARGIN, make_header_footer, get_logo,
)
BLEU_CLAIR = BLEU_LIGHT
GRIS_CLAIR = GRIS
W = USEFUL_W


# ─── Styles ───────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    return {
        "doc_title": ParagraphStyle(
            "doc_title", fontSize=18, fontName="Helvetica-Bold",
            textColor=BLEU, alignment=TA_CENTER, spaceAfter=4,
        ),
        "doc_sub": ParagraphStyle(
            "doc_sub", fontSize=10, fontName="Helvetica",
            textColor=colors.HexColor("#555"), alignment=TA_CENTER, spaceAfter=2,
        ),
        "q_title": ParagraphStyle(
            "q_title", fontSize=14, fontName="Helvetica-Bold",
            textColor=BLANC, spaceAfter=0, spaceBefore=0,
            leftIndent=8, borderPadding=(5, 8, 5, 8),
        ),
        "intro": ParagraphStyle(
            "intro", fontSize=9, fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#444"), spaceAfter=6,
            leftIndent=4, rightIndent=4,
        ),
        "question": ParagraphStyle(
            "question", fontSize=10, fontName="Helvetica-Bold",
            textColor=NOIR, spaceBefore=8, spaceAfter=3, leftIndent=4,
        ),
        "option": ParagraphStyle(
            "option", fontSize=9, fontName="Helvetica",
            textColor=NOIR, spaceAfter=2, leftIndent=20,
        ),
        "small": ParagraphStyle(
            "small", fontSize=8, fontName="Helvetica",
            textColor=colors.HexColor("#666"),
        ),
        "note_box": ParagraphStyle(
            "note_box", fontSize=9, fontName="Helvetica",
            textColor=colors.HexColor("#444"),
            leftIndent=6, rightIndent=6,
        ),
        "protocole": ParagraphStyle(
            "protocole", fontSize=9, fontName="Helvetica",
            textColor=NOIR, spaceAfter=4, leftIndent=8,
        ),
    }


# ─── Header / footer ─────────────────────────────────────────────────────────


# ─── Titre de section ─────────────────────────────────────────────────────────
def section_header(title, subtitle=""):
    tbl = Table([[Paragraph(title, ParagraphStyle(
        "th", fontSize=13, fontName="Helvetica-Bold",
        textColor=BLANC, spaceAfter=0,
    ))]], colWidths=[W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLEU),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    items = [tbl]
    if subtitle:
        items.append(Paragraph(subtitle, ParagraphStyle(
            "ts", fontSize=8, fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#555"), spaceAfter=4,
            leftIndent=4,
        )))
    return items


# ─── Case à cocher ────────────────────────────────────────────────────────────
CHECKBOX = "☐"   # caractère unicode case vide


def checkbox_row(label, extra=""):
    """Retourne une ligne avec case à cocher."""
    return [f"{CHECKBOX}  {label}", extra]


# ─── Tableau de réponses radio ────────────────────────────────────────────────
def radio_table(question_num, question_text, options, styles):
    """
    Crée un bloc question + cases à cocher horizontales pour impression.
    options = [(score, label), ...]
    """
    items = []

    # Numéro + texte de la question
    q_text = f"{question_num}. {question_text}"
    items.append(Paragraph(q_text, styles["question"]))

    # Options en tableau horizontal
    n = len(options)
    col_w = W / n
    header = [[Paragraph(f"{CHECKBOX}  {lbl}", ParagraphStyle(
        "opt", fontSize=9, fontName="Helvetica",
        textColor=NOIR, alignment=TA_CENTER,
    )) for _, lbl in options]]

    tbl = Table(header, colWidths=[col_w] * n)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GRIS_CLAIR),
        ("GRID",          (0, 0), (-1, -1), 0.5, GRIS_BORD),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    items.append(tbl)
    return KeepTogether(items)


def radio_table_vertical(question_num, question_text, options, styles):
    """Options en liste verticale (pour options longues)."""
    items = []
    q_text = f"{question_num}. {question_text}"
    items.append(Paragraph(q_text, styles["question"]))
    rows = [[Paragraph(f"{CHECKBOX}  {lbl}", styles["option"])] for _, lbl in options]
    tbl = Table(rows, colWidths=[W])
    tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
    ]))
    items.append(tbl)
    return KeepTogether(items)


def score_box(label, width=3*cm):
    """Petite boîte 'Score : ___/21'."""
    tbl = Table([[label, ""]], colWidths=[W - width, width])
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 0), (0, 0), BLEU),
        ("BOX",           (1, 0), (1, 0), 1, BLEU),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tbl


def ligne_saisie(label, width_line=8*cm):
    """Ligne de saisie libre."""
    tbl = Table([[label, ""]], colWidths=[W - width_line, width_line])
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, 0), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("LINEBELOW",     (1, 0), (1, 0), 0.8, NOIR),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


# ═══════════════════════════════════════════════════════════════════════════════
#  QUESTIONNAIRE HAD
# ═══════════════════════════════════════════════════════════════════════════════

def build_had(story, styles):
    story += section_header(
        "Échelle HAD — Hospital Anxiety and Depression Scale",
        "Zigmond & Snaith, 1983 — Version française validée"
    )
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Ce questionnaire est un outil de dépistage. Il ne s'agit pas d'un diagnostic. "
        "Lisez chaque item et cochez la réponse qui correspond le mieux à ce que vous avez "
        "ressenti au cours de la semaine écoulée. Ne réfléchissez pas trop longtemps — "
        "votre première réaction est la bonne.",
        styles["intro"],
    ))
    story.append(Spacer(1, 0.2*cm))

    questions_had = [
        ("A", "Je me sens tendu(e) ou énervé(e) :",
         [(3, "La plupart du temps"), (2, "Souvent"), (1, "De temps en temps"), (0, "Jamais")]),
        ("D", "Je prends toujours autant de plaisir aux mêmes choses qu'autrefois :",
         [(0, "Oui, tout autant"), (1, "Pas autant"), (2, "Un peu seulement"), (3, "Presque plus")]),
        ("A", "J'éprouve des sensations de peur comme si quelque chose d'horrible allait m'arriver :",
         [(3, "Oui, très nettement"), (2, "Oui, mais pas trop grave"), (1, "Un peu"), (0, "Pas du tout")]),
        ("D", "Je ris facilement et vois le bon côté des choses :",
         [(0, "Autant qu'avant"), (1, "Plus autant"), (2, "Vraiment moins"), (3, "Plus du tout")]),
        ("A", "Les idées se bousculent dans ma tête :",
         [(3, "La plupart du temps"), (2, "Assez souvent"), (1, "De temps en temps"), (0, "Très occasionnellement")]),
        ("D", "Je me sens de bonne humeur :",
         [(3, "Jamais"), (2, "Rarement"), (1, "Assez souvent"), (0, "La plupart du temps")]),
        ("A", "Je peux rester tranquillement assis(e) à ne rien faire et me sentir décontracté(e) :",
         [(0, "Oui, toujours"), (1, "Oui, en général"), (2, "Rarement"), (3, "Jamais")]),
        ("D", "J'ai l'impression de fonctionner au ralenti :",
         [(3, "Presque toujours"), (2, "Très souvent"), (1, "Parfois"), (0, "Jamais")]),
        ("A", "J'éprouve des sensations de peur et j'ai l'estomac noué :",
         [(0, "Jamais"), (1, "Parfois"), (2, "Assez souvent"), (3, "Très souvent")]),
        ("D", "Je ne m'intéresse plus à mon apparence :",
         [(3, "Plus du tout"), (2, "Pas autant que je devrais"), (1, "Il se peut"), (0, "J'y prête autant attention")]),
        ("A", "Je me sens agité(e) comme si j'avais continuellement besoin de bouger :",
         [(3, "Vraiment très souvent"), (2, "Assez souvent"), (1, "Pas tellement"), (0, "Pas du tout")]),
        ("D", "Je me réjouis à l'avance à l'idée de faire certaines choses :",
         [(0, "Autant qu'avant"), (1, "Un peu moins"), (2, "Bien moins"), (3, "Presque jamais")]),
        ("A", "J'éprouve des sensations soudaines de panique :",
         [(3, "Vraiment très souvent"), (2, "Assez souvent"), (1, "Pas tellement"), (0, "Jamais")]),
        ("D", "Je peux prendre plaisir à un bon livre ou à une émission de TV/radio :",
         [(0, "Souvent"), (1, "Parfois"), (2, "Rarement"), (3, "Très rarement")]),
    ]

    for i, (sous_echelle, question, options) in enumerate(questions_had):
        label = f"{'A' if sous_echelle == 'A' else 'D'}{(i//2)+1}"
        story.append(radio_table_vertical(label, question, options, styles))
        story.append(Spacer(1, 0.15*cm))

    # Zones de score
    story.append(Spacer(1, 0.4*cm))
    score_data = [
        ["Score Anxiété (items A) : _____ / 21",
         "Score Dépression (items D) : _____ / 21"],
        ["☐ Normal (0–7)   ☐ Douteux (8–10)   ☐ Pathologique (11–21)",
         "☐ Normal (0–7)   ☐ Douteux (8–10)   ☐ Pathologique (11–21)"],
    ]
    score_tbl = Table(score_data, colWidths=[W/2, W/2])
    score_tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLEU),
        ("BACKGROUND",    (0, 0), (-1, -1), BLEU_CLAIR),
        ("GRID",          (0, 0), (-1, -1), 0.5, GRIS_BORD),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(score_tbl)


# ═══════════════════════════════════════════════════════════════════════════════
#  QUESTIONNAIRE SF-12
# ═══════════════════════════════════════════════════════════════════════════════

def build_sf12(story, styles):
    story += section_header(
        "SF-12 — Short Form Health Survey",
        "Ware et al., 1996 — Version française validée"
    )
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Ce questionnaire vous pose des questions sur votre santé et votre bien-être. "
        "Pour chaque question, cochez la réponse qui correspond le mieux à votre situation "
        "au cours des 4 dernières semaines.",
        styles["intro"],
    ))
    story.append(Spacer(1, 0.2*cm))

    sf12_questions = [
        ("1", "En général, diriez-vous que votre santé est :", [
            (1, "Excellente"), (2, "Très bonne"), (3, "Bonne"),
            (4, "Passable"), (5, "Mauvaise"),
        ], "h"),
        ("2a", "Activités modérées (passer l'aspirateur, faire du vélo…)\n"
               "— Votre état de santé vous limite-t-il dans cette activité ?", [
            (1, "Oui, très limité(e)"), (2, "Oui, un peu limité(e)"), (3, "Non, pas du tout"),
        ], "h"),
        ("2b", "Monter plusieurs étages par un escalier\n"
               "— Votre état de santé vous limite-t-il dans cette activité ?", [
            (1, "Oui, très limité(e)"), (2, "Oui, un peu limité(e)"), (3, "Non, pas du tout"),
        ], "h"),
    ]

    # Intro Q3
    story.append(Paragraph(
        "Au cours des 4 dernières semaines, avez-vous eu des problèmes dans votre travail "
        "ou activités habituelles en raison de votre état de santé PHYSIQUE ?",
        styles["intro"],
    ))
    sf12_questions += [
        ("3a", "Avez-vous accompli moins de choses que vous le souhaitiez ?",
         [(1, "Oui"), (2, "Non")], "h"),
        ("3b", "Avez-vous été limité(e) dans certaines activités ?",
         [(1, "Oui"), (2, "Non")], "h"),
    ]

    story.append(Paragraph(
        "Au cours des 4 dernières semaines, avez-vous eu des problèmes dans votre travail "
        "ou activités habituelles en raison de problèmes ÉMOTIONNELS ?",
        styles["intro"],
    ))
    sf12_questions += [
        ("4a", "Avez-vous accompli moins de choses que vous le souhaitiez ?",
         [(1, "Oui"), (2, "Non")], "h"),
        ("4b", "Avez-vous fait ce travail avec moins de soin que d'habitude ?",
         [(1, "Oui"), (2, "Non")], "h"),
        ("5", "Dans quelle mesure la douleur a-t-elle gêné votre travail habituel ?", [
            (1, "Pas du tout"), (2, "Un petit peu"), (3, "Modérément"),
            (4, "Beaucoup"), (5, "Énormément"),
        ], "h"),
    ]

    story.append(Paragraph(
        "Ces questions portent sur ce que vous avez ressenti au cours des 4 dernières semaines.",
        styles["intro"],
    ))
    sf12_questions += [
        ("6a", "Vous êtes-vous senti(e) calme et détendu(e) ?", [
            (1, "Tout le temps"), (2, "La plupart du temps"), (3, "Souvent"),
            (4, "Quelquefois"), (5, "Rarement"), (6, "Jamais"),
        ], "h"),
        ("6b", "Avez-vous eu beaucoup d'énergie ?", [
            (1, "Tout le temps"), (2, "La plupart du temps"), (3, "Souvent"),
            (4, "Quelquefois"), (5, "Rarement"), (6, "Jamais"),
        ], "h"),
        ("6c", "Vous êtes-vous senti(e) abattu(e) et triste ?", [
            (1, "Tout le temps"), (2, "La plupart du temps"), (3, "Souvent"),
            (4, "Quelquefois"), (5, "Rarement"), (6, "Jamais"),
        ], "h"),
        ("7", "Dans quelle mesure votre état de santé ou vos problèmes émotionnels "
              "ont-ils gêné vos activités sociales ?", [
            (1, "Tout le temps"), (2, "La plupart du temps"), (3, "Quelquefois"),
            (4, "Rarement"), (5, "Jamais"),
        ], "h"),
    ]

    for num, question, options, layout in sf12_questions:
        if layout == "h" and len(options) <= 4:
            story.append(radio_table(num, question, options, styles))
        else:
            story.append(radio_table_vertical(num, question, options, styles))
        story.append(Spacer(1, 0.15*cm))

    # Zones de score
    story.append(Spacer(1, 0.4*cm))
    pcs_mcs = Table([
        ["PCS-12 (score physique) : _______ / 100",
         "MCS-12 (score mental) : _______ / 100"],
        ["Interprétation : ≥55 au-dessus moy. · 45–55 dans la moy. · 35–45 en-dessous · <35 très en-dessous",
         "Interprétation : ≥55 au-dessus moy. · 45–55 dans la moy. · 35–45 en-dessous · <35 très en-dessous"],
    ], colWidths=[W/2, W/2])
    pcs_mcs.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",      (0, 1), (-1, 1),  "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLEU),
        ("BACKGROUND",    (0, 0), (-1, -1), BLEU_CLAIR),
        ("GRID",          (0, 0), (-1, -1), 0.5, GRIS_BORD),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(pcs_mcs)


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST D'HYPERVENTILATION VOLONTAIRE
# ═══════════════════════════════════════════════════════════════════════════════

def build_hvt(story, styles):
    story += section_header(
        "Test d'Hyperventilation Volontaire (THV)",
        "Fiche praticien — À remplir pendant et après le test"
    )
    story.append(Spacer(1, 0.3*cm))

    # Protocole encadré
    protocole_data = [[Paragraph(
        "<b>Protocole :</b><br/>"
        "1. Expliquer au patient ce qui va se passer et obtenir son consentement.<br/>"
        "2. Demander au patient de respirer plus profondément et plus vite pendant <b>3 minutes</b>.<br/>"
        "3. Lui demander de signaler les symptômes qui apparaissent.<br/>"
        "4. Après arrêt, chronométrer le retour à la normale.<br/>"
        "5. Le test est <b>positif</b> si les symptômes reproduits correspondent aux plaintes habituelles.",
        ParagraphStyle("p", fontSize=9, fontName="Helvetica", textColor=NOIR, leading=14),
    )]]
    prot_tbl = Table(protocole_data, colWidths=[W])
    prot_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLEU_CLAIR),
        ("BOX",           (0, 0), (-1, -1), 1, BLEU),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(prot_tbl)
    story.append(Spacer(1, 0.3*cm))

    # Contre-indications
    ci = Table([[Paragraph(
        "⚠️ <b>Contre-indications :</b> épilepsie · grossesse · pathologie cardiaque sévère · AVC récent",
        ParagraphStyle("ci", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#b71c1c")),
    )]], colWidths=[W])
    ci.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#fff8e1")),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#f9a825")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(ci)
    story.append(Spacer(1, 0.4*cm))

    # Informations test
    story.append(Paragraph("Informations du test", ParagraphStyle(
        "sh", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=6,
    )))

    info_rows = [
        ["Date : ___________________________",
         "Durée du test : _____ min"],
        ["Praticien : ___________________________",
         "Durée retour à la normale : _____ min"],
    ]
    info_tbl = Table(info_rows, colWidths=[W/2, W/2])
    info_tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Résultat global
    story.append(Paragraph("Résultat global", ParagraphStyle(
        "sh2", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=6,
    )))
    result_rows = [
        [f"{CHECKBOX}  Test positif — reproduit les symptômes habituels"],
        [f"{CHECKBOX}  Test partiellement positif — reproduit certains symptômes"],
        [f"{CHECKBOX}  Test négatif — ne reproduit pas les symptômes habituels"],
        [f"{CHECKBOX}  Test non réalisé (contre-indication ou refus)"],
    ]
    result_tbl = Table(result_rows, colWidths=[W])
    result_tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
    ]))
    story.append(result_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Symptômes reproduits
    story.append(Paragraph("Symptômes reproduits (cochez tout ce qui s'applique)", ParagraphStyle(
        "sh3", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=6,
    )))

    symptomes = [
        "Vertiges / étourdissements", "Céphalées", "Vision trouble / flou visuel",
        "Fourmillements des mains / pieds", "Fourmillements péribuccaux", "Engourdissements",
        "Spasmes musculaires / tétanie", "Essoufflement", "Douleur / oppression thoracique",
        "Palpitations", "Sensation de manque d'air", "Anxiété", "Sentiment de panique",
        "Dépersonnalisation", "Nausées", "Fatigue / épuisement soudain",
        "Bouche sèche", "Bâillements répétés",
    ]
    # 2 colonnes
    mid = (len(symptomes) + 1) // 2
    col1 = [[f"{CHECKBOX}  {s}"] for s in symptomes[:mid]]
    col2 = [[f"{CHECKBOX}  {s}"] for s in symptomes[mid:]]
    # Padding pour égaliser
    while len(col2) < len(col1):
        col2.append([""])

    sym_rows = [[Paragraph(col1[i][0], ParagraphStyle("s", fontSize=9, fontName="Helvetica")),
                 Paragraph(col2[i][0], ParagraphStyle("s", fontSize=9, fontName="Helvetica"))]
                for i in range(len(col1))]
    sym_tbl = Table(sym_rows, colWidths=[W/2, W/2])
    sym_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
    ]))
    story.append(sym_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Notes
    story.append(Paragraph("Observations cliniques", ParagraphStyle(
        "sh4", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=6,
    )))
    notes_rows = [[""] for _ in range(4)]
    notes_tbl = Table(notes_rows, colWidths=[W], rowHeights=[0.7*cm]*4)
    notes_tbl.setStyle(TableStyle([
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
    ]))
    story.append(notes_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Grille de mesures ──────────────────────────────────────────────────────
    story.append(Paragraph("Grille de mesures", ParagraphStyle(
        "sh5", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=6,
    )))

    PARAMS     = ["PetCO₂\n(mmHg)", "FR\n(cyc/min)", "SpO₂\n(%)", "FC\n(bpm)"]
    PHASES = [
        ("🟦 Repos",        ["T0", "1 min", "2 min", "3 min"]),
        ("🔴 HV",           ["1 min", "2 min", "3 min"]),
        ("🟩 Récupération", ["1 min", "2 min", "3 min", "4 min", "5 min"]),
    ]

    # Largeurs : colonne temps + 4 paramètres
    col_w_time   = 2.2*cm
    col_w_param  = (W - col_w_time) / 4

    # En-tête globale
    header_row = [Paragraph("<b>Temps</b>", ParagraphStyle(
        "gh", fontSize=8, fontName="Helvetica-Bold",
        textColor=BLANC, alignment=1,
    ))]
    for p in PARAMS:
        header_row.append(Paragraph(
            f"<b>{p}</b>",
            ParagraphStyle("gp", fontSize=8, fontName="Helvetica-Bold",
                           textColor=BLANC, alignment=1, leading=10),
        ))

    all_rows   = [header_row]
    row_styles = []   # (bg_color, row_index)

    for phase_label, times in PHASES:
        # Ligne de phase (fusionnée visuellement via couleur de fond)
        phase_row = [Paragraph(
            f"<b>{phase_label}</b>",
            ParagraphStyle("phase", fontSize=8, fontName="Helvetica-Bold",
                           textColor=BLEU, leading=10),
        )] + [""] * 4
        all_rows.append(phase_row)
        row_styles.append(("phase", len(all_rows) - 1))

        for t_label in times:
            data_row = [Paragraph(
                t_label,
                ParagraphStyle("tl", fontSize=8, fontName="Helvetica",
                               textColor=NOIR, alignment=1),
            )] + [""] * 4
            all_rows.append(data_row)
            row_styles.append(("data", len(all_rows) - 1))

    grid_tbl = Table(
        all_rows,
        colWidths=[col_w_time] + [col_w_param] * 4,
        repeatRows=1,
    )

    tbl_cmds = [
        # Général
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRIS_BORD),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        # En-tête
        ("BACKGROUND",    (0, 0), (-1, 0),  BLEU),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANC),
        ("ROWHEIGHT",     (0, 0), (-1, 0),  0.9*cm),
    ]

    # Lignes de phase et données alternées
    for style_type, row_idx in row_styles:
        if style_type == "phase":
            tbl_cmds += [
                ("BACKGROUND",    (0, row_idx), (-1, row_idx), BLEU_CLAIR),
                ("ALIGN",         (0, row_idx), (0, row_idx),  "LEFT"),
                ("LEFTPADDING",   (0, row_idx), (0, row_idx),  6),
                ("ROWHEIGHT",     (0, row_idx), (-1, row_idx), 0.7*cm),
            ]
        else:
            bg = BLANC if row_idx % 2 == 0 else GRIS_CLAIR
            tbl_cmds += [
                ("BACKGROUND",    (0, row_idx), (-1, row_idx), bg),
                ("ROWHEIGHT",     (0, row_idx), (-1, row_idx), 0.85*cm),
            ]

    grid_tbl.setStyle(TableStyle(tbl_cmds))
    story.append(grid_tbl)


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST BOLT
# ═══════════════════════════════════════════════════════════════════════════════

def build_bolt(story, styles):
    story += section_header(
        "BOLT — Body Oxygen Level Test",
        "Fiche praticien"
    )
    story.append(Spacer(1, 0.3*cm))

    protocole_data = [[Paragraph(
        "<b>Protocole :</b><br/>"
        "1. Laisser le patient respirer normalement pendant 1–2 minutes (ne pas modifier la respiration).<br/>"
        "2. Après une <b>expiration normale</b> (non forcée), demander au patient de bloquer sa respiration.<br/>"
        "3. Chronométrer jusqu'aux <b>premières envies nettes de respirer</b> "
        "(léger inconfort, premier mouvement involontaire du diaphragme).<br/>"
        "4. Relâcher et noter le temps en secondes.<br/>"
        "<br/>"
        "⚠️ <b>Il ne s'agit pas de tenir le plus longtemps possible</b>, mais de noter "
        "la <b>première envie</b> de respirer.",
        ParagraphStyle("p", fontSize=9, fontName="Helvetica", textColor=NOIR, leading=14),
    )]]
    prot_tbl = Table(protocole_data, colWidths=[W])
    prot_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLEU_CLAIR),
        ("BOX",           (0, 0), (-1, -1), 1, BLEU),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(prot_tbl)
    story.append(Spacer(1, 0.5*cm))

    # Résultat
    story.append(Paragraph("Résultat", ParagraphStyle(
        "sh", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=10,
    )))

    result_rows = [
        ["Score BOLT :", "_______ secondes"],
        ["Essai 1 :", "_______ secondes"],
        ["Essai 2 :", "_______ secondes"],
        ["Essai 3 :", "_______ secondes"],
        ["Moyenne :", "_______ secondes"],
    ]
    res_tbl = Table(result_rows, colWidths=[6*cm, W - 6*cm])
    res_tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",     (0, 0), (0, -1), BLEU),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ("FONTSIZE",      (0, 0), (1, 0),   11),  # ligne résultat plus grande
        ("BACKGROUND",    (0, 0), (-1, 0),  BLEU_CLAIR),
    ]))
    story.append(res_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Interprétation
    story.append(Paragraph("Interprétation", ParagraphStyle(
        "sh2", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=6,
    )))
    interp_data = [
        ["< 10 secondes", "Dysfonction respiratoire sévère — tolérance CO₂ très basse",
         f"{CHECKBOX}"],
        ["10 – 19 secondes", "Contrôle respiratoire altéré — SHV probable", f"{CHECKBOX}"],
        ["20 – 39 secondes", "Tolérance au CO₂ correcte mais améliorable", f"{CHECKBOX}"],
        ["≥ 40 secondes", "Bonne tolérance au CO₂ — contrôle satisfaisant", f"{CHECKBOX}"],
    ]
    bg_colors = [
        colors.HexColor("#ffebee"),   # rouge clair
        colors.HexColor("#fff3e0"),   # orange clair
        colors.HexColor("#fffde7"),   # jaune clair
        colors.HexColor("#e8f5e9"),   # vert clair
    ]
    interp_tbl = Table(interp_data, colWidths=[3.5*cm, W - 4.5*cm, 1*cm])
    cmds = [
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ("ALIGN",         (2, 0), (2, -1), "CENTER"),
        ("FONTSIZE",      (2, 0), (2, -1), 14),
    ]
    for i, bg in enumerate(bg_colors):
        cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    interp_tbl.setStyle(TableStyle(cmds))
    story.append(interp_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Notes
    story.append(Paragraph("Notes", ParagraphStyle(
        "shn", fontSize=11, fontName="Helvetica-Bold", textColor=BLEU, spaceAfter=6,
    )))
    notes_tbl = Table([[""] for _ in range(4)], colWidths=[W], rowHeights=[0.8*cm]*4)
    notes_tbl.setStyle(TableStyle([
        ("GRID",          (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
    ]))
    story.append(notes_tbl)


# ═══════════════════════════════════════════════════════════════════════════════
#  GÉNÉRATEUR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

QUESTIONNAIRES = {
    "had":  ("HAD — Anxiété & Dépression", build_had),
    "sf12": ("SF-12 — Qualité de vie",     build_sf12),
    "hvt":  ("Test d'Hyperventilation",    build_hvt),
    "bolt": ("Test BOLT",                  build_bolt),
}


def generate_questionnaires_pdf(
    selected: list,          # ex. ["had", "sf12", "bolt"]
    patient_info: dict = None,
) -> bytes:
    """
    Génère un PDF contenant les questionnaires sélectionnés.
    selected : liste de clés parmi "had", "sf12", "hvt", "bolt"
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.0*cm,  bottomMargin=1.8*cm,
    )
    styles = make_styles()
    story  = []
    hf = make_header_footer("36.9 Bilans — Questionnaires", f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else "")

    # Page de garde
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Questionnaires", ParagraphStyle(
        "gt", fontSize=24, fontName="Helvetica-Bold",
        textColor=BLEU, alignment=TA_CENTER, spaceAfter=6,
    )))
    story.append(Paragraph("Syndrome d'Hyperventilation", ParagraphStyle(
        "gs", fontSize=13, fontName="Helvetica",
        textColor=colors.HexColor("#555"), alignment=TA_CENTER, spaceAfter=4,
    )))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLEU))
    story.append(Spacer(1, 0.4*cm))

    if patient_info:
        pat_rows = [
            ["Patient :", f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"],
            ["Date de naissance :", str(patient_info.get("date_naissance", ""))],
            ["Date :", "_________________________"],
        ]
        pat_tbl = Table(pat_rows, colWidths=[4*cm, W - 4*cm])
        pat_tbl.setStyle(TableStyle([
            ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",  (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE",  (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), BLEU),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
            ("GRID", (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ]))
        story.append(pat_tbl)
        story.append(Spacer(1, 0.4*cm))

    # Table des matières
    story.append(Paragraph("Questionnaires inclus", ParagraphStyle(
        "tc", fontSize=11, fontName="Helvetica-Bold",
        textColor=BLEU, spaceAfter=6,
    )))
    for key in selected:
        if key in QUESTIONNAIRES:
            story.append(Paragraph(
                f"  ▸  {QUESTIONNAIRES[key][0]}",
                ParagraphStyle("li", fontSize=10, fontName="Helvetica",
                               textColor=NOIR, spaceAfter=3),
            ))

    story.append(PageBreak())

    # Questionnaires sélectionnés
    for i, key in enumerate(selected):
        if key not in QUESTIONNAIRES:
            continue
        _, build_fn = QUESTIONNAIRES[key]
        build_fn(story, styles)
        if i < len(selected) - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return buffer.getvalue()
