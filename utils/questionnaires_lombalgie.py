"""
Génération des questionnaires papier imprimables — Lombalgie
(À compléter au fur et à mesure du développement)
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

BLEU_LOMB  = colors.HexColor("#2e5a1c")
BLANC      = colors.white


def generate_questionnaires_lombalgie_pdf(
    selected: list,
    patient_info: dict = None,
) -> bytes:
    """
    Génère le PDF des questionnaires lombalgie sélectionnés.
    Pour l'instant retourne un PDF placeholder.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    base = getSampleStyleSheet()
    story = []

    nom_prenom = (
        f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"
        if patient_info else "Questionnaires vierges"
    )

    story.append(Paragraph(
        "Questionnaires — Bilan Lombalgie",
        ParagraphStyle("t", fontSize=20, fontName="Helvetica-Bold",
                       textColor=BLEU_LOMB, alignment=TA_CENTER, spaceAfter=10),
    ))
    if patient_info:
        story.append(Paragraph(
            f"Patient : {nom_prenom}",
            ParagraphStyle("s", fontSize=12, fontName="Helvetica",
                           textColor=colors.HexColor("#555"), alignment=TA_CENTER),
        ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "🚧 Les questionnaires spécifiques à la lombalgie sont en cours de développement.",
        ParagraphStyle("n", fontSize=11, fontName="Helvetica",
                       textColor=colors.HexColor("#888"), alignment=TA_CENTER),
    ))

    doc.build(story)
    return buffer.getvalue()
