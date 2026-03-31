"""
utils/pdf_cover.py — Page de garde moderne (canvas-based)
Design : blanc épuré, accents bleu/terracotta, style clinique suisse.
Layout entièrement calculé dynamiquement — le bloc IA s'étend pour
remplir l'espace disponible entre la timeline et le footer.
"""

import os
import re as _re
import pandas as pd
from datetime import date as _date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth

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

M        = 1.5 * cm   # marge latérale
FOOTER_H = 3.2 * cm   # hauteur réservée au footer (depuis le bas)


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


def _rrect(canvas, x, y, w, h, r, fill=None, stroke=None, lw=0.5):
    """Raccourci roundRect avec fill/stroke optionnels."""
    canvas.saveState()
    if fill:
        canvas.setFillColor(fill)
    if stroke:
        canvas.setStrokeColor(stroke)
        canvas.setLineWidth(lw)
    canvas.roundRect(x, y, w, h, r,
                     fill=1 if fill else 0,
                     stroke=1 if stroke else 0)
    canvas.restoreState()


def draw_cover_canvas(canvas, doc,
                      patient_info: dict,
                      bilans_df: pd.DataFrame,
                      labels: list,
                      analyse_text: str,
                      template_nom: str,
                      medecin_info: dict):
    """
    Dessine la page de garde complète directement sur le canvas ReportLab.
    Appelé via make_cover_callback() -> PageTemplate.onPage.
    """
    canvas.saveState()
    W, H = A4

    # ── 1. Double accent couleur en haut ──────────────────────────────────────
    canvas.setFillColor(_BLEU)
    canvas.rect(0, H - 5, W, 5, fill=1, stroke=0)
    canvas.setFillColor(_TERRA)
    canvas.rect(0, H - 7.5, W * 0.28, 2.5, fill=1, stroke=0)

    # ── 2. Logo + identité cabinet (haut gauche) ──────────────────────────────
    logo_h  = 0.9 * cm
    logo_y  = H - 2.20 * cm
    logo_x  = M
    name_x  = M

    logo_path = _find_logo()
    if logo_path:
        try:
            canvas.drawImage(logo_path, logo_x, logo_y,
                             width=2.6 * cm, height=logo_h,
                             preserveAspectRatio=True, mask="auto")
            name_x = logo_x + 2.8 * cm
        except Exception:
            logo_path = None

    if not logo_path:
        _rrect(canvas, logo_x, logo_y, logo_h, logo_h, 4, fill=_BLEU)
        canvas.setFillColor(_WHITE)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.drawCentredString(logo_x + logo_h / 2, logo_y + 0.30 * cm, "36.9")
        name_x = logo_x + logo_h + 0.35 * cm

    canvas.setFillColor(_BLEU)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(name_x, logo_y + 0.54 * cm, "36.9 Bilans")
    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(name_x, logo_y + 0.18 * cm, "Physiotherapie")

    # ── 3. Bloc destinataire (haut droite) ────────────────────────────────────
    nom_med  = (medecin_info or {}).get("nom", "").strip()
    spec_med = (medecin_info or {}).get("specialite", "").strip()
    adr_med  = (medecin_info or {}).get("adresse", "").strip()

    if nom_med or spec_med:
        dest_x = W - M
        dy     = H - 1.50 * cm

        canvas.setFillColor(_TERRA)
        canvas.setFont("Helvetica-Bold", 6.5)
        canvas.drawRightString(dest_x, dy, "À L'ATTENTION DE")
        dy -= 0.40 * cm

        if nom_med:
            canvas.setFillColor(_NOIR)
            canvas.setFont("Helvetica-Bold", 10.5)
            canvas.drawRightString(dest_x, dy, f"Dr. {nom_med}")
            dy -= 0.38 * cm
        if spec_med:
            canvas.setFillColor(_GRIS_555)
            canvas.setFont("Helvetica", 8.5)
            canvas.drawRightString(dest_x, dy, spec_med)
            dy -= 0.30 * cm
        if adr_med:
            canvas.setFillColor(_GRIS_999)
            canvas.setFont("Helvetica", 7.5)
            canvas.drawRightString(dest_x, dy, adr_med)

    # ── 4. Séparateur horizontal ──────────────────────────────────────────────
    sep_y = logo_y - 0.48 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.5)
    canvas.line(M, sep_y, W - M, sep_y)

    # curseur qui descend depuis le séparateur
    y = sep_y - 0.65 * cm

    # ── 5. Hero : label RAPPORT + titre + pill ────────────────────────────────
    canvas.setFillColor(_TERRA)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(M, y, "RAPPORT D'EVOLUTION")
    y -= 0.92 * cm

    canvas.setFillColor(_NOIR)
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawString(M, y, str(template_nom or "Bilan"))
    y -= 0.68 * cm

    # Pill : nb bilans + années
    n_bilans = len(bilans_df)
    try:
        dates_ok = bilans_df["date_bilan"].dropna()
        if len(dates_ok) >= 2:
            y1 = dates_ok.iloc[0].strftime("%Y")
            y2 = dates_ok.iloc[-1].strftime("%Y")
            date_rng = f"{y1}–{y2}" if y1 != y2 else y1
        elif len(dates_ok) == 1:
            date_rng = dates_ok.iloc[0].strftime("%Y")
        else:
            date_rng = ""
    except Exception:
        date_rng = ""

    plural   = "s" if n_bilans > 1 else ""
    pill_txt = f"{n_bilans} bilan{plural}  {'·  ' + date_rng if date_rng else ''}"
    pill_fs  = 8.5
    txt_w    = stringWidth(pill_txt, "Helvetica-Bold", pill_fs)
    pill_w   = txt_w + 1.2 * cm
    pill_h   = 0.50 * cm
    pill_y   = y - 0.10 * cm

    _rrect(canvas, M, pill_y, pill_w, pill_h, 10, fill=_BLEU_BG)
    canvas.setFillColor(_BLEU)
    canvas.circle(M + 0.28 * cm, pill_y + pill_h / 2, 3, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", pill_fs)
    canvas.setFillColor(_BLEU)
    canvas.drawString(M + 0.50 * cm, pill_y + 0.08 * cm, pill_txt)

    y = pill_y - 0.72 * cm

    # ── 6. Carte patient ──────────────────────────────────────────────────────
    card_h   = 2.70 * cm
    card_w   = W - 2 * M
    hdr_h    = 0.58 * cm
    mid_x    = M + card_w / 2
    card_top = y

    _rrect(canvas, M, card_top - card_h, card_w, card_h, 6,
           fill=_WHITE, stroke=_GRIS_BORD, lw=0.6)

    # En-tête grisée
    _rrect(canvas, M, card_top - hdr_h, card_w, hdr_h, 6, fill=_CARD_BG)
    canvas.setFillColor(_WHITE)
    canvas.rect(M + 1, card_top - hdr_h, card_w - 2, hdr_h * 0.5, fill=1, stroke=0)
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(M, card_top - hdr_h, M + card_w, card_top - hdr_h)

    canvas.setFillColor(_BLEU)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(M + 0.40 * cm, card_top - 0.38 * cm, "PATIENT")

    # Séparateurs internes
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(mid_x, card_top - hdr_h, mid_x, card_top - card_h + 2)
    row_div = card_top - hdr_h - (card_h - hdr_h) / 2
    canvas.line(M + 1, row_div, M + card_w - 1, row_div)

    def _cell(cx, cy, label, value, maxlen=30):
        v = str(value or "—")
        if len(v) > maxlen:
            v = v[:maxlen - 1] + "…"
        canvas.setFillColor(_GRIS_999)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(cx, cy + 0.31 * cm, label)
        canvas.setFillColor(_NOIR)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(cx, cy + 0.03 * cm, v)

    age_str = "—"
    try:
        ddn_raw = patient_info.get("date_naissance", "")
        if ddn_raw:
            ddn_p = pd.to_datetime(str(ddn_raw), errors="coerce")
            if pd.notna(ddn_p):
                today = _date.today()
                age   = today.year - ddn_p.year - (
                    (today.month, today.day) < (ddn_p.month, ddn_p.day))
                age_str = f"{ddn_p.strftime('%d.%m.%Y')}  ·  {age} ans"
    except Exception:
        pass

    nom_full = (
        f"{(patient_info.get('nom') or '').upper()} "
        f"{(patient_info.get('prenom') or '')}".strip()
    )
    pid = str(patient_info.get("patient_id", "—"))

    row1_y = row_div + 0.52 * cm
    row2_y = row_div - 0.58 * cm

    _cell(M + 0.40 * cm,     row1_y, "Nom",               nom_full, maxlen=28)
    _cell(mid_x + 0.40 * cm, row1_y, "Date de naissance", age_str,  maxlen=32)
    _cell(M + 0.40 * cm,     row2_y, "Sexe",              patient_info.get("sexe", "—"))
    _cell(mid_x + 0.40 * cm, row2_y, "N° dossier",        pid)

    y = card_top - card_h - 0.72 * cm

    # ── 7. Timeline des bilans ────────────────────────────────────────────────
    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(M, y, "BILANS INCLUS")

    tl_y   = y - 0.78 * cm
    n      = len(bilans_df)
    circ_r = 9

    if n > 0:
        slot_w = (W - 2 * M) / n

        if n > 1:
            cx_f = M + slot_w * 0.5
            cx_l = M + slot_w * (n - 0.5)
            canvas.setStrokeColor(_GRIS_BORD)
            canvas.setLineWidth(1.2)
            canvas.line(cx_f, tl_y, cx_l, tl_y)

        for i, (_, row) in enumerate(bilans_df.iterrows()):
            cx      = M + slot_w * (i + 0.5)
            is_last = (i == n - 1)
            dot_col = _TERRA if is_last else _BLEU

            canvas.setFillColor(dot_col)
            canvas.circle(cx, tl_y, circ_r, fill=1, stroke=0)
            canvas.setFillColor(_WHITE)
            canvas.setFont("Helvetica-Bold", 7.5)
            canvas.drawCentredString(cx, tl_y - 2.8, str(i + 1))

            try:
                d  = row.get("date_bilan")
                ds = d.strftime("%d.%m.%Y") if pd.notna(d) else "—"
            except Exception:
                ds = "—"

            canvas.setFillColor(dot_col)
            canvas.setFont("Helvetica-Bold", 8.5)
            canvas.drawCentredString(cx, tl_y - circ_r - 0.38 * cm, ds)

            praticien = str(row.get("praticien", "") or "")
            if praticien:
                canvas.setFillColor(_GRIS_999)
                canvas.setFont("Helvetica", 7.5)
                canvas.drawCentredString(cx, tl_y - circ_r - 0.68 * cm, praticien)

    # Point bas de la timeline
    tl_bottom = tl_y - circ_r - 1.0 * cm

    # ── 8. Synthèse IA ── remplit dynamiquement tout l'espace disponible ──────
    ai_text = str(analyse_text or "").strip()

    # Nettoyer le Markdown pour un rendu PDF propre
    ai_text = _re.sub(r'^#+\s*', '', ai_text, flags=_re.MULTILINE)
    ai_text = _re.sub(r'\*\*(.*?)\*\*', r'\1', ai_text)
    ai_text = _re.sub(r'\*(.*?)\*', r'\1', ai_text)
    ai_text = ai_text.strip()

    footer_top = FOOTER_H + 0.6 * cm  # limite basse du contenu
    ai_top     = tl_bottom             # limite haute du bloc IA

    if ai_text and ai_top > footer_top + 1.5 * cm:
        avail_h = ai_top - footer_top

        # Label
        canvas.setFillColor(_TERRA)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.drawString(M + 0.42 * cm, ai_top - 0.40 * cm,
                          "SYNTHÈSE PHYSIOTHÉRAPEUTIQUE")

        # Barre laterale terracotta (toute la hauteur du bloc)
        canvas.setFillColor(_TERRA)
        canvas.rect(M, footer_top, 2.5, avail_h, fill=1, stroke=0)

        # Zone texte
        lbl_h   = 0.55 * cm
        text_x  = M + 0.42 * cm
        text_w  = W - 2 * M - 0.52 * cm
        text_top = ai_top - lbl_h - 0.20 * cm
        text_h   = text_top - footer_top - 0.15 * cm

        # Taille de police adaptative : on cherche la plus grande qui rentre
        for font_size, leading in [
            (10,   15),
            (9.5,  14),
            (9,    13.5),
            (8.5,  13),
            (8,    12),
            (7.5,  11.5),
        ]:
            ai_style = ParagraphStyle(
                "ai_cvr",
                fontSize=font_size,
                fontName="Helvetica",
                textColor=colors.HexColor("#333333"),
                leading=leading,
            )
            # Remplacer les sauts de ligne par <br/> pour le paragraphe
            html_text = ai_text.replace("\n\n", "<br/><br/>").replace("\n", " ")
            p = Paragraph(html_text, ai_style)
            p_w, p_h = p.wrap(text_w, 9999)
            if p_h <= text_h:
                break  # cette taille rentre

        # Clipper proprement pour ne pas mordre sur le footer
        canvas.saveState()
        canvas.clipRect(text_x, footer_top + 0.10 * cm,
                        text_w, text_top - footer_top, stroke=0)
        p.drawOn(canvas, text_x, text_top - p_h)
        canvas.restoreState()

    # ── 9. Footer ─────────────────────────────────────────────────────────────
    foot_line = FOOTER_H - 0.12 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.5)
    canvas.line(M, foot_line, W - M, foot_line)

    praticien_nom = ""
    try:
        praticien_nom = str(bilans_df.iloc[-1].get("praticien", "") or "")
    except Exception:
        pass

    # Gauche : praticien
    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(M, foot_line - 0.36 * cm, "Praticien responsable")
    canvas.setFillColor(_NOIR)
    canvas.setFont("Helvetica-Bold", 10.5)
    canvas.drawString(M, foot_line - 0.74 * cm, praticien_nom or "—")
    canvas.setFillColor(_GRIS_555)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(M, foot_line - 1.04 * cm, "Physiothérapeute diplômé")

    # Droite : date
    canvas.setFillColor(_GRIS_999)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(W - M, foot_line - 0.36 * cm, "Généré le")
    canvas.setFillColor(_NOIR)
    canvas.setFont("Helvetica-Bold", 10.5)
    canvas.drawRightString(W - M, foot_line - 0.74 * cm,
                           _date.today().strftime("%d.%m.%Y"))
    canvas.setFillColor(_GRIS_AAA)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(W - M, foot_line - 1.04 * cm,
                           "Document confidentiel · Usage médical exclusif")

    # ── 10. Bande bleue en bas ────────────────────────────────────────────────
    canvas.setFillColor(_BLEU)
    canvas.rect(0, 0, W, 5, fill=1, stroke=0)

    canvas.restoreState()


def make_cover_callback(patient_info: dict, bilans_df: pd.DataFrame,
                        labels: list, analyse_text: str,
                        template_nom: str, medecin_info: dict):
    """
    Retourne la fonction onPage à passer au PageTemplate de couverture.
    """
    def _draw(canvas, doc):
        draw_cover_canvas(
            canvas, doc,
            patient_info = patient_info,
            bilans_df    = bilans_df,
            labels       = labels,
            analyse_text = analyse_text,
            template_nom = template_nom,
            medecin_info = medecin_info,
        )
    return _draw
