"""
Thème graphique partagé pour tous les PDF — 36.9 Bilans
Palette : Terracotta #C4603A + Bleu Le Corbusier #2B57A7
"""

import io
import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image

# ─── Palette ──────────────────────────────────────────────────────────────────
TERRA       = colors.HexColor("#C4603A")   # Terracotta
TERRA_LIGHT = colors.HexColor("#FAEEE9")   # Terracotta très clair
BLEU        = colors.HexColor("#2B57A7")   # Bleu Le Corbusier
BLEU_LIGHT  = colors.HexColor("#E8EEF9")   # Bleu très clair
GRIS        = colors.HexColor("#F4F4F4")   # Fond alterné
GRIS_BORD   = colors.HexColor("#DEDEDE")   # Bordures
GRIS_TEXTE  = colors.HexColor("#555555")   # Texte secondaire
NOIR        = colors.HexColor("#1A1A1A")   # Texte principal
BLANC       = colors.white

# Couleurs cliniques
VERT   = colors.HexColor("#388e3c")
ORANGE = colors.HexColor("#f57c00")
ROUGE  = colors.HexColor("#d32f2f")
JAUNE  = colors.HexColor("#fbc02d")

# ─── Chemin logo ──────────────────────────────────────────────────────────────
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_369.png")

PAGE_W, PAGE_H = A4
MARGIN     = 1.5 * cm
USEFUL_W   = PAGE_W - 2 * MARGIN
HEADER_H   = 1.6 * cm
FOOTER_H   = 0.8 * cm


# ─── Logo helper ──────────────────────────────────────────────────────────────
def get_logo(width=3.2*cm, height=1.1*cm):
    if os.path.exists(LOGO_PATH):
        return Image(LOGO_PATH, width=width, height=height, kind="proportional")
    return None


# ─── Header / Footer ──────────────────────────────────────────────────────────
def make_header_footer(report_title: str, patient_name: str = ""):
    """Retourne une fonction canvas à passer à SimpleDocTemplate.build()."""
    def _draw(canvas, doc):
        canvas.saveState()
        w, h = A4

        # ── Bandeau supérieur ──────────────────────────────────────────────
        # Fond blanc avec bande terracotta fine en haut
        canvas.setFillColor(BLEU)
        canvas.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)

        # Bande terracotta à droite du header
        canvas.setFillColor(TERRA)
        canvas.rect(w - 5*cm, h - HEADER_H, 5*cm, HEADER_H, fill=1, stroke=0)

        # Logo
        if os.path.exists(LOGO_PATH):
            try:
                canvas.drawImage(
                    LOGO_PATH,
                    MARGIN, h - HEADER_H + 0.15*cm,
                    width=2.8*cm, height=HEADER_H - 0.3*cm,
                    preserveAspectRatio=True, mask="auto",
                )
            except Exception:
                pass

        # Titre rapport (centre)
        canvas.setFillColor(BLANC)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(w / 2, h - HEADER_H * 0.65, report_title)

        # Patient (droite) dans la bande terra
        if patient_name:
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(w - MARGIN, h - HEADER_H * 0.65, patient_name)

        # ── Pied de page ──────────────────────────────────────────────────
        canvas.setStrokeColor(GRIS_BORD)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, FOOTER_H + 0.2*cm, w - MARGIN, FOOTER_H + 0.2*cm)
        canvas.setFillColor(GRIS_TEXTE)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(MARGIN, 0.35*cm, "Document confidentiel — Usage médical exclusif")
        canvas.drawCentredString(w / 2, 0.35*cm, "36.9 Bilans")
        canvas.drawRightString(w - MARGIN, 0.35*cm,
                               f"Page {doc.page}  ·  {date.today().strftime('%d/%m/%Y')}")

        canvas.restoreState()
    return _draw


# ─── Styles paragraphe ────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title",
            fontSize=26, fontName="Helvetica-Bold", textColor=BLEU,
            spaceAfter=4, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle",
            fontSize=12, fontName="Helvetica", textColor=GRIS_TEXTE,
            spaceAfter=2, alignment=TA_CENTER),
        "section": ParagraphStyle("section",
            fontSize=11, fontName="Helvetica-Bold", textColor=BLANC,
            spaceBefore=12, spaceAfter=6,
            backColor=BLEU,
            leftIndent=-6, rightIndent=-6,
            borderPadding=(5, 8, 5, 8)),
        "subsection": ParagraphStyle("subsection",
            fontSize=10, fontName="Helvetica-Bold", textColor=TERRA,
            spaceBefore=10, spaceAfter=4),
        "normal": ParagraphStyle("normal",
            fontSize=9, fontName="Helvetica", textColor=NOIR, spaceAfter=2),
        "small": ParagraphStyle("small",
            fontSize=7.5, fontName="Helvetica", textColor=GRIS_TEXTE),
        "bold": ParagraphStyle("bold",
            fontSize=9, fontName="Helvetica-Bold", textColor=BLEU),
        "note": ParagraphStyle("note",
            fontSize=8, fontName="Helvetica", textColor=GRIS_TEXTE,
            leftIndent=8, spaceAfter=4),
        "center": ParagraphStyle("center",
            fontSize=9, fontName="Helvetica", alignment=TA_CENTER),
    }


# ─── Section header (bandeau titre) ───────────────────────────────────────────
def section_band(title: str, accent=BLEU) -> Table:
    """Bandeau de section coloré avec trait latéral terracotta."""
    row = [[
        Paragraph(f"<font color='#C4603A'>▌</font>&nbsp;&nbsp;<b>{title}</b>",
                  ParagraphStyle("sh", fontSize=11, fontName="Helvetica-Bold",
                                 textColor=BLANC, leading=14))
    ]]
    tbl = Table(row, colWidths=[USEFUL_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), accent),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return tbl


# ─── Table générique ──────────────────────────────────────────────────────────
def make_table(data, col_widths=None, header=True, accent=BLEU):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANC, GRIS]),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ]
    if header:
        cmds += [
            ("BACKGROUND",  (0, 0), (-1, 0), accent),
            ("TEXTCOLOR",   (0, 0), (-1, 0), BLANC),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 8),
            ("TOPPADDING",  (0, 0), (-1, 0), 7),
            ("BOTTOMPADDING",(0, 0),(-1, 0), 7),
        ]
    t.setStyle(TableStyle(cmds))
    return t


# ─── Score badge ──────────────────────────────────────────────────────────────
def score_badge(label: str, value: str, color=BLEU, width=USEFUL_W) -> Table:
    """Badge coloré affichant un score."""
    row = [[Paragraph(
        f"<font color='white'><b>{label}</b>&nbsp;&nbsp;{value}</font>",
        ParagraphStyle("sb", fontSize=10, fontName="Helvetica-Bold",
                       textColor=BLANC, alignment=TA_CENTER, leading=14)
    )]]
    tbl = Table(row, colWidths=[width])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), color),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROWBORDER",     (0, 0), (-1, -1), 0, BLANC),
    ]))
    return tbl


# ─── Cover page helper ────────────────────────────────────────────────────────
def make_cover(story, title: str, subtitle: str, patient_info: dict,
               bilans_df, labels: list, styles: dict):
    """Génère la page de garde moderne."""
    import pandas as pd

    # Grand bandeau coloré en haut
    band_data = [[Paragraph(
        f"<font color='white'><b>{title}</b></font>",
        ParagraphStyle("ct", fontSize=22, fontName="Helvetica-Bold",
                       textColor=BLANC, alignment=TA_CENTER)
    )]]
    band = Table(band_data, colWidths=[USEFUL_W])
    band.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLEU),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(Spacer(1, 1*cm))
    story.append(band)

    # Sous-bande terracotta
    sub_data = [[Paragraph(
        f"<font color='white'>{subtitle}</font>",
        ParagraphStyle("cs", fontSize=11, fontName="Helvetica",
                       textColor=BLANC, alignment=TA_CENTER)
    )]]
    sub_band = Table(sub_data, colWidths=[USEFUL_W])
    sub_band.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), TERRA),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sub_band)
    story.append(Spacer(1, 0.8*cm))

    # Logo centré
    logo = get_logo(width=5*cm, height=2*cm)
    if logo:
        logo_row = [[logo]]
        logo_tbl = Table(logo_row, colWidths=[USEFUL_W])
        logo_tbl.setStyle(TableStyle([("ALIGN", (0,0),(-1,-1),"CENTER")]))
        story.append(logo_tbl)
        story.append(Spacer(1, 0.6*cm))

    # Infos patient sur fond bleu clair
    nom_complet = f"{patient_info.get('nom','')} {patient_info.get('prenom','')}".strip()
    n = len(bilans_df)
    pat_data = [
        ["Patient",          nom_complet],
        ["Date de naissance", str(patient_info.get("date_naissance","—"))],
        ["Sexe",             patient_info.get("sexe","—")],
        ["Profession",       patient_info.get("profession","—") or "—"],
        ["Nombre de bilans", str(n)],
        ["Rapport généré le", date.today().strftime("%d/%m/%Y")],
    ]
    pat_tbl = Table(pat_data, colWidths=[4.5*cm, USEFUL_W - 4.5*cm])
    pat_tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 0), (0, -1),  BLEU),
        ("TEXTCOLOR",     (1, 0), (1, -1),  NOIR),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [BLANC, BLEU_LIGHT]),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(pat_tbl)
    story.append(Spacer(1, 0.6*cm))

    # Tableau des bilans
    story.append(Paragraph("Bilans inclus dans ce rapport", styles["subsection"]))
    bil_rows = [["#", "Date", "Type", "Praticien"]]
    for i, (_, row) in enumerate(bilans_df.iterrows()):
        d = row["date_bilan"]
        ds = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        bil_rows.append([str(i+1), ds,
                         row.get("type_bilan","—") or "—",
                         row.get("praticien","—") or "—"])
    story.append(make_table(bil_rows,
                            col_widths=[1.2*cm, 3.2*cm, 5*cm, USEFUL_W-9.4*cm]))
