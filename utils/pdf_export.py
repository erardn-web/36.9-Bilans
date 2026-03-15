"""
Génération du rapport PDF d'évolution SHV
Utilise ReportLab Platypus pour un rendu professionnel.
"""

import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

# ─── Palette couleurs ─────────────────────────────────────────────────────────
BLEU_FONCE  = colors.HexColor("#1a3c5e")
BLEU_CLAIR  = colors.HexColor("#e0ecf8")
ORANGE      = colors.HexColor("#f57c00")
VERT        = colors.HexColor("#388e3c")
ROUGE       = colors.HexColor("#d32f2f")
GRIS_CLAIR  = colors.HexColor("#f5f5f5")
GRIS_TEXTE  = colors.HexColor("#555555")
BLANC       = colors.white


def safe_num(val):
    try:
        v = float(val)
        return v if v != 0 else None
    except (TypeError, ValueError):
        return None


def val_str(val, suffix=""):
    v = safe_num(val)
    if v is None:
        return "—"
    if v == int(v):
        return f"{int(v)}{suffix}"
    return f"{v}{suffix}"


def had_color(score):
    s = safe_num(score)
    if s is None: return GRIS_TEXTE
    if s <= 7:    return VERT
    if s <= 10:   return ORANGE
    return ROUGE


def bolt_color(score):
    s = safe_num(score)
    if s is None: return GRIS_TEXTE
    if s < 10:    return ROUGE
    if s < 20:    return ORANGE
    if s < 40:    return colors.HexColor("#fbc02d")
    return VERT


def sf36_color(score):
    s = safe_num(score)
    if s is None: return GRIS_TEXTE
    if s >= 66:   return VERT
    if s >= 33:   return ORANGE
    return ROUGE


# ─── Styles ───────────────────────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Title"],
            fontSize=22, textColor=BLEU_FONCE,
            spaceAfter=4, alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=11, textColor=GRIS_TEXTE,
            spaceAfter=2, alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "section", parent=base["Heading1"],
            fontSize=13, textColor=BLANC,
            spaceBefore=14, spaceAfter=6,
            backColor=BLEU_FONCE,
            leftIndent=-6, rightIndent=-6,
            borderPadding=(4, 6, 4, 6),
        ),
        "subsection": ParagraphStyle(
            "subsection", parent=base["Heading2"],
            fontSize=11, textColor=BLEU_FONCE,
            spaceBefore=10, spaceAfter=4,
            borderPadding=(2, 0, 2, 0),
        ),
        "normal": ParagraphStyle(
            "normal", parent=base["Normal"],
            fontSize=9, textColor=GRIS_TEXTE, spaceAfter=2,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"],
            fontSize=8, textColor=GRIS_TEXTE,
        ),
        "bold": ParagraphStyle(
            "bold", parent=base["Normal"],
            fontSize=9, textColor=BLEU_FONCE, fontName="Helvetica-Bold",
        ),
        "center": ParagraphStyle(
            "center", parent=base["Normal"],
            fontSize=9, alignment=TA_CENTER,
        ),
        "note": ParagraphStyle(
            "note", parent=base["Normal"],
            fontSize=8, textColor=GRIS_TEXTE,
            leftIndent=10, spaceAfter=4,
            borderPadding=4,
        ),
    }
    return styles


# ─── Entête de page ───────────────────────────────────────────────────────────

def make_header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = A4
    # Bandeau haut
    canvas_obj.setFillColor(BLEU_FONCE)
    canvas_obj.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)
    canvas_obj.setFillColor(BLANC)
    canvas_obj.setFont("Helvetica-Bold", 10)
    canvas_obj.drawString(1.5*cm, h - 0.85*cm, "36.9 Bilans — Rapport d'évolution SHV")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawRightString(w - 1.5*cm, h - 0.85*cm, f"Page {doc.page}")
    # Ligne pied de page
    canvas_obj.setStrokeColor(BLEU_CLAIR)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(1.5*cm, 1.2*cm, w - 1.5*cm, 1.2*cm)
    canvas_obj.setFillColor(GRIS_TEXTE)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawString(1.5*cm, 0.7*cm, "Document confidentiel — Usage médical")
    canvas_obj.drawRightString(w - 1.5*cm, 0.7*cm, f"Généré le {date.today().strftime('%d/%m/%Y')}")
    canvas_obj.restoreState()


# ─── Table générique ──────────────────────────────────────────────────────────

def make_table(data, col_widths=None, header=True):
    """data : liste de listes. Première ligne = en-têtes si header=True."""
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANC, GRIS_CLAIR]),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        cmds += [
            ("BACKGROUND",  (0, 0), (-1, 0), BLEU_FONCE),
            ("TEXTCOLOR",   (0, 0), (-1, 0), BLANC),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 8),
        ]
    t.setStyle(TableStyle(cmds))
    return t


# ─── Générateur principal ─────────────────────────────────────────────────────

def generate_pdf(bilans_df, patient_info: dict) -> bytes:
    """
    Génère le PDF complet d'évolution.
    Retourne les bytes du fichier PDF.
    """
    import pandas as pd

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.0*cm, bottomMargin=1.8*cm,
        title=f"Bilan SHV – {patient_info.get('nom')} {patient_info.get('prenom')}",
    )

    styles = make_styles()
    story  = []
    w      = A4[0] - 3*cm  # largeur utile

    # Trier bilans par date
    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)
    n_bilans  = len(bilans_df)

    def bilan_label(row):
        d = row["date_bilan"]
        ds = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        return f"{ds} — {row.get('type_bilan','')}"

    labels = [bilan_label(r) for _, r in bilans_df.iterrows()]

    # ══════════════════════════════════════════════════════════════════
    #  PAGE DE GARDE
    # ══════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Rapport d'évolution", styles["title"]))
    story.append(Paragraph("Syndrome d'Hyperventilation (SHV)", styles["subtitle"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLEU_FONCE))
    story.append(Spacer(1, 0.4*cm))

    # Infos patient
    pat_data = [
        ["Patient",     f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"],
        ["Date de naissance", str(patient_info.get("date_naissance", "—"))],
        ["Sexe",        patient_info.get("sexe", "—")],
        ["Profession",  patient_info.get("profession", "—") or "—"],
        ["ID patient",  patient_info.get("patient_id", "—")],
        ["Nombre de bilans", str(n_bilans)],
        ["Rapport généré le", date.today().strftime("%d/%m/%Y")],
    ]
    pat_table = Table(pat_data, colWidths=[5*cm, w - 5*cm])
    pat_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("FONTNAME",    (0, 0), (0, -1),  "Helvetica-Bold"),
        ("TEXTCOLOR",   (0, 0), (0, -1),  BLEU_FONCE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(pat_table)
    story.append(Spacer(1, 0.6*cm))

    # Tableau des bilans
    story.append(Paragraph("Bilans inclus dans ce rapport", styles["subsection"]))
    bil_header = [["#", "Date", "Type de bilan", "Praticien"]]
    bil_rows   = []
    for i, (_, row) in enumerate(bilans_df.iterrows()):
        d  = row["date_bilan"]
        ds = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        bil_rows.append([
            str(i + 1), ds,
            row.get("type_bilan", "—"),
            row.get("praticien", "—") or "—",
        ])
    story.append(make_table(bil_header + bil_rows,
                            col_widths=[1*cm, 3*cm, 6*cm, w - 10*cm]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  TABLEAU DE SYNTHÈSE DES SCORES
    # ══════════════════════════════════════════════════════════════════
    story.append(Paragraph("Synthèse des scores", styles["section"]))
    story.append(Spacer(1, 0.2*cm))

    synth_header = [["Indicateur"] + [f"B{i+1}" for i in range(n_bilans)]]
    synth_rows   = []

    def synth_row(label, key, suffix="", color_fn=None):
        vals = [val_str(r.get(key), suffix) for _, r in bilans_df.iterrows()]
        row  = [label] + vals
        return row

    synth_rows.append(synth_row("HAD Anxiété (/21)",    "had_score_anxiete"))
    synth_rows.append(synth_row("HAD Dépression (/21)", "had_score_depression"))
    synth_rows.append([""] + [""] * n_bilans)   # séparateur
    synth_rows.append(synth_row("BOLT (secondes)",      "bolt_score", "s"))
    synth_rows.append([""] + [""] * n_bilans)
    synth_rows.append(synth_row("SF36 – Fonct. physique",    "sf36_pf"))
    synth_rows.append(synth_row("SF36 – Limit. physique",    "sf36_rp"))
    synth_rows.append(synth_row("SF36 – Douleur",            "sf36_bp"))
    synth_rows.append(synth_row("SF36 – Santé générale",     "sf36_gh"))
    synth_rows.append(synth_row("SF36 – Vitalité",           "sf36_vt"))
    synth_rows.append(synth_row("SF36 – Vie sociale",        "sf36_sf"))
    synth_rows.append(synth_row("SF36 – Limit. émotionnel",  "sf36_re"))
    synth_rows.append(synth_row("SF36 – Santé psychique",    "sf36_mh"))
    synth_rows.append([""] + [""] * n_bilans)
    synth_rows.append(synth_row("HVT – Retour normal (min)", "hvt_duree_retour", " min"))

    col_w = [6*cm] + [(w - 6*cm) / n_bilans] * n_bilans
    synth_table = make_table(synth_header + synth_rows, col_widths=col_w)

    # Coloriser les lignes HAD, BOLT, SF36
    extra_cmds = []
    offset = 1   # ligne 0 = header
    for i, row_data in enumerate(synth_rows):
        row_idx = i + offset
        label   = row_data[0] if row_data else ""
        for j in range(1, n_bilans + 1):
            raw_val = bilans_df.iloc[j - 1].get(
                {"HAD Anxiété (/21)": "had_score_anxiete",
                 "HAD Dépression (/21)": "had_score_depression",
                 "BOLT (secondes)": "bolt_score",
                }.get(label, ""), None
            )
            if "HAD" in label:
                c = had_color(raw_val)
            elif "BOLT" in label:
                c = bolt_color(raw_val)
            elif "SF36" in label:
                raw_val = bilans_df.iloc[j - 1].get(
                    "sf36_" + {
                        "SF36 – Fonct. physique": "pf",
                        "SF36 – Limit. physique": "rp",
                        "SF36 – Douleur": "bp",
                        "SF36 – Santé générale": "gh",
                        "SF36 – Vitalité": "vt",
                        "SF36 – Vie sociale": "sf",
                        "SF36 – Limit. émotionnel": "re",
                        "SF36 – Santé psychique": "mh",
                    }.get(label, ""), None)
                c = sf36_color(raw_val)
            else:
                continue
            if c != GRIS_TEXTE:
                extra_cmds.append(("TEXTCOLOR", (j, row_idx), (j, row_idx), c))
                extra_cmds.append(("FONTNAME",  (j, row_idx), (j, row_idx), "Helvetica-Bold"))

    synth_table.setStyle(TableStyle(synth_table._cmds + extra_cmds))
    story.append(synth_table)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Légende HAD : vert = normal (0–7) · orange = douteux (8–10) · rouge = pathologique (11–21)   |   "
        "BOLT : rouge < 10s · orange < 20s · jaune < 40s · vert ≥ 40s   |   "
        "SF36 : vert ≥ 66 · orange ≥ 33 · rouge < 33",
        styles["small"],
    ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  DÉTAIL BILAN PAR BILAN
    # ══════════════════════════════════════════════════════════════════
    for i, (_, row) in enumerate(bilans_df.iterrows()):
        story.append(Paragraph(
            f"Bilan {i+1} — {labels[i]}", styles["section"]
        ))
        story.append(Spacer(1, 0.2*cm))

        # Infos générales
        if row.get("notes_generales"):
            story.append(Paragraph("Notes générales", styles["subsection"]))
            story.append(Paragraph(str(row["notes_generales"]), styles["note"]))

        # ── HAD ─────────────────────────────────────────────────────
        story.append(Paragraph("Échelle HAD", styles["subsection"]))
        had_data = [
            ["", "Score", "Interprétation"],
            ["Anxiété",
             val_str(row.get("had_score_anxiete")) + "/21",
             ("Normal" if safe_num(row.get("had_score_anxiete")) is None
              else "Normal (0–7)" if safe_num(row.get("had_score_anxiete")) <= 7
              else "Douteux (8–10)" if safe_num(row.get("had_score_anxiete")) <= 10
              else "Pathologique (11–21)")],
            ["Dépression",
             val_str(row.get("had_score_depression")) + "/21",
             ("Normal" if safe_num(row.get("had_score_depression")) is None
              else "Normal (0–7)" if safe_num(row.get("had_score_depression")) <= 7
              else "Douteux (8–10)" if safe_num(row.get("had_score_depression")) <= 10
              else "Pathologique (11–21)")],
        ]
        story.append(make_table(had_data, col_widths=[4*cm, 3*cm, w - 7*cm]))

        # ── BOLT ────────────────────────────────────────────────────
        story.append(Paragraph("Test BOLT", styles["subsection"]))
        bolt_s    = safe_num(row.get("bolt_score"))
        bolt_interp = row.get("bolt_interpretation", "—") or "—"
        bolt_data   = [
            ["Score BOLT", "Interprétation"],
            [val_str(row.get("bolt_score"), " s"), bolt_interp],
        ]
        story.append(make_table(bolt_data, col_widths=[4*cm, w - 4*cm]))

        # ── SF-36 ───────────────────────────────────────────────────
        story.append(Paragraph("SF-36 — Qualité de vie", styles["subsection"]))
        sf_dims = [
            ("Fonctionnement physique",       "sf36_pf"),
            ("Limitations physiques",          "sf36_rp"),
            ("Douleur physique",               "sf36_bp"),
            ("Santé générale",                 "sf36_gh"),
            ("Vitalité",                       "sf36_vt"),
            ("Vie et relations sociales",      "sf36_sf"),
            ("Limitations émotionnelles",      "sf36_re"),
            ("Santé psychique",                "sf36_mh"),
        ]
        sf_header = [["Dimension", "Score /100"]]
        sf_rows   = [[label, val_str(row.get(key))] for label, key in sf_dims]
        story.append(make_table(sf_header + sf_rows, col_widths=[10*cm, w - 10*cm]))

        # ── HVT ─────────────────────────────────────────────────────
        story.append(Paragraph("Test d'hyperventilation volontaire", styles["subsection"]))
        hvt_rows = [
            ["Symptômes reproduits",    str(row.get("hvt_symptomes_reproduits", "—") or "—")],
            ["Retour à la normale",     val_str(row.get("hvt_duree_retour"), " min")],
            ["Symptômes observés",
             str(row.get("hvt_symptomes_list", "—") or "—").replace("|", " · ")],
        ]
        if row.get("hvt_notes"):
            hvt_rows.append(["Notes", str(row["hvt_notes"])])

        hvt_table = Table(hvt_rows, colWidths=[5*cm, w - 5*cm])
        hvt_table.setStyle(TableStyle([
            ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("TEXTCOLOR",   (0, 0), (0, -1), BLEU_FONCE),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLANC, GRIS_CLAIR]),
            ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("TOPPADDING",  (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(hvt_table)

        if i < n_bilans - 1:
            story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  BUILD
    # ══════════════════════════════════════════════════════════════════
    doc.build(story, onFirstPage=make_header_footer, onLaterPages=make_header_footer)
    return buffer.getvalue()
