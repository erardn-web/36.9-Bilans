"""
shv_pdf.py — PDF SHV
Fusion : pdf_export.py · questionnaires_print.py
"""

import os as _os
from reportlab.lib import colors as _colors
from reportlab.lib.pagesizes import A4 as _A4
from reportlab.lib.units import cm as _cm
from reportlab.lib.enums import TA_CENTER as _TA_CENTER
from reportlab.lib.styles import ParagraphStyle as _PS
from reportlab.platypus import Table as _Table, TableStyle as _TableStyle, Paragraph as _Para, Image as _Image
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Image,
)
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ─── Palette 36.9 Bilans ──────────────────────────────────────────────────────
TERRA       = _colors.HexColor("#C4603A")
TERRA_LIGHT = _colors.HexColor("#FAEEE9")
BLEU        = _colors.HexColor("#2B57A7")
BLEU_LIGHT  = _colors.HexColor("#E8EEF9")
GRIS        = _colors.HexColor("#F4F4F4")
GRIS_BORD   = _colors.HexColor("#DEDEDE")
GRIS_TEXTE  = _colors.HexColor("#555555")
NOIR        = _colors.HexColor("#1A1A1A")
BLANC       = _colors.white
VERT        = _colors.HexColor("#388e3c")
ORANGE      = _colors.HexColor("#f57c00")
ROUGE       = _colors.HexColor("#d32f2f")
JAUNE       = _colors.HexColor("#fbc02d")

# Aliases ancienne palette
BLEU_FONCE  = BLEU
BLEU_CLAIR  = BLEU_LIGHT
GRIS_CLAIR  = GRIS

USEFUL_W = _A4[0] - 3*_cm
MARGIN   = 1.5*_cm
HEADER_H = 1.6*_cm
W        = USEFUL_W

# ─── Case à cocher dessinée (pas unicode) ────────────────────────────────────
from reportlab.platypus import Flowable as _Flowable

class Checkbox(_Flowable):
    """Case à cocher vide dessinée proprement."""
    def __init__(self, size=8):
        _Flowable.__init__(self)
        self.size = size
        self.width = size + 4
        self.height = size
    def draw(self):
        self.canv.setStrokeColor(_colors.HexColor("#333333"))
        self.canv.setLineWidth(0.7)
        self.canv.rect(1, 0, self.size, self.size, fill=0, stroke=1)

def option_row(text, style, col_w=None):
    """Ligne avec case à cocher + texte."""
    if col_w is None: col_w = USEFUL_W
    cb   = Checkbox(size=8)
    para = Paragraph(f"  {text}", style)
    tbl  = _Table([[cb, para]], colWidths=[0.5*_cm, col_w - 0.5*_cm])
    tbl.setStyle(_TableStyle([
        ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",    (0,0),(-1,-1), 2),
        ("RIGHTPADDING",   (0,0),(-1,-1), 2),
        ("TOPPADDING",     (0,0),(-1,-1), 3),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 3),
    ]))
    return tbl


def _find_logo():
    candidates = [
        _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "assets", "logo_369.png"),
        _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets", "logo_369.png"),
        "assets/logo_369.png",
        "/mount/src/36.9-bilans/assets/logo_369.png",
    ]
    for c in candidates:
        if _os.path.exists(c):
            return c
    return None

def get_logo(width=3.2*_cm, height=1.1*_cm):
    p = _find_logo()
    if p:
        return _Image(p, width=width, height=height, kind="proportional")
    return None

def make_header_footer(report_title, patient_name=""):
    from datetime import date as _date
    def _draw(canvas, doc):
        canvas.saveState()
        w, h = _A4

        # Fond blanc header (transparent — pas de fond coloré)
        # Trait terracotta en haut de page
        canvas.setFillColor(TERRA)
        canvas.rect(0, h - 0.35*_cm, w, 0.35*_cm, fill=1, stroke=0)

        # Logo à gauche
        logo_p = _find_logo()
        if logo_p:
            try:
                canvas.drawImage(logo_p, MARGIN, h - 1.4*_cm,
                    width=2.6*_cm, height=1.0*_cm,
                    preserveAspectRatio=True, mask="auto")
            except Exception:
                pass

        # Titre rapport (centre, discret)
        canvas.setFillColor(GRIS_TEXTE)
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(w/2, h - 1.1*_cm, report_title)

        # Patient (droite, en bleu)
        if patient_name:
            canvas.setFillColor(BLEU)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawRightString(w - MARGIN, h - 1.1*_cm, patient_name)

        # Ligne séparatrice fine
        canvas.setStrokeColor(GRIS_BORD)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, h - 1.5*_cm, w - MARGIN, h - 1.5*_cm)

        # Pied de page
        canvas.setStrokeColor(GRIS_BORD)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, 0.9*_cm, w - MARGIN, 0.9*_cm)
        canvas.setFillColor(GRIS_TEXTE)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(MARGIN, 0.35*_cm, "Document confidentiel — Usage médical exclusif")
        canvas.drawCentredString(w/2, 0.35*_cm, "36.9 Bilans")
        canvas.drawRightString(w - MARGIN, 0.35*_cm,
            f"Page {doc.page}  ·  {_date.today().strftime('%d/%m/%Y')}")
        canvas.restoreState()
    return _draw

def make_styles():
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER
    base = getSampleStyleSheet()
    return {
        "title": _PS("title", fontSize=26, fontName="Helvetica-Bold", textColor=BLEU,
            spaceAfter=4, alignment=TA_CENTER),
        "subtitle": _PS("subtitle", fontSize=12, fontName="Helvetica", textColor=GRIS_TEXTE,
            spaceAfter=2, alignment=TA_CENTER),
        "section": _PS("section369", fontSize=11, fontName="Helvetica-Bold", textColor=BLANC,
            spaceBefore=12, spaceAfter=6, backColor=BLEU,
            leftIndent=-6, rightIndent=-6, borderPadding=(5,8,5,8)),
        "subsection": _PS("subsection369", fontSize=10, fontName="Helvetica-Bold",
            textColor=TERRA, spaceBefore=10, spaceAfter=4),
        "normal": _PS("normal369", fontSize=9, fontName="Helvetica",
            textColor=NOIR, spaceAfter=2),
        "small": _PS("small369", fontSize=7.5, fontName="Helvetica", textColor=GRIS_TEXTE),
        "bold": _PS("bold369", fontSize=9, fontName="Helvetica-Bold", textColor=BLEU),
        "note": _PS("note369", fontSize=8, fontName="Helvetica",
            textColor=GRIS_TEXTE, leftIndent=8, spaceAfter=4),
        "center": _PS("center369", fontSize=9, fontName="Helvetica", alignment=TA_CENTER),
        # Styles questionnaires imprimables
        "intro":    _PS("intro369", fontSize=9, fontName="Helvetica-Oblique",
            textColor=_colors.HexColor("#444"), spaceAfter=6, leftIndent=4),
        "question": _PS("question369", fontSize=10, fontName="Helvetica-Bold",
            textColor=NOIR, spaceBefore=8, spaceAfter=3, leftIndent=4),
        "option":   _PS("option369", fontSize=9, fontName="Helvetica",
            textColor=NOIR, spaceAfter=2, leftIndent=20),
    }

def section_band(title, accent=None):
    if accent is None: accent = BLEU
    row = [[_Para(
        f"<font color='#C4603A'>▌</font>&nbsp;&nbsp;<b>{title}</b>",
        _PS("sh369", fontSize=11, fontName="Helvetica-Bold", textColor=BLANC, leading=14)
    )]]
    tbl = _Table(row, colWidths=[USEFUL_W])
    tbl.setStyle(_TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), accent),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ]))
    return tbl

def make_table(data, col_widths=None, header=True, accent=None):
    if accent is None: accent = BLEU
    t = _Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
    ]
    if header:
        cmds += [
            ("BACKGROUND",   (0,0),(-1,0), accent),
            ("TEXTCOLOR",    (0,0),(-1,0), BLANC),
            ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0),(-1,0), 8),
            ("TOPPADDING",   (0,0),(-1,0), 7),
            ("BOTTOMPADDING",(0,0),(-1,0), 7),
        ]
    t.setStyle(_TableStyle(cmds))
    return t

def make_cover(story, title, subtitle, patient_info, bilans_df, labels, styles):
    import pandas as _pd
    from datetime import date as _date
    from reportlab.platypus import Spacer, PageBreak
    # Bandeau titre bleu
    band_data = [[_Para(f"<font color='white'><b>{title}</b></font>",
        _PS("ct369", fontSize=22, fontName="Helvetica-Bold",
            textColor=BLANC, alignment=_TA_CENTER))]]
    band = _Table(band_data, colWidths=[USEFUL_W])
    band.setStyle(_TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),20),("BOTTOMPADDING",(0,0),(-1,-1),20)]))
    story.append(Spacer(1, 0.8*_cm))
    story.append(band)
    # Sous-bande terracotta
    sub_data = [[_Para(f"<font color='white'>{subtitle}</font>",
        _PS("cs369", fontSize=11, fontName="Helvetica",
            textColor=BLANC, alignment=_TA_CENTER))]]
    sub = _Table(sub_data, colWidths=[USEFUL_W])
    sub.setStyle(_TableStyle([("BACKGROUND",(0,0),(-1,-1),TERRA),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story.append(sub)
    story.append(Spacer(1, 0.6*_cm))
    # Logo centré
    logo = get_logo(width=5*_cm, height=2*_cm)
    if logo:
        lt = _Table([[logo]], colWidths=[USEFUL_W])
        lt.setStyle(_TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
        story.append(lt)
        story.append(Spacer(1, 0.5*_cm))
    # Infos patient
    n = len(bilans_df)
    pat = [
        ["Patient",           f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"],
        ["Date de naissance", str(patient_info.get("date_naissance","—"))],
        ["Sexe",              patient_info.get("sexe","—")],
        ["Profession",        patient_info.get("profession","—") or "—"],
        ["Nombre de bilans",  str(n)],
        ["Généré le",         _date.today().strftime("%d/%m/%Y")],
    ]
    pt = _Table(pat, colWidths=[4.5*_cm, USEFUL_W-4.5*_cm])
    pt.setStyle(_TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(1,0),(1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("TEXTCOLOR",(0,0),(0,-1),BLEU),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[BLANC,BLEU_LIGHT]),
        ("LINEBELOW",(0,0),(-1,-1),0.3,GRIS_BORD),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.6*_cm))
    # Tableau bilans
    story.append(_Para("Bilans inclus dans ce rapport",
        _PS("subs369b", fontSize=10, fontName="Helvetica-Bold",
            textColor=TERRA, spaceBefore=8, spaceAfter=4)))
    bil = [["#","Date","Type","Praticien"]]
    for i,(_, row) in enumerate(bilans_df.iterrows()):
        d = row["date_bilan"]
        ds = d.strftime("%d/%m/%Y") if _pd.notna(d) else "—"
        bil.append([str(i+1), ds, row.get("type_bilan","—") or "—",
                    row.get("praticien","—") or "—"])
    story.append(make_table(bil, col_widths=[1.2*_cm,3.2*_cm,5*_cm,USEFUL_W-9.4*_cm]))


matplotlib.use("Agg")

BLEU = BLEU
BLEU_LIGHT = BLEU_LIGHT
GRIS = GRIS
CHART_COLORS_NEW = ["#2B57A7", "#C4603A", "#388e3c", "#7b1fa2", "#f57c00",
                    "#0097a7", "#e64a19", "#5d4037"]


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


def sf12_color(score):
    s = safe_num(score)
    if s is None: return GRIS_TEXTE
    if s >= 66:   return VERT
    if s >= 33:   return ORANGE
    return ROUGE


# ─── Utilitaires graphiques ───────────────────────────────────────────────────



def fig_to_rl_image(fig, width_cm=17, height_cm=8):
    """Convertit une figure matplotlib en Image ReportLab."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width_cm * cm, height=height_cm * cm)


def short_labels(labels):
    """Raccourcit les labels pour l'axe X."""
    result = []
    for lbl in labels:
        parts = lbl.split("—")
        result.append(parts[0].strip() if parts else lbl)
    return result


def make_chart_had(bilans_df, labels):
    """Courbe HAD anxiété & dépression."""
    xlbls   = short_labels(labels)
    x       = range(len(xlbls))
    scores_a = [safe_num(r.get("had_score_anxiete"))    for _, r in bilans_df.iterrows()]
    scores_d = [safe_num(r.get("had_score_depression")) for _, r in bilans_df.iterrows()]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.axhspan(0,  7,  alpha=0.08, color="green",  label="Normal (0–7)")
    ax.axhspan(8,  10, alpha=0.10, color="orange", label="Douteux (8–10)")
    ax.axhspan(11, 21, alpha=0.08, color="red",    label="Pathologique (11–21)")

    ax.plot(x, scores_a, "o-", color="#f57c00", linewidth=2.5,
            markersize=8, label="Anxiété", zorder=5)
    ax.plot(x, scores_d, "s-", color="#7b1fa2", linewidth=2.5,
            markersize=8, label="Dépression", zorder=5)

    for xi, (va, vd) in enumerate(zip(scores_a, scores_d)):
        if va is not None:
            ax.annotate(str(int(va)), (xi, va), textcoords="offset points",
                        xytext=(0, 10), ha="center", fontsize=9, color="#f57c00", fontweight="bold")
        if vd is not None:
            ax.annotate(str(int(vd)), (xi, vd), textcoords="offset points",
                        xytext=(0, -16), ha="center", fontsize=9, color="#7b1fa2", fontweight="bold")

    ax.set_xticks(list(x))
    ax.set_xticklabels(xlbls, rotation=15, ha="right", fontsize=9)
    ax.set_ylim(0, 23)
    ax.set_yticks([0, 7, 10, 21])
    ax.set_ylabel("Score /21")
    ax.set_title("Évolution HAD — Anxiété & Dépression", fontsize=12,
                 fontweight="bold", color="#1a3c5e", pad=10)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("white")
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=17, height_cm=7)


def make_chart_bolt(bilans_df, labels):
    """Barres BOLT."""
    xlbls     = short_labels(labels)
    bolt_vals = [safe_num(r.get("bolt_score")) for _, r in bilans_df.iterrows()]
    bar_cols  = []
    for v in bolt_vals:
        if v is None:    bar_cols.append("#cccccc")
        elif v < 10:     bar_cols.append("#d32f2f")
        elif v < 20:     bar_cols.append("#f57c00")
        elif v < 40:     bar_cols.append("#fbc02d")
        else:            bar_cols.append("#388e3c")

    fig, ax = plt.subplots(figsize=(10, 4))
    x = range(len(xlbls))
    bars = ax.bar(x, [v or 0 for v in bolt_vals], color=bar_cols,
                  width=0.5, zorder=3)
    for bar, v in zip(bars, bolt_vals):
        if v is not None:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.8,
                    f"{int(v)}s", ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color="#333333")

    ymax = max([v or 0 for v in bolt_vals] + [50]) + 15
    ax.axhline(20, color="#f57c00", linestyle="--", linewidth=1.5,
               label="Seuil 20s (altéré)", zorder=4)
    ax.axhline(40, color="#388e3c", linestyle="--", linewidth=1.5,
               label="Seuil 40s (bon)", zorder=4)
    ax.set_xticks(list(x))
    ax.set_xticklabels(xlbls, rotation=15, ha="right", fontsize=9)
    ax.set_ylim(0, ymax)
    ax.set_ylabel("Secondes")
    ax.set_title("Évolution BOLT", fontsize=12,
                 fontweight="bold", color="#1a3c5e", pad=10)
    ax.legend(fontsize=8, framealpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("white")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=17, height_cm=6.5)


def make_chart_sf12_bars(bilans_df, labels):
    """8 sous-graphiques SF-12."""
    dim_keys   = ["pf", "rp", "bp", "gh", "vt", "sf", "re", "mh"]
    dim_labels_short = ["Fonct.\nphysique", "Limit.\nphysique", "Douleur",
                        "Santé\ngénérale", "Vitalité", "Vie\nsociale",
                        "Limit.\némotionnel", "Santé\npsychique"]
    xlbls = short_labels(labels)
    x     = np.arange(len(xlbls))
    n     = len(bilans_df)
    width = 0.7 / max(n, 1)

    fig, axes = plt.subplots(2, 4, figsize=(14, 7), sharey=True)
    fig.suptitle("Évolution SF-12 par dimension", fontsize=13,
                 fontweight="bold", color="#1a3c5e", y=1.01)

    for i, (dk, dl) in enumerate(zip(dim_keys, dim_labels_short)):
        ax  = axes[i // 4][i % 4]
        for j, (_, row) in enumerate(bilans_df.iterrows()):
            val = safe_num(row.get(f"sf12_{dk}")) or 0
            c   = ("#388e3c" if val >= 66 else "#f57c00" if val >= 33 else "#d32f2f")
            offset = (j - (n - 1) / 2) * width
            bar = ax.bar(j, val, color=c, width=width * 0.85, zorder=3)
            ax.text(j, val + 2, str(int(val)) if val else "—",
                    ha="center", va="bottom", fontsize=7, fontweight="bold")

        ax.set_ylim(0, 115)
        ax.set_title(dl, fontsize=8, fontweight="bold", color="#1a3c5e")
        ax.set_xticks(range(n))
        ax.set_xticklabels([f"B{j+1}" for j in range(n)], fontsize=7)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_facecolor("white")
        ax.grid(axis="y", alpha=0.3, zorder=0)
        if i % 4 == 0:
            ax.set_ylabel("Score /100", fontsize=7)

    # Légende couleurs
    patches = [
        mpatches.Patch(color="#388e3c", label="≥ 66 (bon)"),
        mpatches.Patch(color="#f57c00", label="33–65 (moyen)"),
        mpatches.Patch(color="#d32f2f", label="< 33 (faible)"),
    ]
    fig.legend(handles=patches, loc="lower center", ncol=3,
               fontsize=8, framealpha=0.8, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=17, height_cm=10)


def make_chart_sf12_radar(bilans_df, labels):
    """Radar SF-12 comparatif."""
    dim_keys   = ["pf", "rp", "bp", "gh", "vt", "sf", "re", "mh"]
    dim_labels_r = ["Fonct.\nphysique", "Limit.\nphysique", "Douleur",
                    "Santé\ngénérale", "Vitalité", "Vie\nsociale",
                    "Limit.\némot.", "Santé\npsychique"]
    N      = len(dim_keys)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    for j, (_, row) in enumerate(bilans_df.iterrows()):
        vals = [safe_num(row.get(f"sf12_{dk}")) or 0 for dk in dim_keys]
        vals += vals[:1]
        color = CHART_COLORS[j % len(CHART_COLORS)]
        ax.plot(angles, vals, "o-", linewidth=2, color=color,
                label=short_labels(labels)[j])
        ax.fill(angles, vals, alpha=0.12, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dim_labels_r, size=8)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], size=7, color="grey")
    ax.set_title("Comparaison SF-12 — Radar", fontsize=12,
                 fontweight="bold", color="#1a3c5e", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
              fontsize=8, framealpha=0.8)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=14, height_cm=10)


def make_chart_hvt(bilans_df, labels):
    """Durée de retour HVT."""
    durees = [safe_num(r.get("hvt_duree_retour")) for _, r in bilans_df.iterrows()]
    if not any(d for d in durees):
        return None
    xlbls = short_labels(labels)
    fig, ax = plt.subplots(figsize=(10, 3.5))
    x    = range(len(xlbls))
    bars = ax.bar(x, [d or 0 for d in durees], color="#1a3c5e",
                  width=0.5, zorder=3)
    for bar, v in zip(bars, durees):
        if v:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.1,
                    f"{int(v)} min", ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color="#1a3c5e")
    ax.set_xticks(list(x))
    ax.set_xticklabels(xlbls, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("Minutes")
    ax.set_title("Test HV — Durée de retour à la normale", fontsize=12,
                 fontweight="bold", color="#1a3c5e", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("white")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=17, height_cm=5.5)


# make_styles() imported from pdf_theme


# make_header_footer() imported from pdf_theme


# make_table() imported from pdf_theme


# ─── Générateur principal ─────────────────────────────────────────────────────

# ─── Questionnaires helpers ──────────────────────────────────────────────────

# ─── Palette 36.9 Bilans ──────────────────────────────────────────────────────
TERRA       = _colors.HexColor("#C4603A")
TERRA_LIGHT = _colors.HexColor("#FAEEE9")
BLEU        = _colors.HexColor("#2B57A7")
BLEU_LIGHT  = _colors.HexColor("#E8EEF9")
GRIS        = _colors.HexColor("#F4F4F4")
GRIS_BORD   = _colors.HexColor("#DEDEDE")
GRIS_TEXTE  = _colors.HexColor("#555555")
NOIR        = _colors.HexColor("#1A1A1A")
BLANC       = _colors.white
VERT        = _colors.HexColor("#388e3c")
ORANGE      = _colors.HexColor("#f57c00")
ROUGE       = _colors.HexColor("#d32f2f")
JAUNE       = _colors.HexColor("#fbc02d")

# Aliases ancienne palette
BLEU_FONCE  = BLEU
BLEU_CLAIR  = BLEU_LIGHT
GRIS_CLAIR  = GRIS

USEFUL_W = _A4[0] - 3*_cm
MARGIN   = 1.5*_cm
HEADER_H = 1.6*_cm
W        = USEFUL_W

# ─── Case à cocher dessinée (pas unicode) ────────────────────────────────────
from reportlab.platypus import Flowable as _Flowable

class Checkbox(_Flowable):
    """Case à cocher vide dessinée proprement."""
    def __init__(self, size=8):
        _Flowable.__init__(self)
        self.size = size
        self.width = size + 4
        self.height = size
    def draw(self):
        self.canv.setStrokeColor(_colors.HexColor("#333333"))
        self.canv.setLineWidth(0.7)
        self.canv.rect(1, 0, self.size, self.size, fill=0, stroke=1)

def option_row(text, style, col_w=None):
    """Ligne avec case à cocher + texte."""
    if col_w is None: col_w = USEFUL_W
    cb   = Checkbox(size=8)
    para = Paragraph(f"  {text}", style)
    tbl  = _Table([[cb, para]], colWidths=[0.5*_cm, col_w - 0.5*_cm])
    tbl.setStyle(_TableStyle([
        ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",    (0,0),(-1,-1), 2),
        ("RIGHTPADDING",   (0,0),(-1,-1), 2),
        ("TOPPADDING",     (0,0),(-1,-1), 3),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 3),
    ]))
    return tbl


def _find_logo():
    candidates = [
        _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "assets", "logo_369.png"),
        _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets", "logo_369.png"),
        "assets/logo_369.png",
        "/mount/src/36.9-bilans/assets/logo_369.png",
    ]
    for c in candidates:
        if _os.path.exists(c):
            return c
    return None

def get_logo(width=3.2*_cm, height=1.1*_cm):
    p = _find_logo()
    if p:
        return _Image(p, width=width, height=height, kind="proportional")
    return None

def make_header_footer(report_title, patient_name=""):
    from datetime import date as _date
    def _draw(canvas, doc):
        canvas.saveState()
        w, h = _A4

        # Fond blanc header (transparent — pas de fond coloré)
        # Trait terracotta en haut de page
        canvas.setFillColor(TERRA)
        canvas.rect(0, h - 0.35*_cm, w, 0.35*_cm, fill=1, stroke=0)

        # Logo à gauche
        logo_p = _find_logo()
        if logo_p:
            try:
                canvas.drawImage(logo_p, MARGIN, h - 1.4*_cm,
                    width=2.6*_cm, height=1.0*_cm,
                    preserveAspectRatio=True, mask="auto")
            except Exception:
                pass

        # Titre rapport (centre, discret)
        canvas.setFillColor(GRIS_TEXTE)
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(w/2, h - 1.1*_cm, report_title)

        # Patient (droite, en bleu)
        if patient_name:
            canvas.setFillColor(BLEU)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawRightString(w - MARGIN, h - 1.1*_cm, patient_name)

        # Ligne séparatrice fine
        canvas.setStrokeColor(GRIS_BORD)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, h - 1.5*_cm, w - MARGIN, h - 1.5*_cm)

        # Pied de page
        canvas.setStrokeColor(GRIS_BORD)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, 0.9*_cm, w - MARGIN, 0.9*_cm)
        canvas.setFillColor(GRIS_TEXTE)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(MARGIN, 0.35*_cm, "Document confidentiel — Usage médical exclusif")
        canvas.drawCentredString(w/2, 0.35*_cm, "36.9 Bilans")
        canvas.drawRightString(w - MARGIN, 0.35*_cm,
            f"Page {doc.page}  ·  {_date.today().strftime('%d/%m/%Y')}")
        canvas.restoreState()
    return _draw

def section_band(title, accent=None):
    if accent is None: accent = BLEU
    row = [[_Para(
        f"<font color='#C4603A'>▌</font>&nbsp;&nbsp;<b>{title}</b>",
        _PS("sh369", fontSize=11, fontName="Helvetica-Bold", textColor=BLANC, leading=14)
    )]]
    tbl = _Table(row, colWidths=[USEFUL_W])
    tbl.setStyle(_TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), accent),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ]))
    return tbl

def make_table(data, col_widths=None, header=True, accent=None):
    if accent is None: accent = BLEU
    t = _Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
    ]
    if header:
        cmds += [
            ("BACKGROUND",   (0,0),(-1,0), accent),
            ("TEXTCOLOR",    (0,0),(-1,0), BLANC),
            ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0),(-1,0), 8),
            ("TOPPADDING",   (0,0),(-1,0), 7),
            ("BOTTOMPADDING",(0,0),(-1,0), 7),
        ]
    t.setStyle(_TableStyle(cmds))
    return t

def make_cover(story, title, subtitle, patient_info, bilans_df, labels, styles):
    import pandas as _pd
    from datetime import date as _date
    from reportlab.platypus import Spacer, PageBreak
    # Bandeau titre bleu
    band_data = [[_Para(f"<font color='white'><b>{title}</b></font>",
        _PS("ct369", fontSize=22, fontName="Helvetica-Bold",
            textColor=BLANC, alignment=_TA_CENTER))]]
    band = _Table(band_data, colWidths=[USEFUL_W])
    band.setStyle(_TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),20),("BOTTOMPADDING",(0,0),(-1,-1),20)]))
    story.append(Spacer(1, 0.8*_cm))
    story.append(band)
    # Sous-bande terracotta
    sub_data = [[_Para(f"<font color='white'>{subtitle}</font>",
        _PS("cs369", fontSize=11, fontName="Helvetica",
            textColor=BLANC, alignment=_TA_CENTER))]]
    sub = _Table(sub_data, colWidths=[USEFUL_W])
    sub.setStyle(_TableStyle([("BACKGROUND",(0,0),(-1,-1),TERRA),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story.append(sub)
    story.append(Spacer(1, 0.6*_cm))
    # Logo centré
    logo = get_logo(width=5*_cm, height=2*_cm)
    if logo:
        lt = _Table([[logo]], colWidths=[USEFUL_W])
        lt.setStyle(_TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
        story.append(lt)
        story.append(Spacer(1, 0.5*_cm))
    # Infos patient
    n = len(bilans_df)
    pat = [
        ["Patient",           f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"],
        ["Date de naissance", str(patient_info.get("date_naissance","—"))],
        ["Sexe",              patient_info.get("sexe","—")],
        ["Profession",        patient_info.get("profession","—") or "—"],
        ["Nombre de bilans",  str(n)],
        ["Généré le",         _date.today().strftime("%d/%m/%Y")],
    ]
    pt = _Table(pat, colWidths=[4.5*_cm, USEFUL_W-4.5*_cm])
    pt.setStyle(_TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(1,0),(1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("TEXTCOLOR",(0,0),(0,-1),BLEU),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[BLANC,BLEU_LIGHT]),
        ("LINEBELOW",(0,0),(-1,-1),0.3,GRIS_BORD),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.6*_cm))
    # Tableau bilans
    story.append(_Para("Bilans inclus dans ce rapport",
        _PS("subs369b", fontSize=10, fontName="Helvetica-Bold",
            textColor=TERRA, spaceBefore=8, spaceAfter=4)))
    bil = [["#","Date","Type","Praticien"]]
    for i,(_, row) in enumerate(bilans_df.iterrows()):
        d = row["date_bilan"]
        ds = d.strftime("%d/%m/%Y") if _pd.notna(d) else "—"
        bil.append([str(i+1), ds, row.get("type_bilan","—") or "—",
                    row.get("praticien","—") or "—"])
    story.append(make_table(bil, col_widths=[1.2*_cm,3.2*_cm,5*_cm,USEFUL_W-9.4*_cm]))



# ─── Couleurs ─────────────────────────────────────────────────────────────────
BLEU_CLAIR = BLEU_LIGHT
GRIS_CLAIR = GRIS
W = USEFUL_W


# ─── Styles ───────────────────────────────────────────────────────────────────
def make_styles_questionnaires():
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
CHECKBOX = "[  ]"  # fallback text   # caractère unicode case vide


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
    header = [[option_row(lbl, ParagraphStyle(
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
    rows = [[option_row(lbl, styles["option"])] for _, lbl in options]
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


# ─── Nijmegen data ────────────────────────────────────────────────────────────
_NIJMEGEN_ITEMS = [
    "Douleur thoracique",
    "Sensation de tension",
    "Vision troublée",
    "Étourdissements",
    "Confusion ou perte de contact",
    "Accélération ou irrégularité du rythme cardiaque",
    "Anxiété",
    "Mains, pieds ou visage engourdis",
    "Difficultés à respirer ou à avaler",
    "Raideur des mains ou des pieds",
    "Serrement autour de la bouche",
    "Picotements dans les doigts",
    "Abdomen tendu ou ballonné",
    "Vertiges",
    "Impression d'étouffement",
    "Tension dans la région thoracique",
]
_NIJMEGEN_OPTIONS = ["Jamais", "Rarement", "Parfois", "Souvent", "Très souvent"]


def build_nijmegen(story, styles):
    """Questionnaire de Nijmegen imprimable."""
    story.append(section_band("Questionnaire de Nijmegen"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Pour chacun des symptômes suivants, indiquez la fréquence à laquelle vous les ressentez.",
        styles["intro"]))
    story.append(Spacer(1, 0.2*cm))

    # En-tête tableau
    header = [["Symptôme"] + _NIJMEGEN_OPTIONS]
    rows = []
    for i, item in enumerate(_NIJMEGEN_ITEMS):
        row = [Paragraph(f"{i+1}. {item}", ParagraphStyle(
            "nij_item", fontSize=8, fontName="Helvetica", textColor=NOIR,
            spaceAfter=1, leading=10))]
        for _ in _NIJMEGEN_OPTIONS:
            row.append(Checkbox(size=8))
        rows.append(row)

    col_item = USEFUL_W - 5 * 1.8*cm
    col_opt  = 1.8*cm
    col_widths = [col_item] + [col_opt]*5

    tbl = Table(header + rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  8),
        ("BACKGROUND",    (0,0),(-1,0),  BLEU),
        ("TEXTCOLOR",     (0,0),(-1,0),  BLANC),
        ("ALIGN",         (1,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Score : comptez 0 = Jamais · 1 = Rarement · 2 = Parfois · 3 = Souvent · 4 = Très souvent  "
        "→  Seuil SHV positif : ≥ 23 points",
        ParagraphStyle("nij_leg", fontSize=7.5, fontName="Helvetica-Oblique",
                       textColor=GRIS_TEXTE)))


def build_mrc(story, styles):
    """Échelle MRC Dyspnée imprimable."""
    story.append(section_band("Échelle MRC — Dyspnée"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Cochez le grade qui décrit le mieux votre essoufflement au quotidien.",
        styles["intro"]))
    story.append(Spacer(1, 0.2*cm))

    grades = [
        (0, "Pas de dyspnée sauf en cas d'exercice intense"),
        (1, "Dyspnée lors d'une montée rapide ou d'une côte légère"),
        (2, "Marche plus lentement que les personnes du même âge à plat, "
            "ou s'arrête à son propre rythme"),
        (3, "S'arrête après 100 m ou quelques minutes à plat"),
        (4, "Trop essoufflé(e) pour quitter la maison, ou essoufflé(e) "
            "en s'habillant/déshabillant"),
    ]

    rows = []
    for grade, desc in grades:
        rows.append([
            Checkbox(size=10),
            Paragraph(f"<b>Grade {grade}</b>", ParagraphStyle(
                "mrc_g", fontSize=10, fontName="Helvetica-Bold",
                textColor=BLEU, leading=14)),
            Paragraph(desc, ParagraphStyle(
                "mrc_d", fontSize=9, fontName="Helvetica",
                textColor=NOIR, leading=13)),
        ])

    tbl = Table(rows, colWidths=[0.7*cm, 2.5*cm, USEFUL_W - 3.2*cm])
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Grade sélectionné : ______  "
        "Date : _____________  "
        "Initiales patient : ______",
        ParagraphStyle("mrc_fill", fontSize=9, fontName="Helvetica", textColor=GRIS_TEXTE)))


def build_comorb(story, styles):
    """Checklist comorbidités imprimable."""
    story.append(section_band("Comorbidités & Antécédents"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Cochez les affections dont vous souffrez ou avez souffert. "
        "Ajoutez tout autre renseignement pertinent dans la zone 'Autres'.",
        styles["intro"]))
    story.append(Spacer(1, 0.3*cm))

    categories = [
        ("🫁 Respiratoires", [
            "Asthme", "BPCO / Emphysème", "Bronchectasies",
            "Rhinite / sinusite chronique", "Apnées du sommeil (SAOS)", "Fibrose pulmonaire",
        ]),
        ("❤️ Cardio-vasculaires", [
            "Insuffisance cardiaque", "Hypertension artérielle",
            "Arythmie / tachycardie", "Cardiopathie ischémique", "Embolie pulmonaire (antécédent)",
        ]),
        ("🧠 Neurologique / Psychiatrique", [
            "Trouble anxieux généralisé", "Trouble panique", "Dépression",
            "Stress post-traumatique", "Épilepsie",
        ]),
        ("🦴 Musculo-squelettique", [
            "Scoliose / cyphose", "Douleurs chroniques", "Fibromyalgie",
        ]),
        ("⚗️ Métabolique / Endocrinien", [
            "Diabète", "Dysthyroïdie", "Anémie", "Reflux gastro-œsophagien (RGO)",
        ]),
        ("💊 Traitements en cours", [
            "Bronchodilatateurs", "Corticoïdes inhalés", "Anxiolytiques / benzodiazépines",
            "Antidépresseurs", "Bêtabloquants", "Diurétiques",
        ]),
    ]

    for cat_name, items in categories:
        story.append(Paragraph(cat_name, ParagraphStyle(
            "cat_h", fontSize=10, fontName="Helvetica-Bold",
            textColor=TERRA, spaceBefore=10, spaceAfter=4)))
        # 2 items per row
        for j in range(0, len(items), 2):
            pair = items[j:j+2]
            row = []
            for item in pair:
                row += [Checkbox(size=8),
                        Paragraph(item, ParagraphStyle(
                            "ci", fontSize=9, fontName="Helvetica",
                            textColor=NOIR, leading=12))]
            # Pad if odd
            while len(row) < 4:
                row += ["", ""]
            col_w = [0.5*cm, (USEFUL_W/2)-0.5*cm] * 2
            r_tbl = Table([row], colWidths=col_w)
            r_tbl.setStyle(TableStyle([
                ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
                ("TOPPADDING",   (0,0),(-1,-1), 3),
                ("BOTTOMPADDING",(0,0),(-1,-1), 3),
                ("LEFTPADDING",  (0,0),(-1,-1), 4),
            ]))
            story.append(r_tbl)

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Autres / remarques :", ParagraphStyle(
        "other_lbl", fontSize=9, fontName="Helvetica-Bold", textColor=NOIR)))
    story.append(Spacer(1, 0.2*cm))
    for _ in range(3):
        story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_BORD))
        story.append(Spacer(1, 0.4*cm))


# ═══════════════════════════════════════════════════════════════════════════════
#  BUILD — Testing musculaire membres inférieurs (fiche imprimable)
# ═══════════════════════════════════════════════════════════════════════════════

def build_muscle_testing(story, styles):
    """Fiche testing musculaire membres inférieurs imprimable."""
    MUSCLE_GROUPS_PRINT = [
        ("Fléchisseurs de hanche",       "Décubitus dorsal — flexion contre résistance"),
        ("Extenseurs de hanche",         "Décubitus ventral — extension contre résistance"),
        ("Abducteurs de hanche",         "Décubitus latéral — abduction contre résistance"),
        ("Adducteurs de hanche",         "Décubitus latéral — adduction contre résistance"),
        ("Extenseurs du genou (Quad)",   "Assis — extension contre résistance"),
        ("Fléchisseurs du genou (IJ)",   "Décubitus ventral — flexion contre résistance"),
        ("Dorsiflexeurs cheville",       "Décubitus dorsal — dorsiflexion contre résistance"),
        ("Plantarflexeurs cheville",     "Debout — montée sur pointe des pieds"),
    ]

    story.append(section_band("Testing musculaire — Membres inférieurs"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Échelle MRC : 0 = aucune contraction · 1 = contraction sans mvt · "
        "2 = mvt pesanteur éliminée · 3 = mvt contre pesanteur · "
        "4 = mvt contre résistance partielle · 5 = force normale",
        ParagraphStyle("musc_leg", fontSize=8, fontName="Helvetica-Oblique",
                       textColor=GRIS_TEXTE, spaceAfter=6)))

    # Tableau
    header = [[
        Paragraph("<b>Groupe musculaire</b>",
            ParagraphStyle("mh1",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC)),
        Paragraph("<b>Position / méthode</b>",
            ParagraphStyle("mh2",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC)),
        Paragraph("<b>Droit</b>",
            ParagraphStyle("mhd",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
        Paragraph("<b>Gauche</b>",
            ParagraphStyle("mhg",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
        Paragraph("<b>Observations</b>",
            ParagraphStyle("mho",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC)),
    ]]
    rows = []
    for label, desc in MUSCLE_GROUPS_PRINT:
        rows.append([
            Paragraph(f"<b>{label}</b>",
                ParagraphStyle("ml",fontSize=8,fontName="Helvetica-Bold",textColor=NOIR,leading=11)),
            Paragraph(desc,
                ParagraphStyle("md",fontSize=7.5,fontName="Helvetica",textColor=GRIS_TEXTE,leading=10)),
            "",  # Droit — à remplir à la main
            "",  # Gauche — à remplir à la main
            "",  # Observations
        ])

    col_w = [4.2*cm, USEFUL_W - 4.2*cm - 1.5*cm - 1.5*cm - 3.5*cm, 1.5*cm, 1.5*cm, 3.5*cm]
    tbl = Table(header + rows, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BLEU),
        ("TEXTCOLOR",     (0,0),(-1,0),  BLANC),
        ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("ALIGN",         (2,0),(3,-1),  "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("LINEAFTER",     (1,1),(3,-1),  0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    # Score global
    score_tbl = Table([[
        Paragraph("<b>Score global MRC</b>",
            ParagraphStyle("sg",fontSize=9,fontName="Helvetica-Bold",textColor=BLEU)),
        Paragraph("Moyenne D : ___/5   ·   Moyenne G : ___/5   ·   Moyenne globale : ___/5",
            ParagraphStyle("sgv",fontSize=9,fontName="Helvetica",textColor=NOIR)),
    ]], colWidths=[4.5*cm, USEFUL_W-4.5*cm])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLEU_LIGHT),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Notes :", ParagraphStyle(
        "musc_nl", fontSize=9, fontName="Helvetica-Bold", textColor=NOIR)))
    story.append(Spacer(1, 0.2*cm))
    for _ in range(2):
        story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_BORD))
        story.append(Spacer(1, 0.4*cm))


def build_leg_press(story, styles):
    """Fiche 1RM Leg Press imprimable."""
    story.append(section_band("1RM Leg Press — Test de force"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Formule de Brzycki (1–10 rép.) : 1RM = charge / (1.0278 − 0.0278 × rép.)  |  "
        "Epley (> 10 rép.) : 1RM = charge × (1 + rép./30)",
        ParagraphStyle("lp_leg", fontSize=8, fontName="Helvetica-Oblique",
                       textColor=GRIS_TEXTE, spaceAfter=8)))

    rows = [
        ["Poids corporel (kg)", "________", "Date", "________________"],
        ["Charge utilisée (kg)", "________", "Répétitions", "________"],
        ["1RM estimé (kg)", "________", "Ratio 1RM / poids corporel", "________"],
        ["Machine / réglages", "", "", ""],
    ]
    tbl = Table(rows, colWidths=[5*cm, 3.5*cm, 5*cm, USEFUL_W-13.5*cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (2,0),(2,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("TEXTCOLOR",     (0,0),(0,-1), BLEU),
        ("TEXTCOLOR",     (2,0),(2,-1), BLEU),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("SPAN",          (1,3),(3,3)),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Observations :", ParagraphStyle(
        "lp_obs", fontSize=9, fontName="Helvetica-Bold", textColor=NOIR)))
    story.append(Spacer(1, 0.2*cm))
    for _ in range(2):
        story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_BORD))
        story.append(Spacer(1, 0.4*cm))


# ═══════════════════════════════════════════════════════════════════════════════
#  Registre des questionnaires imprimables
# ═══════════════════════════════════════════════════════════════════════════════

QUESTIONNAIRES = {
    "had":      ("HAD — Anxiété & Dépression", build_had),
    "sf12":     ("SF-12 — Qualité de vie",     build_sf12),
    "hvt":      ("Test d'Hyperventilation",    build_hvt),
    "bolt":     ("Test BOLT",                  build_bolt),
    "nijmegen": ("Questionnaire de Nijmegen",  build_nijmegen),
    "mrc":      ("Échelle MRC Dyspnée",        build_mrc),
    "comorb":   ("Comorbidités & Antécédents", build_comorb),
}


def generate_questionnaires_pdf(selected: list, patient_info: dict) -> bytes:
    """Génère un PDF avec les questionnaires sélectionnés."""
    buffer = io.BytesIO()
    styles  = make_styles()
    story   = []

    def hf(canvas, doc):
        name = f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else ""
        make_header_footer("36.9 Bilans — Questionnaires imprimables", patient_name=name)(canvas, doc)

    for i, key in enumerate(selected):
        if key not in QUESTIONNAIRES:
            continue
        title, builder = QUESTIONNAIRES[key]
        story.append(Paragraph(title, styles["section"]))
        story.append(Spacer(1, 0.3*cm))
        builder(story, styles)
        if i < len(selected) - 1:
            story.append(PageBreak())

    if not story:
        story.append(Paragraph("Aucun questionnaire sélectionné.", styles["normal"]))

    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.2*cm, bottomMargin=1.8*cm)
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return buffer.getvalue()


QUESTIONNAIRES["muscle"] = ("Testing musculaire MI", build_muscle_testing)
QUESTIONNAIRES["leg_press"] = ("1RM Leg Press", build_leg_press)
