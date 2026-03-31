"""
utils/pdf_cover.py — Page de garde canvas-based (v4)

Fontes enregistrées à l'IMPORT du module (pas à l'intérieur du callback)
pour garantir la disponibilité lors du rendu ReportLab/BaseDocTemplate.
Fallback sur Helvetica si les TTF système sont absents.

Typographie : Liberation Sans (Regular/Bold) + DejaVu ExtraLight pour labels.
Texte IA : justifié, taille adaptative, remplit tout l'espace disponible.
"""

import os
import re as _re
import pandas as pd
from datetime import date as _date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth

# ── Palette ───────────────────────────────────────────────────────────────────
_BLEU      = colors.HexColor("#2B57A7")
_TERRA     = colors.HexColor("#C4603A")
_NOIR      = colors.HexColor("#1A1A1A")
_GRIS_33   = colors.HexColor("#333333")
_GRIS_55   = colors.HexColor("#555555")
_GRIS_77   = colors.HexColor("#777777")
_GRIS_99   = colors.HexColor("#999999")
_GRIS_BB   = colors.HexColor("#BBBBBB")
_GRIS_BORD = colors.HexColor("#E0E0E0")
_BLEU_BG   = colors.HexColor("#EBF0FA")
_CARD_BG   = colors.HexColor("#F7F8FC")
_WHITE     = colors.white

M        = 1.5 * cm   # marge latérale
FOOTER_H = 3.0 * cm   # hauteur réservée au footer


# ── Enregistrement des fontes au niveau MODULE ────────────────────────────────
# Doit se faire ICI, pas à l'intérieur des callbacks, pour que les noms
# soient disponibles lors du build() de BaseDocTemplate.

_FONT_CANDIDATES = {
    "Cover-Light": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
    ],
    "Cover-Regular": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "Cover-Bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}

# Noms résolus — remplacés par "Helvetica[-Bold]" si TTF introuvable
F_LIGHT   = "Helvetica"
F_REG     = "Helvetica"
F_BOLD    = "Helvetica-Bold"

def _try_register(internal_name, candidates):
    """Essaie d'enregistrer la fonte ; retourne le nom réussi ou None."""
    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(internal_name, path))
                return internal_name
            except Exception:
                continue
    return None

_r = _try_register("Cover-Light",   _FONT_CANDIDATES["Cover-Light"])
if _r:
    F_LIGHT = _r

_r = _try_register("Cover-Regular", _FONT_CANDIDATES["Cover-Regular"])
if _r:
    F_REG = _r

_r = _try_register("Cover-Bold",    _FONT_CANDIDATES["Cover-Bold"])
if _r:
    F_BOLD = _r


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _rrect(canvas, x, y, w, h, r, fill=None, stroke=None, lw=0.4):
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


# ── Dessin principal ──────────────────────────────────────────────────────────

def draw_cover_canvas(canvas, doc,
                      patient_info: dict,
                      bilans_df: pd.DataFrame,
                      labels: list,
                      analyse_text: str,
                      template_nom: str,
                      medecin_info: dict):
    """
    Dessine la page de garde complète sur le canvas ReportLab.
    Appelé via make_cover_callback() → PageTemplate.onPage.
    """
    canvas.saveState()
    W, H = A4

    # ── 1. Accents couleur haut ───────────────────────────────────────────────
    canvas.setFillColor(_BLEU)
    canvas.rect(0, H - 4.5, W, 4.5, fill=1, stroke=0)
    canvas.setFillColor(_TERRA)
    canvas.rect(0, H - 7, W * 0.26, 2.5, fill=1, stroke=0)

    # ── 2. Logo + cabinet ─────────────────────────────────────────────────────
    logo_h  = 0.85 * cm
    logo_y  = H - 2.15 * cm
    logo_x  = M
    name_x  = M

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
        _rrect(canvas, logo_x, logo_y, logo_h, logo_h, 4, fill=_BLEU)
        canvas.setFillColor(_WHITE)
        canvas.setFont(F_BOLD, 7)
        canvas.drawCentredString(logo_x + logo_h / 2, logo_y + 0.28 * cm, "36.9")
        name_x = logo_x + logo_h + 0.35 * cm

    canvas.setFillColor(_BLEU)
    canvas.setFont(F_REG, 11.5)
    canvas.drawString(name_x, logo_y + 0.52 * cm, "36.9 Bilans")
    canvas.setFillColor(_GRIS_99)
    canvas.setFont(F_LIGHT, 8)
    canvas.drawString(name_x, logo_y + 0.16 * cm, "Physiothérapie")

    # ── 3. Destinataire (haut droite) ─────────────────────────────────────────
    nom_med  = (medecin_info or {}).get("nom", "").strip()
    spec_med = (medecin_info or {}).get("specialite", "").strip()
    adr_med  = (medecin_info or {}).get("adresse", "").strip()

    if nom_med or spec_med:
        dx = W - M
        dy = H - 1.48 * cm
        canvas.setFillColor(_TERRA)
        canvas.setFont(F_BOLD, 6)
        canvas.drawRightString(dx, dy, "À L'ATTENTION DE")
        dy -= 0.40 * cm
        if nom_med:
            canvas.setFillColor(_NOIR)
            canvas.setFont(F_BOLD, 10)
            canvas.drawRightString(dx, dy, f"Dr. {nom_med}")
            dy -= 0.36 * cm
        if spec_med:
            canvas.setFillColor(_GRIS_55)
            canvas.setFont(F_REG, 8)
            canvas.drawRightString(dx, dy, spec_med)
            dy -= 0.28 * cm
        if adr_med:
            canvas.setFillColor(_GRIS_99)
            canvas.setFont(F_LIGHT, 7.5)
            canvas.drawRightString(dx, dy, adr_med)

    # ── 4. Séparateur ─────────────────────────────────────────────────────────
    sep_y = logo_y - 0.46 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.4)
    canvas.line(M, sep_y, W - M, sep_y)

    y = sep_y - 0.62 * cm

    # ── 5. Hero ───────────────────────────────────────────────────────────────
    canvas.setFillColor(_TERRA)
    canvas.setFont(F_BOLD, 7)
    canvas.drawString(M, y, "RAPPORT D'ÉVOLUTION")
    y -= 0.88 * cm

    canvas.setFillColor(_NOIR)
    canvas.setFont(F_REG, 26)
    canvas.drawString(M, y, str(template_nom or "Bilan"))
    y -= 0.62 * cm

    # Pill badge
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
    pill_txt = f"{n_bilans} bilan{plural}{'  ·  ' + date_rng if date_rng else ''}"
    pill_fs  = 8
    txt_w    = stringWidth(pill_txt, F_REG, pill_fs)
    pill_w   = txt_w + 1.1 * cm
    pill_h   = 0.46 * cm
    pill_y   = y - 0.10 * cm

    _rrect(canvas, M, pill_y, pill_w, pill_h, 10, fill=_BLEU_BG)
    canvas.setFillColor(_BLEU)
    canvas.circle(M + 0.26 * cm, pill_y + pill_h / 2, 2.5, fill=1, stroke=0)
    canvas.setFillColor(_BLEU)
    canvas.setFont(F_REG, pill_fs)
    canvas.drawString(M + 0.46 * cm, pill_y + 0.08 * cm, pill_txt)

    y = pill_y - 0.70 * cm

    # ── 6. Carte patient ──────────────────────────────────────────────────────
    card_h   = 3.00 * cm
    card_w   = W - 2 * M
    hdr_h    = 0.54 * cm
    mid_x    = M + card_w / 2
    card_top = y

    _rrect(canvas, M, card_top - card_h, card_w, card_h, 6,
           fill=_WHITE, stroke=_GRIS_BORD, lw=0.4)

    # En-tête légère
    _rrect(canvas, M, card_top - hdr_h, card_w, hdr_h, 6, fill=_CARD_BG)
    canvas.setFillColor(_WHITE)
    canvas.rect(M + 1, card_top - hdr_h, card_w - 2, hdr_h * 0.45, fill=1, stroke=0)
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(M, card_top - hdr_h, M + card_w, card_top - hdr_h)

    canvas.setFillColor(_BLEU)
    canvas.setFont(F_BOLD, 6.5)
    canvas.drawString(M + 0.40 * cm, card_top - 0.35 * cm, "PATIENT")

    # Séparateurs internes
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(mid_x, card_top - hdr_h, mid_x, card_top - card_h + 2)
    row_div = card_top - hdr_h - (card_h - hdr_h) / 2
    canvas.line(M + 1, row_div, M + card_w - 1, row_div)

    # Offsets label / valeur dans chaque demi-cellule
    LABEL_OFF = 0.60 * cm
    VALUE_OFF = 0.16 * cm

    def _cell(cx, cy, label, value, maxlen=30):
        v = str(value or "—")
        if len(v) > maxlen:
            v = v[:maxlen - 1] + "…"
        canvas.setFillColor(_GRIS_99)
        canvas.setFont(F_LIGHT, 7)
        canvas.drawString(cx, cy + LABEL_OFF, label)
        canvas.setFillColor(_NOIR)
        canvas.setFont(F_REG, 9.5)
        canvas.drawString(cx, cy + VALUE_OFF, v)

    # Âge
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

    row1_y = row_div + 0.24 * cm
    row2_y = card_top - card_h + 0.20 * cm

    _cell(M + 0.40 * cm,     row1_y, "Nom",               nom_full, maxlen=28)
    _cell(mid_x + 0.40 * cm, row1_y, "Date de naissance", age_str,  maxlen=32)
    _cell(M + 0.40 * cm,     row2_y, "Sexe",              patient_info.get("sexe", "—"))
    _cell(mid_x + 0.40 * cm, row2_y, "N° dossier",        pid)

    y = card_top - card_h - 0.70 * cm

    # ── 7. Timeline ───────────────────────────────────────────────────────────
    canvas.setFillColor(_GRIS_77)
    canvas.setFont(F_BOLD, 6.5)
    canvas.drawString(M, y, "BILANS INCLUS")

    tl_y   = y - 0.78 * cm
    n      = len(bilans_df)
    circ_r = 8.5

    if n > 0:
        slot_w = (W - 2 * M) / n
        if n > 1:
            canvas.setStrokeColor(_GRIS_BORD)
            canvas.setLineWidth(1.0)
            canvas.line(M + slot_w * 0.5, tl_y,
                        M + slot_w * (n - 0.5), tl_y)

        for i, (_, row) in enumerate(bilans_df.iterrows()):
            cx      = M + slot_w * (i + 0.5)
            is_last = (i == n - 1)
            dot_col = _TERRA if is_last else _BLEU

            canvas.setFillColor(dot_col)
            canvas.circle(cx, tl_y, circ_r, fill=1, stroke=0)
            canvas.setFillColor(_WHITE)
            canvas.setFont(F_BOLD, 7)
            canvas.drawCentredString(cx, tl_y - 2.5, str(i + 1))

            try:
                d  = row.get("date_bilan")
                ds = d.strftime("%d.%m.%Y") if pd.notna(d) else "—"
            except Exception:
                ds = "—"

            canvas.setFillColor(dot_col)
            canvas.setFont(F_REG, 8)
            canvas.drawCentredString(cx, tl_y - circ_r - 0.36 * cm, ds)

            praticien = str(row.get("praticien", "") or "")
            if praticien:
                canvas.setFillColor(_GRIS_99)
                canvas.setFont(F_LIGHT, 7)
                canvas.drawCentredString(cx, tl_y - circ_r - 0.62 * cm, praticien)

    tl_bottom = tl_y - circ_r - 1.0 * cm

    # ── 8. Synthèse IA — justifiée, remplit tout l'espace ────────────────────
    ai_text = str(analyse_text or "").strip()
    # Nettoyer le Markdown
    ai_text = _re.sub(r'^#+\s*', '', ai_text, flags=_re.MULTILINE)
    ai_text = _re.sub(r'\*\*(.*?)\*\*', r'\1', ai_text)
    ai_text = _re.sub(r'\*(.*?)\*', r'\1', ai_text)
    ai_text = ai_text.strip()

    footer_top = FOOTER_H + 0.5 * cm
    ai_top     = tl_bottom

    if ai_text and ai_top > footer_top + 1.5 * cm:
        avail_h = ai_top - footer_top

        # Barre latérale terracotta fine
        canvas.setFillColor(_TERRA)
        canvas.rect(M, footer_top, 2, avail_h, fill=1, stroke=0)

        # Label
        canvas.setFillColor(_TERRA)
        canvas.setFont(F_BOLD, 6.5)
        canvas.drawString(M + 0.38 * cm, ai_top - 0.38 * cm,
                          "SYNTHÈSE PHYSIOTHÉRAPEUTIQUE")

        lbl_h    = 0.52 * cm
        text_x   = M + 0.38 * cm
        text_w   = W - 2 * M - 0.48 * cm
        text_top = ai_top - lbl_h - 0.18 * cm
        text_h   = text_top - footer_top - 0.12 * cm

        # Convertir sauts de paragraphe en balises HTML
        html_text = ai_text.replace("\n\n", "<br/><br/>").replace("\n", " ")

        # Taille adaptative — de la plus grande à la plus petite
        chosen_p = None
        for font_size, leading in [
            (10.5, 16.0),
            (10.0, 15.0),
            (9.5,  14.5),
            (9.0,  13.5),
            (8.5,  13.0),
            (8.0,  12.0),
            (7.5,  11.5),
        ]:
            ai_style = ParagraphStyle(
                "ai_cvr",
                fontSize=font_size,
                fontName=F_REG,
                textColor=_GRIS_33,
                leading=leading,
                alignment=TA_JUSTIFY,       # ← texte justifié
                spaceAfter=leading * 0.35,
            )
            p = Paragraph(html_text, ai_style)
            p_w, p_h = p.wrap(text_w, 9999)
            if p_h <= text_h:
                chosen_p = p
                break

        if chosen_p is None:
            # Tout mettre à la taille minimum et clipper
            ai_style = ParagraphStyle(
                "ai_cvr_min",
                fontSize=7.5,
                fontName=F_REG,
                textColor=_GRIS_33,
                leading=11.5,
                alignment=TA_JUSTIFY,
            )
            chosen_p = Paragraph(html_text, ai_style)
            chosen_p.wrap(text_w, text_h)

        # Clipper proprement
        canvas.saveState()
        clip = canvas.beginPath()
        clip.rect(text_x, footer_top + 0.10 * cm,
                  text_w, text_top - footer_top)
        canvas.clipPath(clip, stroke=0, fill=0)
        chosen_p.drawOn(canvas, text_x, text_top - chosen_p.height)
        canvas.restoreState()

    # ── 9. Footer ─────────────────────────────────────────────────────────────
    foot_y = FOOTER_H - 0.10 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.4)
    canvas.line(M, foot_y, W - M, foot_y)

    praticien_nom = ""
    try:
        praticien_nom = str(bilans_df.iloc[-1].get("praticien", "") or "")
    except Exception:
        pass

    # Gauche
    canvas.setFillColor(_GRIS_99)
    canvas.setFont(F_LIGHT, 6.5)
    canvas.drawString(M, foot_y - 0.34 * cm, "Praticien responsable")
    canvas.setFillColor(_NOIR)
    canvas.setFont(F_REG, 10)
    canvas.drawString(M, foot_y - 0.70 * cm, praticien_nom or "—")
    canvas.setFillColor(_GRIS_55)
    canvas.setFont(F_REG, 7.5)
    canvas.drawString(M, foot_y - 0.98 * cm, "Physiothérapeute diplômé")

    # Droite
    canvas.setFillColor(_GRIS_99)
    canvas.setFont(F_LIGHT, 6.5)
    canvas.drawRightString(W - M, foot_y - 0.34 * cm, "Généré le")
    canvas.setFillColor(_NOIR)
    canvas.setFont(F_BOLD, 10)
    canvas.drawRightString(W - M, foot_y - 0.70 * cm,
                           _date.today().strftime("%d.%m.%Y"))
    canvas.setFillColor(_GRIS_BB)
    canvas.setFont(F_LIGHT, 6.5)
    canvas.drawRightString(W - M, foot_y - 0.98 * cm,
                           "Document confidentiel · Usage médical exclusif")

    # ── 10. Bande bleue bas ───────────────────────────────────────────────────
    canvas.setFillColor(_BLEU)
    canvas.rect(0, 0, W, 4.5, fill=1, stroke=0)

    canvas.restoreState()


def make_cover_callback(patient_info: dict, bilans_df: pd.DataFrame,
                        labels: list, analyse_text: str,
                        template_nom: str, medecin_info: dict):
    """Retourne la fonction onPage à passer au PageTemplate de couverture."""
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
