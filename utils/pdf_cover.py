"""
utils/pdf_cover.py — Page de garde canvas-based (v6)

IMPORTANT : aucun calcul, aucune importation lourde au niveau module.
Tout est lazy (à l'intérieur des fonctions) pour ne pas bloquer Streamlit
au démarrage.
"""

# Seuls des imports stdlib légers ici — jamais reportlab au top-level
import os
import re as _re


# ── Constantes de layout (calculées une seule fois à la demande) ──────────────

_LAYOUT = None   # cache lazy

def _get_layout():
    """Calcule et met en cache toutes les constantes de layout."""
    global _LAYOUT
    if _LAYOUT is not None:
        return _LAYOUT

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm

    M        = 1.5 * cm
    FOOTER_H = 3.0 * cm
    W, H     = A4

    logo_y   = H - 2.15 * cm
    sep_y    = logo_y - 0.46 * cm
    y        = sep_y - 1.8 * cm
    y       -= 0.88 * cm
    y       -= 0.75 * cm
    pill_y   = y - 0.10 * cm
    y        = pill_y - 1.00 * cm
    card_top = y
    y        = card_top - 3.80 * cm - 0.70 * cm
    tl_y     = y - 0.78 * cm
    tl_bot   = tl_y - 8.5 - 1.9 * cm

    ia_x      = M + 0.38 * cm
    ia_bottom = FOOTER_H + 0.5 * cm
    ia_w      = W - 2 * M - 0.48 * cm
    ia_top    = tl_bot

    _LAYOUT = dict(
        M=M, FOOTER_H=FOOTER_H, W=W, H=H,
        ia_x=ia_x, ia_bottom=ia_bottom, ia_w=ia_w, ia_top=ia_top,
    )
    return _LAYOUT


# ── Fontes (enregistrées une seule fois à la demande) ─────────────────────────

_FONTS = None   # cache lazy

def _get_fonts():
    """Enregistre et retourne les noms de fontes."""
    global _FONTS
    if _FONTS is not None:
        return _FONTS

    import reportlab as _rl
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    rl_fonts = os.path.join(os.path.dirname(_rl.__file__), "fonts")

    def _reg(name, paths, fallback="Helvetica"):
        for p in paths:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(name, p))
                    return name
                except Exception:
                    continue
        return fallback

    f_light = _reg("CV-Lt", [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        os.path.join(rl_fonts, "Vera.ttf"),
    ])
    f_reg = _reg("CV-Rg", [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
        os.path.join(rl_fonts, "Vera.ttf"),
    ])
    f_bold = _reg("CV-Bd", [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
        os.path.join(rl_fonts, "VeraBd.ttf"),
    ], fallback="Helvetica-Bold")

    _FONTS = dict(light=f_light, reg=f_reg, bold=f_bold)
    return _FONTS


# ── API publique ──────────────────────────────────────────────────────────────

def get_ia_frame():
    """Retourne (x, y, w, h) du Frame IA pour le story de pdf.py."""
    L = _get_layout()
    h = L["ia_top"] - L["ia_bottom"]
    return (L["ia_x"], L["ia_bottom"], L["ia_w"], h)


# Propriétés exposées pour pdf.py (lazy)
@property
def _F_REG_prop():
    return _get_fonts()["reg"]

# pdf.py importe F_REG comme attribut — on l'expose via une fonction
def get_f_reg():
    return _get_fonts()["reg"]

# Compatibilité : pdf.py fait `F_REG as _COVER_F_REG`
# On définit F_REG comme une constante qui sera résolue à l'import si besoin
# Mais pour éviter tout calcul module-level, on la définit comme chaîne
# et on laisse _get_fonts() la corriger à la première utilisation.
# Solution : pdf.py appellera get_f_reg() au lieu d'importer F_REG.
F_REG = "Helvetica"   # sera écrasé si on appelle _get_fonts() — mais pdf.py doit appeler get_f_reg()


# ── Dessin ────────────────────────────────────────────────────────────────────

def draw_cover_canvas(canvas, doc,
                      patient_info, bilans_df,
                      labels, template_nom, medecin_info):

    import pandas as pd
    from datetime import date as _date
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase.pdfmetrics import stringWidth

    L   = _get_layout()
    fnt = _get_fonts()

    M        = L["M"]
    FOOTER_H = L["FOOTER_H"]
    W, H     = A4

    FL = fnt["light"]
    FR = fnt["reg"]
    FB = fnt["bold"]

    # Palette
    BLEU      = colors.HexColor("#2B57A7")
    TERRA     = colors.HexColor("#C4603A")
    NOIR      = colors.HexColor("#1A1A1A")
    GRIS_55   = colors.HexColor("#555555")
    GRIS_77   = colors.HexColor("#777777")
    GRIS_99   = colors.HexColor("#999999")
    GRIS_BB   = colors.HexColor("#BBBBBB")
    GRIS_BORD = colors.HexColor("#E0E0E0")
    BLEU_BG   = colors.HexColor("#EBF0FA")
    CARD_BG   = colors.HexColor("#F7F8FC")
    WHITE     = colors.white

    from reportlab.lib.units import cm

    def _rrect(x, y, w, h, r, fill=None, stroke=None, lw=0.4):
        canvas.saveState()
        if fill:   canvas.setFillColor(fill)
        if stroke: canvas.setStrokeColor(stroke); canvas.setLineWidth(lw)
        canvas.roundRect(x, y, w, h, r,
                         fill=1 if fill else 0,
                         stroke=1 if stroke else 0)
        canvas.restoreState()

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

    canvas.saveState()

    # ── Page 2+ : continuation ────────────────────────────────────────────────
    if doc.page > 1:
        canvas.setFillColor(BLEU)
        canvas.rect(0, H - 4.5, W, 4.5, fill=1, stroke=0)
        canvas.setFillColor(TERRA)
        canvas.rect(0, H - 7, W * 0.26, 2.5, fill=1, stroke=0)

        logo_path = _find_logo()
        nx = M
        if logo_path:
            try:
                canvas.drawImage(logo_path, M, H - 1.9 * cm,
                                 width=1.8 * cm, height=0.65 * cm,
                                 preserveAspectRatio=True, mask="auto")
                nx = M + 2.0 * cm
            except Exception:
                pass
        canvas.setFillColor(GRIS_77)
        canvas.setFont(FR, 9)
        canvas.drawString(nx, H - 1.55 * cm, "36.9 Bilans — Synthèse (suite)")

        # Barre terracotta bornée à la zone header uniquement
        # Elle accompagne visuellement la synthèse sans déborder sur les tableaux
        _footer_top = FOOTER_H - 0.10 * cm
        _bar_top    = H - 2.5 * cm   # bas du header
        canvas.setFillColor(TERRA)
        canvas.rect(M, _footer_top, 2, _bar_top - _footer_top, fill=1, stroke=0)

        foot_y = FOOTER_H - 0.10 * cm
        canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(0.4)
        canvas.line(M, foot_y, W - M, foot_y)
        canvas.setFillColor(GRIS_99); canvas.setFont(FL, 6.5)
        canvas.drawRightString(W - M, foot_y - 0.44 * cm,
                               "Document confidentiel · Usage médical exclusif")
        canvas.setFillColor(BLEU)
        canvas.rect(0, 0, W, 4.5, fill=1, stroke=0)
        canvas.restoreState()
        return

    # ── Page 1 ────────────────────────────────────────────────────────────────

    # 1. Accents
    canvas.setFillColor(BLEU)
    canvas.rect(0, H - 4.5, W, 4.5, fill=1, stroke=0)
    canvas.setFillColor(TERRA)
    canvas.rect(0, H - 7, W * 0.26, 2.5, fill=1, stroke=0)

    # 2. Logo
    logo_h = 0.85 * cm
    logo_y = H - 2.15 * cm
    name_x = M

    logo_path = _find_logo()
    if logo_path:
        try:
            canvas.drawImage(logo_path, M, logo_y,
                             width=2.5 * cm, height=logo_h,
                             preserveAspectRatio=True, mask="auto")
            name_x = M + 2.7 * cm
        except Exception:
            logo_path = None

    if not logo_path:
        _rrect(M, logo_y, logo_h, logo_h, 4, fill=BLEU)
        canvas.setFillColor(WHITE); canvas.setFont(FB, 7)
        canvas.drawCentredString(M + logo_h / 2, logo_y + 0.28 * cm, "36.9")
        name_x = M + logo_h + 0.35 * cm

    canvas.setFillColor(BLEU);  canvas.setFont(FR, 11.5)
    canvas.drawString(name_x, logo_y + 0.52 * cm, "36.9 Bilans")
    canvas.setFillColor(GRIS_99); canvas.setFont(FL, 8)
    canvas.drawString(name_x, logo_y + 0.16 * cm, "Physiothérapie")

    # 3. Destinataire
    nom_med  = (medecin_info or {}).get("nom", "").strip()
    spec_med = (medecin_info or {}).get("specialite", "").strip()
    adr_med  = (medecin_info or {}).get("adresse", "").strip()
    if nom_med or spec_med:
        dx = W - M; dy = H - 1.48 * cm
        canvas.setFillColor(TERRA); canvas.setFont(FB, 6)
        canvas.drawRightString(dx, dy, "À L'ATTENTION DE"); dy -= 0.40 * cm
        if nom_med:
            canvas.setFillColor(NOIR); canvas.setFont(FB, 10)
            canvas.drawRightString(dx, dy, f"Dr. {nom_med}"); dy -= 0.36 * cm
        if spec_med:
            canvas.setFillColor(GRIS_55); canvas.setFont(FR, 8)
            canvas.drawRightString(dx, dy, spec_med); dy -= 0.28 * cm
        if adr_med:
            canvas.setFillColor(GRIS_99); canvas.setFont(FL, 7.5)
            canvas.drawRightString(dx, dy, adr_med)

    # 4. Séparateur
    sep_y = logo_y - 0.46 * cm
    canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(0.4)
    canvas.line(M, sep_y, W - M, sep_y)

    # 5. Hero
    y = sep_y - 1.8 * cm
    canvas.setFillColor(TERRA); canvas.setFont(FB, 7)
    canvas.drawString(M, y, "RAPPORT D'ÉVOLUTION")
    y -= 0.88 * cm

    canvas.setFillColor(NOIR); canvas.setFont(FR, 26)
    canvas.drawString(M, y, str(template_nom or "Bilan"))
    y -= 0.75 * cm

    n_bilans = len(bilans_df)
    try:
        dates_ok = bilans_df["date_bilan"].dropna()
        y1 = dates_ok.iloc[0].strftime("%Y") if len(dates_ok) >= 1 else ""
        y2 = dates_ok.iloc[-1].strftime("%Y") if len(dates_ok) >= 2 else ""
        date_rng = f"{y1}–{y2}" if y1 and y2 and y1 != y2 else (y1 or "")
    except Exception:
        date_rng = ""

    plural   = "s" if n_bilans > 1 else ""
    pill_txt = f"{n_bilans} bilan{plural}{'  ·  ' + date_rng if date_rng else ''}"
    pill_fs  = 8
    txt_w    = stringWidth(pill_txt, FR, pill_fs)
    pill_w   = txt_w + 1.1 * cm
    pill_h   = 0.46 * cm
    pill_y   = y - 0.10 * cm

    _rrect(M, pill_y, pill_w, pill_h, 10, fill=BLEU_BG)
    canvas.setFillColor(BLEU)
    canvas.circle(M + 0.26 * cm, pill_y + pill_h / 2, 2.5, fill=1, stroke=0)
    canvas.setFont(FR, pill_fs)
    canvas.drawString(M + 0.46 * cm, pill_y + 0.08 * cm, pill_txt)

    y = pill_y - 1.00 * cm

    # 6. Carte patient
    card_h   = 3.80 * cm
    card_w   = W - 2 * M
    hdr_h    = 0.54 * cm
    mid_x    = M + card_w / 2
    card_top = y

    _rrect(M, card_top - card_h, card_w, card_h, 6, fill=WHITE, stroke=GRIS_BORD, lw=0.4)
    _rrect(M, card_top - hdr_h, card_w, hdr_h, 6, fill=CARD_BG)
    canvas.setFillColor(WHITE)
    canvas.rect(M + 1, card_top - hdr_h, card_w - 2, hdr_h * 0.45, fill=1, stroke=0)
    canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(0.3)
    canvas.line(M, card_top - hdr_h, M + card_w, card_top - hdr_h)
    canvas.setFillColor(BLEU); canvas.setFont(FB, 6.5)
    canvas.drawString(M + 0.40 * cm, card_top - 0.35 * cm, "PATIENT")

    canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(0.3)
    canvas.line(mid_x, card_top - hdr_h, mid_x, card_top - card_h + 2)
    row_div = card_top - hdr_h - (card_h - hdr_h) / 2
    canvas.line(M + 1, row_div, M + card_w - 1, row_div)

    LABEL_OFF = 0.82 * cm
    VALUE_OFF = 0.28 * cm

    def _cell(cx, cy, label, value, maxlen=30):
        v = str(value or "—")[:maxlen]
        canvas.setFillColor(GRIS_99); canvas.setFont(FL, 7)
        canvas.drawString(cx, cy + LABEL_OFF, label)
        canvas.setFillColor(NOIR); canvas.setFont(FR, 9.5)
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

    nom_full = f"{(patient_info.get('nom') or '').upper()} {(patient_info.get('prenom') or '')}".strip()
    pid = str(patient_info.get("patient_id", "—"))

    row1_y = row_div + 0.30 * cm
    row2_y = card_top - card_h + 0.28 * cm

    _cell(M + 0.40 * cm,     row1_y, "Nom",               nom_full, maxlen=28)
    _cell(mid_x + 0.40 * cm, row1_y, "Date de naissance", age_str,  maxlen=32)
    _cell(M + 0.40 * cm,     row2_y, "Sexe",              patient_info.get("sexe", "—"))
    _cell(mid_x + 0.40 * cm, row2_y, "N° dossier",        pid)

    y = card_top - card_h - 0.70 * cm

    # 7. Timeline
    canvas.setFillColor(GRIS_77); canvas.setFont(FB, 6.5)
    canvas.drawString(M, y, "BILANS INCLUS")

    tl_y   = y - 0.78 * cm
    n      = len(bilans_df)
    circ_r = 8.5

    if n > 0:
        slot_w = (W - 2 * M) / n
        if n > 1:
            canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(1.0)
            canvas.line(M + slot_w * 0.5, tl_y, M + slot_w * (n - 0.5), tl_y)

        for i, (_, row) in enumerate(bilans_df.iterrows()):
            cx      = M + slot_w * (i + 0.5)
            dot_col = TERRA if i == n - 1 else BLEU
            canvas.setFillColor(dot_col)
            canvas.circle(cx, tl_y, circ_r, fill=1, stroke=0)
            canvas.setFillColor(WHITE); canvas.setFont(FB, 7)
            canvas.drawCentredString(cx, tl_y - 2.5, str(i + 1))
            try:
                d  = row.get("date_bilan")
                ds = d.strftime("%d.%m.%Y") if pd.notna(d) else "—"
            except Exception:
                ds = "—"
            canvas.setFillColor(dot_col); canvas.setFont(FR, 8)
            canvas.drawCentredString(cx, tl_y - circ_r - 0.36 * cm, ds)
            praticien = str(row.get("praticien", "") or "")
            if praticien:
                canvas.setFillColor(GRIS_99); canvas.setFont(FL, 7)
                canvas.drawCentredString(cx, tl_y - circ_r - 0.62 * cm, praticien)

    # 8. Déco zone IA (barre + label — le texte est dans le story)
    ia_x, ia_bottom, ia_w, ia_h = get_ia_frame()
    canvas.setFillColor(TERRA)
    canvas.rect(M, ia_bottom, 2, ia_h, fill=1, stroke=0)
    canvas.setFont(FB, 6.5)
    canvas.drawString(ia_x, L["ia_top"] - 0.38 * cm, "SYNTHÈSE PHYSIOTHÉRAPEUTIQUE")

    # 9. Footer
    foot_y = FOOTER_H - 0.10 * cm
    canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(0.4)
    canvas.line(M, foot_y, W - M, foot_y)

    praticien_nom = ""
    try:
        praticien_nom = str(bilans_df.iloc[-1].get("praticien", "") or "")
    except Exception:
        pass

    canvas.setFillColor(GRIS_99); canvas.setFont(FL, 6.5)
    canvas.drawString(M, foot_y - 0.34 * cm, "Praticien responsable")
    canvas.setFillColor(NOIR); canvas.setFont(FR, 10)
    canvas.drawString(M, foot_y - 0.70 * cm, praticien_nom or "—")
    canvas.setFillColor(GRIS_55); canvas.setFont(FR, 7.5)
    canvas.drawString(M, foot_y - 0.98 * cm, "Physiothérapeute diplômé")

    canvas.setFillColor(GRIS_99); canvas.setFont(FL, 6.5)
    canvas.drawRightString(W - M, foot_y - 0.34 * cm, "Généré le")
    canvas.setFillColor(NOIR); canvas.setFont(FB, 10)
    canvas.drawRightString(W - M, foot_y - 0.70 * cm, _date.today().strftime("%d.%m.%Y"))
    canvas.setFillColor(GRIS_BB); canvas.setFont(FL, 6.5)
    canvas.drawRightString(W - M, foot_y - 0.98 * cm,
                           "Document confidentiel · Usage médical exclusif")

    # 10. Bande bleue bas
    canvas.setFillColor(BLEU)
    canvas.rect(0, 0, W, 4.5, fill=1, stroke=0)

    canvas.restoreState()


def make_cover_callback(patient_info, bilans_df, labels,
                        analyse_text, template_nom, medecin_info):
    """Retourne la fonction onPage pour le PageTemplate Cover."""
    def _draw(canvas, doc):
        draw_cover_canvas(canvas, doc,
                          patient_info=patient_info,
                          bilans_df=bilans_df,
                          labels=labels,
                          template_nom=template_nom,
                          medecin_info=medecin_info)
    return _draw
