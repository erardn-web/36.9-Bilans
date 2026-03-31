"""
utils/pdf_cover.py — Page de garde canvas-based (v5)

Changements v5 :
- Fontes : Vera (bundlées avec ReportLab, TOUJOURS disponibles) +
           Liberation/Carlito en supplément si présentes sur le système.
- Espacement : zone plus aérée entre le header et "RAPPORT D'ÉVOLUTION".
- Texte IA retiré du canvas → géré comme Flowable dans le story (pdf.py),
  ce qui permet un vrai débordement sur page 2 sans recouper le texte.
- Le canvas dessine uniquement la bordure terracotta + label IA (décoration).
- Export : get_ia_frame(), F_REG, F_BOLD pour que pdf.py puisse construire
  le Paragraph IA avec la même fonte.
"""

import os
import re as _re
import pandas as pd
from datetime import date as _date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
import reportlab as _rl

# ── Palette ───────────────────────────────────────────────────────────────────
_BLEU      = colors.HexColor("#2B57A7")
_TERRA     = colors.HexColor("#C4603A")
_NOIR      = colors.HexColor("#1A1A1A")
_GRIS_55   = colors.HexColor("#555555")
_GRIS_77   = colors.HexColor("#777777")
_GRIS_99   = colors.HexColor("#999999")
_GRIS_BB   = colors.HexColor("#BBBBBB")
_GRIS_BORD = colors.HexColor("#E0E0E0")
_BLEU_BG   = colors.HexColor("#EBF0FA")
_CARD_BG   = colors.HexColor("#F7F8FC")
_WHITE     = colors.white

M        = 1.5 * cm
FOOTER_H = 3.0 * cm


# ── Fontes ─────────────────────────────────────────────────────────────────────
# Vera est bundlée avec ReportLab → toujours disponible.
# On essaie d'abord Liberation (plus fine) puis Carlito, puis Vera comme garantie.

_RL_FONTS = os.path.dirname(_rl.__file__) + "/fonts/"

def _reg(name, paths, fallback="Helvetica"):
    for p in paths:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(name, p))
                return name
            except Exception:
                continue
    return fallback

F_LIGHT = _reg("CV-Lt", [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    _RL_FONTS + "Vera.ttf",
])

F_REG = _reg("CV-Rg", [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
    _RL_FONTS + "Vera.ttf",
])

F_BOLD = _reg("CV-Bd", [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
    _RL_FONTS + "VeraBd.ttf",
], fallback="Helvetica-Bold")


# ── Coordonnées de la zone IA (exportées pour pdf.py) ─────────────────────────
_W, _H = A4

# Reproduire le layout de draw_cover_canvas pour calculer tl_bottom
_logo_y   = _H - 2.15 * cm
_sep_y    = _logo_y - 0.46 * cm
_y        = _sep_y - 1.8 * cm          # gap aéré vers le hero
_y       -= 0.88 * cm                  # label RAPPORT
_y       -= 0.75 * cm                  # titre pathologie
_pill_y   = _y - 0.10 * cm
_y        = _pill_y - 1.00 * cm        # card_top
_card_top = _y
_y        = _card_top - 3.00 * cm - 0.70 * cm  # timeline label
_tl_y     = _y - 0.78 * cm
_tl_bot   = _tl_y - 8.5 - 1.0 * cm   # 8.5 pt = circ_r

_IA_X      = M + 0.38 * cm
_IA_BOTTOM = FOOTER_H + 0.5 * cm
_IA_W      = _W - 2 * M - 0.48 * cm
_IA_TOP    = _tl_bot


def get_ia_frame():
    """Retourne (x, y, w, h) du Frame à utiliser pour le texte IA dans le story."""
    return (_IA_X, _IA_BOTTOM, _IA_W, _IA_TOP - _IA_BOTTOM)


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


# ── Canvas cover ──────────────────────────────────────────────────────────────

def draw_cover_canvas(canvas, doc,
                      patient_info: dict,
                      bilans_df: pd.DataFrame,
                      labels: list,
                      template_nom: str,
                      medecin_info: dict):
    """
    Dessine la page de garde (tout SAUF le texte IA).
    Le texte IA est rendu comme Flowable dans le story de pdf.py,
    ce qui permet un débordement propre sur la page suivante.

    Sur page > 1 (débordement IA), dessine un en-tête minimal.
    """
    canvas.saveState()
    W, H = A4

    # ── Page 2+ : continuation IA ─────────────────────────────────────────────
    if doc.page > 1:
        # Barre bleue haut
        canvas.setFillColor(_BLEU)
        canvas.rect(0, H - 4.5, W, 4.5, fill=1, stroke=0)
        canvas.setFillColor(_TERRA)
        canvas.rect(0, H - 7, W * 0.26, 2.5, fill=1, stroke=0)

        # Logo et titre compact
        logo_path = _find_logo()
        name_x = M
        if logo_path:
            try:
                canvas.drawImage(logo_path, M, H - 1.9 * cm,
                                 width=1.8 * cm, height=0.65 * cm,
                                 preserveAspectRatio=True, mask="auto")
                name_x = M + 2.0 * cm
            except Exception:
                pass
        canvas.setFillColor(_GRIS_77)
        canvas.setFont(F_REG, 9)
        canvas.drawString(name_x, H - 1.55 * cm, "36.9 Bilans — Synthèse (suite)")

        # Barre latérale terracotta (continuité visuelle)
        ia_x, ia_bottom, ia_w, ia_h = get_ia_frame()
        canvas.setFillColor(_TERRA)
        canvas.rect(M, ia_bottom, 2, H - 2.5 * cm - ia_bottom, fill=1, stroke=0)

        # Footer
        canvas.setStrokeColor(_GRIS_BORD)
        canvas.setLineWidth(0.4)
        canvas.line(M, FOOTER_H - 0.10 * cm, W - M, FOOTER_H - 0.10 * cm)
        canvas.setFillColor(_GRIS_99)
        canvas.setFont(F_LIGHT, 6.5)
        canvas.drawRightString(W - M, FOOTER_H - 0.44 * cm,
                               "Document confidentiel · Usage médical exclusif")
        canvas.setFillColor(_BLEU)
        canvas.rect(0, 0, W, 4.5, fill=1, stroke=0)

        canvas.restoreState()
        return

    # ── Page 1 : page de garde complète ──────────────────────────────────────

    # 1. Accents couleur haut
    canvas.setFillColor(_BLEU)
    canvas.rect(0, H - 4.5, W, 4.5, fill=1, stroke=0)
    canvas.setFillColor(_TERRA)
    canvas.rect(0, H - 7, W * 0.26, 2.5, fill=1, stroke=0)

    # 2. Logo + cabinet
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

    # 3. Destinataire
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

    # 4. Séparateur
    sep_y = logo_y - 0.46 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.4)
    canvas.line(M, sep_y, W - M, sep_y)

    # 5. Hero — ZONE AÉRÉE ↓
    y = sep_y - 1.8 * cm      # ← espace généreux

    canvas.setFillColor(_TERRA)
    canvas.setFont(F_BOLD, 7)
    canvas.drawString(M, y, "RAPPORT D'ÉVOLUTION")
    y -= 0.88 * cm

    canvas.setFillColor(_NOIR)
    canvas.setFont(F_REG, 26)   # Regular, pas Bold
    canvas.drawString(M, y, str(template_nom or "Bilan"))
    y -= 0.75 * cm

    # Pill
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

    y = pill_y - 1.00 * cm

    # 6. Carte patient
    card_h   = 3.80 * cm
    card_w   = W - 2 * M
    hdr_h    = 0.54 * cm
    mid_x    = M + card_w / 2
    card_top = y

    _rrect(canvas, M, card_top - card_h, card_w, card_h, 6,
           fill=_WHITE, stroke=_GRIS_BORD, lw=0.4)
    _rrect(canvas, M, card_top - hdr_h, card_w, hdr_h, 6, fill=_CARD_BG)
    canvas.setFillColor(_WHITE)
    canvas.rect(M + 1, card_top - hdr_h, card_w - 2, hdr_h * 0.45, fill=1, stroke=0)
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(M, card_top - hdr_h, M + card_w, card_top - hdr_h)

    canvas.setFillColor(_BLEU)
    canvas.setFont(F_BOLD, 6.5)
    canvas.drawString(M + 0.40 * cm, card_top - 0.35 * cm, "PATIENT")

    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.3)
    canvas.line(mid_x, card_top - hdr_h, mid_x, card_top - card_h + 2)
    row_div = card_top - hdr_h - (card_h - hdr_h) / 2
    canvas.line(M + 1, row_div, M + card_w - 1, row_div)

    LABEL_OFF = 0.82 * cm
    VALUE_OFF = 0.28 * cm

    def _cell(cx, cy, label, value, maxlen=30):
        v = str(value or "—")
        if len(v) > maxlen:
            v = v[:maxlen - 1] + "…"
        canvas.setFillColor(_GRIS_99)
        canvas.setFont(F_LIGHT, 7)
        canvas.drawString(cx, cy + LABEL_OFF, label)
        canvas.setFillColor(_NOIR)
        canvas.setFont(F_REG, 9.5)     # Regular, pas Bold
        canvas.drawString(cx, cy + VALUE_OFF, v)

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

    row1_y = row_div + 0.30 * cm
    row2_y = card_top - card_h + 0.28 * cm

    _cell(M + 0.40 * cm,     row1_y, "Nom",               nom_full, maxlen=28)
    _cell(mid_x + 0.40 * cm, row1_y, "Date de naissance", age_str,  maxlen=32)
    _cell(M + 0.40 * cm,     row2_y, "Sexe",              patient_info.get("sexe", "—"))
    _cell(mid_x + 0.40 * cm, row2_y, "N° dossier",        pid)

    y = card_top - card_h - 0.70 * cm

    # 7. Timeline
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

    # 8. Zone IA — barre décorative + label uniquement (le texte est dans le story)
    ia_x, ia_bottom, ia_w, ia_h = get_ia_frame()

    canvas.setFillColor(_TERRA)
    canvas.rect(M, ia_bottom, 2, ia_h, fill=1, stroke=0)

    canvas.setFillColor(_TERRA)
    canvas.setFont(F_BOLD, 6.5)
    canvas.drawString(ia_x, _IA_TOP - 0.38 * cm, "SYNTHÈSE PHYSIOTHÉRAPEUTIQUE")

    # 9. Footer
    foot_y = FOOTER_H - 0.10 * cm
    canvas.setStrokeColor(_GRIS_BORD)
    canvas.setLineWidth(0.4)
    canvas.line(M, foot_y, W - M, foot_y)

    praticien_nom = ""
    try:
        praticien_nom = str(bilans_df.iloc[-1].get("praticien", "") or "")
    except Exception:
        pass

    canvas.setFillColor(_GRIS_99)
    canvas.setFont(F_LIGHT, 6.5)
    canvas.drawString(M, foot_y - 0.34 * cm, "Praticien responsable")
    canvas.setFillColor(_NOIR)
    canvas.setFont(F_REG, 10)
    canvas.drawString(M, foot_y - 0.70 * cm, praticien_nom or "—")
    canvas.setFillColor(_GRIS_55)
    canvas.setFont(F_REG, 7.5)
    canvas.drawString(M, foot_y - 0.98 * cm, "Physiothérapeute diplômé")

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

    # 10. Bande bleue bas
    canvas.setFillColor(_BLEU)
    canvas.rect(0, 0, W, 4.5, fill=1, stroke=0)

    canvas.restoreState()


def make_cover_callback(patient_info: dict, bilans_df: pd.DataFrame,
                        labels: list, analyse_text: str,
                        template_nom: str, medecin_info: dict):
    """
    Retourne la fonction onPage pour le PageTemplate de couverture.
    Note : analyse_text n'est PLUS utilisé ici — il est géré dans le story (pdf.py).
    """
    def _draw(canvas, doc):
        draw_cover_canvas(
            canvas, doc,
            patient_info = patient_info,
            bilans_df    = bilans_df,
            labels       = labels,
            template_nom = template_nom,
            medecin_info = medecin_info,
        )
    return _draw
