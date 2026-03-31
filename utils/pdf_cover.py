"""
utils/pdf_cover.py — Page de garde moderne (canvas-based)
Design : blanc épuré, accents bleu/terracotta, style clinique suisse.
Appelé via onPage d'un PageTemplate dédié dans generate_pdf.
"""

import os
import io
import pandas as pd
from datetime import date as _date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

# ── Palette ───────────────────────────────────────────────────────────────────
_BLEU      = colors.HexColor("#2B57A7")
_TERRA     = colors.HexColor("#C4603A")
_NOIR      = colors.HexColor("#1A1A1A")
_GRIS_555  = colors.HexColor("#555555")
_GRIS_999  = colors.HexColor("#999999")
_GRIS_AAA  = colors.HexColor("#AAAAAA")
_GRIS_BORD = colors.HexColor("#E0E0E0")
_BLEU_BG   = colors.HexColor("#E8EEF9")
_CARD_BG   = colors.HexColor("#F8F9FC")
_WHITE     = colors.white

M = 1.5 * cm  # marge latérale standard


def _find_logo():
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo_369.png"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_369.png"),
        "assets/logo_369.png",
        "/mount/src/36.9-bilans/assets/logo_369.png",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def draw_cover_canvas(canvas, doc, patient_info: dict, bilans_df: pd.DataFrame,
                      labels: list, analyse_text: str,
                      template_nom: str, medecin_info: dict):
    """
    Dessine la page de garde complète directement sur le canvas ReportLab.
    À appeler uniquement via make_cover_callback() → PageTemplate.onPage.
    """
    canvas.saveState()
    W, H = A4

    # ── 1. Double accent couleur en haut ──────────────────────────────────────
    canvas.setFillColor(_BLEU)
    canvas.rect(0, H - 5, W, 5, fill=1, stroke=0)
    canvas.setFillColor(_TERRA)
    canvas.rect(0, H - 7, W * 0.30, 2, fill=1, stroke=0)

    # ── 2. Logo + identité cabinet (haut gauche) ──────────────────────────────
    logo_h   = 0.85 * cm
    logo_y   = H - 2.1 * cm
    logo_x   = M
    name_x   = M  # sera ajusté après le logo

    logo_path = _find_logo()
    if logo_path:
        try:
            canvas.drawImage(logo_path, logo_x, logo_y,
                             width=2.5 * cm, height=logo_h,
                             preserveAspectRatio=True, mask="auto")
            name_x = logo_x + 2.7 * cm
        except Exception:
            logo_path = None

    if not logo_path:
        canvas.setFillColor(_BLEU)
        canvas.roundRect(logo_x, logo_y, logo_h, logo_h, 4, fill=1, stroke=0)
        canvas.setFillColor(_WHITE)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawCentredString(logo_x + logo_h / 2, logo_y + 0.28 * cm, "36.9")
        name_x = logo_x + logo_h + 0.32 * cm

    canvas.setFillColor(_BLEU)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(name_x, logo_y + 0.51 * cm, "36.9 Bilans")
    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(name_x, logo_y + 0.18 * cm, "Physiotherapie")

    # ── 3. Bloc destinataire (haut droite) ────────────────────────────────────
    nom_med  = (medecin_info or {}).get("nom", "").strip()
    spec_med = (medecin_info or {}).get("specialite", "").strip()
    adr_med  = (medecin_info or {}).get("adresse", "").strip()

    if nom_med or spec_med:
        dest_x = W - M
        dy     = H - 1.48 * cm

        canvas.setFillColor(_TERRA)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.drawRightString(dest_x, dy, "A L'ATTENTION DE")
        dy -= 0.38 * cm

        if nom_med:
            canvas.setFillColor(_NOIR)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawRightString(dest_x, dy, f"Dr. {nom_med}")
            dy -= 0.36 * cm
        if spec_med:
            canvas.setFillColor(_GRIS_555)
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(dest_x, dy, spec_med)
            dy -= 0.30 * cm
        if adr_med:
            canvas.setFillColor(_GRIS_999)
            canvas.setFont("Helvetica", 7.5)
            canvas.drawRightString(dest_x, dy, adr_med)

    # ── 4. Séparateur horizontal ──────────────────────────────────────────────
    sep_y = H - 2.55 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.5)
    canvas.line(M, sep_y, W - M, sep_y)

    # ── 5. Zone hero ──────────────────────────────────────────────────────────
    y = sep_y - 0.88 * cm

    canvas.setFillColor(_TERRA)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(M, y, "RAPPORT D'EVOLUTION")

    y -= 0.72 * cm
    canvas.setFillColor(_NOIR)
    canvas.setFont("Helvetica-Bold", 24)
    title = str(template_nom or "Bilan")
    canvas.drawString(M, y, title)

    # Pill badge
    y -= 0.58 * cm
    n_bilans = len(bilans_df)
    try:
        dates_ok = bilans_df["date_bilan"].dropna()
        if len(dates_ok) >= 2:
            y1 = dates_ok.iloc[0].strftime("%Y")
            y2 = dates_ok.iloc[-1].strftime("%Y")
            date_rng = f"{y1}-{y2}" if y1 != y2 else y1
        elif len(dates_ok) == 1:
            date_rng = dates_ok.iloc[0].strftime("%Y")
        else:
            date_rng = ""
    except Exception:
        date_rng = ""

    plural   = "s" if n_bilans > 1 else ""
    pill_txt = f"{n_bilans} bilan{plural}  {'+  ' + date_rng if date_rng else ''}"
    pill_w   = len(pill_txt) * 0.175 * cm + 1.1 * cm
    canvas.setFillColor(_BLEU_BG)
    canvas.roundRect(M, y - 0.08 * cm, pill_w, 0.44 * cm, 10, fill=1, stroke=0)
    canvas.setFillColor(_BLEU)
    canvas.circle(M + 0.27 * cm, y + 0.13 * cm, 2.5, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(M + 0.44 * cm, y + 0.06 * cm, pill_txt)

    # ── 6. Carte patient ──────────────────────────────────────────────────────
    card_top = y - 0.68 * cm
    card_h   = 2.50 * cm
    card_w   = W - 2 * M
    mid_x    = M + card_w / 2
    hdr_h    = 0.52 * cm

    # Fond blanc + bordure
    canvas.setFillColor(_WHITE)
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.5)
    canvas.roundRect(M, card_top - card_h, card_w, card_h, 5, fill=1, stroke=1)

    # En-tête grisée (hack : roundRect puis rect blanc pour effacer arrondi bas)
    canvas.setFillColor(_CARD_BG)
    canvas.roundRect(M, card_top - hdr_h, card_w, hdr_h, 5, fill=1, stroke=0)
    canvas.setFillColor(_WHITE)
    canvas.rect(M + 1, card_top - hdr_h, card_w - 2, hdr_h * 0.45, fill=1, stroke=0)
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(M, card_top - hdr_h, M + card_w, card_top - hdr_h)

    canvas.setFillColor(_BLEU)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(M + 0.35 * cm, card_top - 0.34 * cm, "PATIENT")

    # Séparateurs internes
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(mid_x, card_top - hdr_h, mid_x, card_top - card_h)
    row_div = card_top - hdr_h - (card_h - hdr_h) / 2
    canvas.line(M, row_div, M + card_w, row_div)

    def _cell(cx, cy, label, value, maxlen=28):
        v = str(value or "—")
        if len(v) > maxlen:
            v = v[:maxlen - 1] + "…"
        canvas.setFillColor(_GRIS_999)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(cx, cy + 0.26 * cm, label)
        canvas.setFillColor(_NOIR)
        canvas.setFont("Helvetica-Bold", 9.5)
        canvas.drawString(cx, cy, v)

    # Calculer âge
    age_str = "—"
    try:
        ddn_raw = patient_info.get("date_naissance", "")
        if ddn_raw:
            ddn_p = pd.to_datetime(str(ddn_raw), errors="coerce")
            if pd.notna(ddn_p):
                today = _date.today()
                age   = today.year - ddn_p.year - ((today.month, today.day) < (ddn_p.month, ddn_p.day))
                age_str = f"{ddn_p.strftime('%d.%m.%Y')}  +  {age} ans"
    except Exception:
        pass

    nom_full = f"{(patient_info.get('nom') or '').upper()} {(patient_info.get('prenom') or '')}".strip()
    pid      = str(patient_info.get("patient_id", "—"))

    row1_y = row_div + 0.44 * cm
    row2_y = row_div - 0.65 * cm

    _cell(M + 0.35 * cm,      row1_y, "Nom",               nom_full, maxlen=26)
    _cell(mid_x + 0.35 * cm,  row1_y, "Date de naissance", age_str,  maxlen=30)
    _cell(M + 0.35 * cm,      row2_y, "Sexe",              patient_info.get("sexe", "—"))
    _cell(mid_x + 0.35 * cm,  row2_y, "N dossier",         pid)

    # ── 7. Timeline des bilans ────────────────────────────────────────────────
    tl_label_y = card_top - card_h - 0.68 * cm
    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(M, tl_label_y, "BILANS INCLUS")

    tl_y   = tl_label_y - 0.68 * cm
    n      = len(bilans_df)
    circ_r = 8

    if n > 0:
        slot_w = (W - 2 * M) / n

        if n > 1:
            cx_f = M + slot_w * 0.5
            cx_l = M + slot_w * (n - 0.5)
            canvas.setStrokeColor(_GRIS_BORD)
            canvas.setLineWidth(1)
            canvas.line(cx_f, tl_y, cx_l, tl_y)

        for i, (_, row) in enumerate(bilans_df.iterrows()):
            cx      = M + slot_w * (i + 0.5)
            is_last = (i == n - 1)
            dot_col = _TERRA if is_last else _BLEU

            canvas.setFillColor(dot_col)
            canvas.circle(cx, tl_y, circ_r, fill=1, stroke=0)
            canvas.setFillColor(_WHITE)
            canvas.setFont("Helvetica-Bold", 7)
            canvas.drawCentredString(cx, tl_y - 2.5, str(i + 1))

            try:
                d  = row.get("date_bilan")
                ds = d.strftime("%d.%m.%Y") if pd.notna(d) else "—"
            except Exception:
                ds = "—"

            canvas.setFillColor(dot_col)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawCentredString(cx, tl_y - circ_r - 0.33 * cm, ds)

            praticien = str(row.get("praticien", "") or "")
            canvas.setFillColor(_GRIS_999)
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString(cx, tl_y - circ_r - 0.62 * cm, praticien)

    # ── 8. Synthèse IA ────────────────────────────────────────────────────────
    ai_top = tl_y - circ_r - 0.95 * cm if n > 0 else card_top - card_h - 1.4 * cm

    if analyse_text and str(analyse_text).strip():
        ai_text = str(analyse_text).strip()
        if len(ai_text) > 500:
            ai_text = ai_text[:497] + "..."

        ai_block_h = 2.1 * cm

        # Bordure gauche terracotta
        canvas.setFillColor(_TERRA)
        canvas.rect(M, ai_top - ai_block_h, 2.5, ai_block_h, fill=1, stroke=0)

        # Label
        canvas.setFillColor(_TERRA)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.drawString(M + 0.32 * cm, ai_top - 0.30 * cm, "SYNTHESE PHYSIOTHERAPEUTIQUE")

        # Paragraphe ReportLab rendu dans le canvas
        ai_style = ParagraphStyle(
            "ai_cover", fontSize=8.5, fontName="Helvetica",
            textColor=colors.HexColor("#444444"), leading=13,
        )
        p = Paragraph(ai_text, ai_style)
        avail_w = W - 2 * M - 0.5 * cm
        avail_h = ai_block_h - 0.5 * cm
        p_w, p_h = p.wrap(avail_w, avail_h)
        p.drawOn(canvas, M + 0.36 * cm, ai_top - 0.5 * cm - p_h)

    # ── 9. Footer ────────────────────────────────────────────────────────────
    foot_y = 2.55 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.5)
    canvas.line(M, foot_y, W - M, foot_y)

    # Praticien (gauche)
    praticien_nom = ""
    try:
        praticien_nom = str(bilans_df.iloc[-1].get("praticien", "") or "")
    except Exception:
        pass

    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(M, foot_y - 0.33 * cm, "Praticien responsable")
    canvas.setFillColor(_NOIR)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(M, foot_y - 0.70 * cm, praticien_nom or "—")
    canvas.setFillColor(_GRIS_555)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(M, foot_y - 1.00 * cm, "Physiotherapeute diplome")

    # Date générée (droite)
    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(W - M, foot_y - 0.33 * cm, "Genere le")
    canvas.setFillColor(_NOIR)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawRightString(W - M, foot_y - 0.70 * cm, _date.today().strftime("%d.%m.%Y"))
    canvas.setFillColor(_GRIS_AAA)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(W - M, foot_y - 1.00 * cm,
                           "Document confidentiel - Usage medical exclusif")

    # ── 10. Bande bleue en bas ────────────────────────────────────────────────
    canvas.setFillColor(_BLEU)
    canvas.rect(0, 0, W, 4, fill=1, stroke=0)

    canvas.restoreState()


def make_cover_callback(patient_info: dict, bilans_df: pd.DataFrame,
                        labels: list, analyse_text: str,
                        template_nom: str, medecin_info: dict):
    """
    Retourne la fonction onPage à passer au PageTemplate de couverture.
    Utilisation :
        cover_cb = make_cover_callback(...)
        PageTemplate(id='Cover', frames=[cover_frame], onPage=cover_cb)
    """
    def _draw(canvas, doc):
        draw_cover_canvas(
            canvas, doc,
            patient_info  = patient_info,
            bilans_df     = bilans_df,
            labels        = labels,
            analyse_text  = analyse_text,
            template_nom  = template_nom,
            medecin_info  = medecin_info,
        )
    return _draw
