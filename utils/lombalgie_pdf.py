"""
lombalgie_pdf.py — PDF Lombalgie
Fusion : pdf_lombalgie.py · questionnaires_lombalgie.py
"""

import os as _os
from reportlab.lib import colors as _colors
from reportlab.lib.pagesizes import A4 as _A4
from reportlab.lib.units import cm as _cm
from reportlab.lib.enums import TA_CENTER as _TA_CENTER
from reportlab.lib.styles import ParagraphStyle as _PS
from reportlab.platypus import Table as _Table, TableStyle as _TableStyle, Paragraph as _Para, Image as _Image
import io
import numpy as np
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image,
)
import matplotlib
import matplotlib.pyplot as plt
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ════════════════════════════════════════════════════════════
# pdf_lombalgie.py
# ════════════════════════════════════════════════════════════
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

GRIS = GRIS
W = USEFUL_W


def safe_n(val):
    try:
        v = float(val)
        return v if v != 0 else None
    except (TypeError, ValueError):
        return None


def val_s(val, suffix=""):
    v = safe_n(val)
    if v is None: return "—"
    return f"{int(v)}{suffix}" if v == int(v) else f"{v}{suffix}"


# ─── Styles ───────────────────────────────────────────────────────────────────


def fig_to_img(fig, width_cm=17, height_cm=7):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width_cm*cm, height=height_cm*cm)


def short_labels(labels):
    return [l.split("–")[0].strip() for l in labels]


# ─── Graphiques ───────────────────────────────────────────────────────────────

def chart_eva(bilans_df, labels):
    xlbls = short_labels(labels)
    x = range(len(xlbls))
    fig, ax = plt.subplots(figsize=(10, 4))
    for key, label, color, marker in [
        ("s_eva_repos",    "EVA Repos",     "#388e3c", "o"),
        ("s_eva_mouvement","EVA Mouvement", "#f57c00", "s"),
        ("s_eva_nuit",     "EVA Nuit",      "#7b1fa2", "^"),
    ]:
        vals = [safe_n(r.get(key)) for _, r in bilans_df.iterrows()]
        xp = [i for i,v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        if xp:
            ax.plot(xp, yp, f"{marker}-", color=color, linewidth=2.5,
                    markersize=8, label=label)
            for xi,yi in zip(xp,yp):
                ax.annotate(str(int(yi)), (xi,yi), textcoords="offset points",
                            xytext=(0,8), ha="center", fontsize=8, color=color, fontweight="bold")
    ax.axhline(3, linestyle="--", color="#388e3c", linewidth=1, alpha=0.6, label="3 légère")
    ax.axhline(6, linestyle="--", color="#f57c00", linewidth=1, alpha=0.6, label="6 modérée")
    ax.set_xticks(list(x)); ax.set_xticklabels(xlbls, rotation=15, ha="right", fontsize=9)
    ax.set_ylim(0, 11); ax.set_ylabel("EVA /10")
    ax.set_title("Évolution EVA", fontsize=11, fontweight="bold", color="#2e5a1c")
    ax.legend(fontsize=8, framealpha=0.8); ax.spines[["top","right"]].set_visible(False)
    ax.set_facecolor("white"); fig.tight_layout()
    return fig_to_img(fig, 17, 6)


def chart_questionnaires(bilans_df, labels):
    xlbls = short_labels(labels)
    x = list(range(len(xlbls)))
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    configs = [
        ("odi_score",   "ODI (%)",     "#1a3c5e", [(20,"#388e3c"),(40,"#8bc34a"),(60,"#f57c00"),(80,"#e64a19")], 100),
        ("tampa_score", "Tampa (/68)", "#f57c00", [(37,"#388e3c"),(44,"#f57c00")], 68),
        ("orebro_score","Örebro",      "#7b1fa2", [(50,"#388e3c"),(74,"#f57c00")], 100),
    ]
    for ax, (key, title, color, thrs, ymax) in zip(axes, configs):
        vals = [safe_n(r.get(key)) for _, r in bilans_df.iterrows()]
        xp = [i for i,v in enumerate(vals) if v is not None]
        yp = [v for v in vals if v is not None]
        bars = ax.bar(xp, yp, color=color, width=0.5, zorder=3)
        for bar, v in zip(bars, yp):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                    str(int(v)), ha="center", fontsize=9, fontweight="bold")
        for thr, tc in thrs:
            ax.axhline(thr, linestyle="--", color=tc, linewidth=1.2, alpha=0.7)
        ax.set_xticks(x); ax.set_xticklabels(xlbls, rotation=15, ha="right", fontsize=8)
        ax.set_ylim(0, ymax + 10); ax.set_title(title, fontsize=9, fontweight="bold", color="#2e5a1c")
        ax.spines[["top","right"]].set_visible(False)
        ax.set_facecolor("white"); ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig_to_img(fig, 17, 5.5)


def chart_luomajoki(bilans_df, labels):
    xlbls = short_labels(labels)
    vals  = [safe_n(r.get("o_luomajoki_score")) for _, r in bilans_df.iterrows()]
    if not any(vals):
        return None
    fig, ax = plt.subplots(figsize=(10, 3.5))
    bar_cols = ["#d32f2f" if v and v>=3 else "#f57c00" if v and v>=1 else "#388e3c" for v in vals]
    bars = ax.bar(range(len(xlbls)), [v or 0 for v in vals], color=bar_cols, width=0.5)
    for bar, v in zip(bars, vals):
        if v:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                    f"{int(v)}/6", ha="center", fontsize=9, fontweight="bold")
    ax.axhline(3, linestyle="--", color="#d32f2f", linewidth=1.5, label="Seuil significatif (≥3)")
    ax.set_xticks(range(len(xlbls))); ax.set_xticklabels(xlbls, rotation=15, ha="right", fontsize=9)
    ax.set_ylim(0, 7); ax.set_ylabel("Échecs /6")
    ax.set_title("Tests de Luomajoki", fontsize=11, fontweight="bold", color="#2e5a1c")
    ax.legend(fontsize=8); ax.spines[["top","right"]].set_visible(False)
    ax.set_facecolor("white"); ax.grid(axis="y", alpha=0.3); fig.tight_layout()
    return fig_to_img(fig, 17, 5.5)


def chart_mobilite(bilans_df, labels):
    xlbls = short_labels(labels)
    MOB_NUM = {"1/3": 1, "2/3": 2, "3/3": 3}
    mob_keys = [
        ("o_extension_mob",  "Extension"),
        ("o_lat_droite_mob", "Latérofl. D"),
        ("o_lat_gauche_mob", "Latérofl. G"),
        ("o_rot_droite_mob", "Rotation D"),
        ("o_rot_gauche_mob", "Rotation G"),
    ]
    colors_mob = ["#1a3c5e","#f57c00","#388e3c","#7b1fa2","#d32f2f"]
    n = len(bilans_df)
    x = np.arange(len(mob_keys))
    width = 0.7 / max(n, 1)

    fig, ax = plt.subplots(figsize=(12, 4))
    for j, (_, row) in enumerate(bilans_df.iterrows()):
        vals = [MOB_NUM.get(row.get(key,""), 0) for key, _ in mob_keys]
        offset = (j - (n-1)/2) * width
        bars = ax.bar(x + offset, vals, width=width*0.9,
                      color=colors_mob[j % len(colors_mob)],
                      label=xlbls[j], zorder=3)
        for bar, v, (key, klabel) in zip(bars, vals, mob_keys):
            txt = row.get(key,"") or ""
            if txt:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                        txt, ha="center", fontsize=7, fontweight="bold")

    ax.set_xticks(x); ax.set_xticklabels([kl for _, kl in mob_keys], fontsize=9)
    ax.set_yticks([1,2,3]); ax.set_yticklabels(["1/3","2/3","3/3"])
    ax.set_ylim(0, 4); ax.set_title("Mobilité lombaire", fontsize=11, fontweight="bold", color="#2e5a1c")
    ax.legend(fontsize=8, framealpha=0.8); ax.spines[["top","right"]].set_visible(False)
    ax.set_facecolor("white"); ax.grid(axis="y", alpha=0.3); fig.tight_layout()
    return fig_to_img(fig, 17, 5.5)


# ═══════════════════════════════════════════════════════════════════════════════
#  GÉNÉRATEUR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def generate_pdf_lombalgie(bilans_df, patient_info: dict) -> bytes:
    import pandas as pd
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=1.8*cm,
        title=f"Bilan Lombalgie – {patient_info.get('nom','')} {patient_info.get('prenom','')}")

    styles = make_styles()
    story  = []
    hf = make_header_footer("36.9 Bilans", f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else "")

    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)
    n = len(bilans_df)

    def bilan_label(row):
        d = row["date_bilan"]
        ds = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        return f"{ds} — {row.get('type_bilan','')}"

    labels = [bilan_label(r) for _, r in bilans_df.iterrows()]

    # ── Page de garde moderne ───────────────────────────────────────────────────
    make_cover(story,
               title="Rapport d'évolution — Lombalgie",
               subtitle="Bilan physiothérapeutique",
               patient_info=patient_info,
               bilans_df=bilans_df,
               labels=labels,
               styles=styles)

# ════════════════════════════════════════════════════════════
# questionnaires_lombalgie.py
# ════════════════════════════════════════════════════════════
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



GRIS_CLAIR = GRIS
BLEU_CLAIR = BLEU_LIGHT
BLEU_FONCE = BLEU
BLEU_CLAIR = BLEU_LIGHT
W = USEFUL_W
CHECKBOX = "☐"

def make_styles():
    base = getSampleStyleSheet()
    return {
        "question": ParagraphStyle("q", fontSize=10, fontName="Helvetica-Bold",
                                   textColor=NOIR, spaceBefore=8, spaceAfter=3),
        "option":   ParagraphStyle("o", fontSize=9, fontName="Helvetica",
                                   textColor=NOIR, spaceAfter=2, leftIndent=20),
        "intro":    ParagraphStyle("i", fontSize=9, fontName="Helvetica-Oblique",
                                   textColor=colors.HexColor("#444"), spaceAfter=6),
        "small":    ParagraphStyle("sm", fontSize=8, fontName="Helvetica",
                                   textColor=colors.HexColor("#666")),
    }

def section_header(title, subtitle=""):
    tbl = Table([[Paragraph(title, ParagraphStyle("th", fontSize=13,
        fontName="Helvetica-Bold", textColor=BLANC))]], colWidths=[W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    items = [tbl]
    if subtitle:
        items.append(Paragraph(subtitle, ParagraphStyle("ts", fontSize=8,
            fontName="Helvetica-Oblique", textColor=colors.HexColor("#555"), spaceAfter=4)))
    return items


def radio_v(num, question, options, styles):
    q_text = f"{num}. {question}" if question else str(num)
    items = [Paragraph(q_text, styles["question"])]
    rows = [[Paragraph(f"{CHECKBOX}  {lbl}", styles["option"])] for lbl in options]
    tbl = Table(rows, colWidths=[W])
    tbl.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),20),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[BLANC, GRIS_CLAIR]),
        ("GRID",(0,0),(-1,-1),0.3,GRIS_BORD),
    ]))
    items.append(tbl)
    return KeepTogether(items)

def score_footer(label, max_score, guide):
    rows = [[f"Score : _______ / {max_score}", ""]]
    tbl = Table(rows, colWidths=[W/2, W/2])
    tbl.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("TEXTCOLOR",(0,0),(0,0),BLEU),
        ("BACKGROUND",(0,0),(-1,-1),BLEU_CLAIR),
        ("BOX",(0,0),(-1,-1),1,BLEU),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    return [tbl, Paragraph(guide, ParagraphStyle("ig", fontSize=7,
        fontName="Helvetica", textColor=colors.HexColor("#666"), spaceBefore=3))]

def build_odi(story, styles):
    story += section_header("Oswestry Disability Index (ODI)",
        "Fairbank & Pynsent, 2000 — Version française — 10 sections, score 0–100%")
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Cochez UNE SEULE case par section — celle qui décrit le mieux votre situation aujourd'hui.",
        styles["intro"]))
    sections = [
        ("1. Intensité de la douleur", [
            "Pas de douleur actuellement",
            "La douleur est très légère",
            "La douleur est modérée",
            "La douleur est assez sévère",
            "La douleur est très sévère",
            "La douleur est la pire imaginable",
        ]),
        ("2. Soins personnels (se laver, s'habiller)", [
            "Je me prends en charge normalement sans douleur supplémentaire",
            "Je me prends en charge normalement mais c'est très douloureux",
            "Se prendre en charge est douloureux — je suis lent(e) et prudent(e)",
            "J'ai besoin d'aide mais j'arrive à gérer la plupart de mes soins",
            "J'ai besoin d'aide chaque jour pour la plupart de mes soins",
            "Je ne m'habille pas, me lave avec difficulté et reste au lit",
        ]),
        ("3. Soulever des charges", [
            "Je peux soulever des charges lourdes sans douleur",
            "Je peux soulever des charges lourdes mais avec douleur",
            "La douleur m'empêche de soulever des charges lourdes du sol",
            "La douleur m'empêche de soulever des charges lourdes — je peux soulever du léger si bien placé",
            "Je peux soulever des charges très légères uniquement",
            "Je ne peux rien soulever ni porter",
        ]),
        ("4. Marche", [
            "La douleur ne m'empêche pas de marcher",
            "La douleur m'empêche de marcher plus d'un kilomètre",
            "La douleur m'empêche de marcher plus de 500 mètres",
            "La douleur m'empêche de marcher plus de 100 mètres",
            "Je ne marche qu'avec une canne ou des béquilles",
            "Je suis au lit et dois me traîner pour aller aux toilettes",
        ]),
        ("5. Position assise", [
            "Je peux rester assis(e) aussi longtemps que je veux sans douleur",
            "Je peux rester assis(e) aussi longtemps que je veux avec légère douleur",
            "La douleur m'empêche de rester assis(e) plus d'une heure",
            "La douleur m'empêche de rester assis(e) plus de 30 minutes",
            "La douleur m'empêche de rester assis(e) plus de 10 minutes",
            "La douleur m'empêche totalement de m'asseoir",
        ]),
        ("6. Position debout", [
            "Je peux rester debout aussi longtemps que je veux sans douleur",
            "Je peux rester debout aussi longtemps que je veux mais avec douleur",
            "La douleur m'empêche de rester debout plus d'une heure",
            "La douleur m'empêche de rester debout plus de 30 minutes",
            "La douleur m'empêche de rester debout plus de 10 minutes",
            "La douleur m'empêche totalement de rester debout",
        ]),
        ("7. Sommeil", [
            "Mon sommeil n'est jamais perturbé par la douleur",
            "Mon sommeil est parfois perturbé",
            "Je dors moins de 6 heures à cause de la douleur",
            "Je dors moins de 4 heures à cause de la douleur",
            "Je dors moins de 2 heures à cause de la douleur",
            "La douleur m'empêche totalement de dormir",
        ]),
        ("8. Vie sexuelle (si applicable)", [
            "Ma vie sexuelle est normale, sans douleur",
            "Ma vie sexuelle est normale mais douloureuse",
            "Ma vie sexuelle est presque normale mais très douloureuse",
            "Ma vie sexuelle est sévèrement limitée par la douleur",
            "Ma vie sexuelle est presque absente",
            "La douleur empêche toute vie sexuelle",
        ]),
        ("9. Vie sociale", [
            "Ma vie sociale est normale sans douleur supplémentaire",
            "Ma vie sociale est normale mais augmente ma douleur",
            "La douleur n'affecte pas les activités légères mais limite les activités énergiques",
            "La douleur a limité ma vie sociale — je sors moins souvent",
            "La douleur a limité ma vie sociale à ma maison",
            "Je n'ai pas de vie sociale à cause de la douleur",
        ]),
        ("10. Voyages / transports", [
            "Je peux voyager n'importe où sans douleur",
            "Je peux voyager n'importe où mais avec douleur",
            "La douleur est sévère mais je gère les trajets > 2 heures",
            "La douleur me limite à des trajets < 1 heure",
            "La douleur me limite à des trajets courts < 30 minutes",
            "La douleur m'empêche de voyager sauf pour des soins médicaux",
        ]),
    ]
    for title, options in sections:
        story.append(radio_v(title, "", options, styles))
        story.append(Spacer(1, 0.1*cm))
    story.append(Spacer(1, 0.4*cm))
    story += score_footer("ODI", 100,
        "0–20% : incapacité minimale  ·  21–40% : modérée  ·  41–60% : sévère  ·  61–80% : très sévère  ·  >80% : grabataire")

def build_tampa(story, styles):
    story += section_header("Tampa Scale for Kinesiophobia (TSK-17)",
        "Miller et al., 1991 — Version française — Score 17–68")
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Indiquez dans quelle mesure vous êtes en accord avec chaque affirmation. "
        "1 = Pas du tout d'accord  ·  2 = Plutôt pas d'accord  ·  3 = Plutôt d'accord  ·  4 = Tout à fait d'accord",
        styles["intro"]))
    scale = ["1 — Pas du tout d'accord","2 — Plutôt pas d'accord","3 — Plutôt d'accord","4 — Tout à fait d'accord"]
    items_text = [
        "J'ai peur de me blesser si je fais de l'exercice.",
        "Si j'essayais de surmonter ma douleur, celle-ci augmenterait.",
        "Mon corps me dit que quelque chose ne va pas vraiment.",
        "Ma blessure a mis mon corps en danger toute ma vie.",
        "Les gens ne prennent pas ma condition médicale assez au sérieux.",
        "Ma blessure a mis mon corps en danger de façon permanente.",
        "La douleur signifie toujours que j'ai subi une blessure.",
        "Simplement parce que quelque chose aggrave ma douleur ne signifie pas qu'elle est dangereuse. (R)",
        "J'ai peur de me blesser accidentellement.",
        "Le plus sûr est de faire attention à ne pas faire de mouvements inutiles.",
        "Je n'aurais pas autant de douleur si quelque chose de grave ne se passait pas.",
        "Bien que ma condition soit douloureuse, je me sentirais mieux si j'étais plus actif(ve). (R)",
        "La douleur me signale que je dois arrêter pour ne pas me blesser.",
        "Ce n'est pas sûr pour quelqu'un avec ma condition d'être physiquement actif(ve).",
        "Je risque trop facilement de me blesser.",
        "Même si quelque chose me fait très mal, je ne pense pas que ce soit dangereux. (R)",
        "Personne ne devrait faire d'exercice quand il souffre de douleur.",
    ]
    for i, txt in enumerate(items_text):
        story.append(radio_v(str(i+1), txt, scale, styles))
        story.append(Spacer(1, 0.1*cm))
    story.append(Spacer(1, 0.4*cm))
    story += score_footer("TSK-17", 68,
        "≤ 37 : kinésiophobie faible  ·  38–44 : modérée  ·  > 44 : élevée  (R) = items inversés")

def build_orebro(story, styles):
    story += section_header("Örebro Musculoskeletal Pain Questionnaire",
        "Linton & Hallden, 1998 — Dépistage du risque de chronicisation")
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Ce questionnaire évalue les facteurs pouvant influencer l'évolution de votre douleur. "
        "Pour les questions avec une échelle de 0 à 10, entourez le chiffre correspondant.",
        styles["intro"]))

    def scale_row(num, question):
        story.append(Paragraph(f"{num}. {question}", styles["question"]))
        nums = ["0","1","2","3","4","5","6","7","8","9","10"]
        tbl = Table([nums], colWidths=[(W)/11]*11)
        tbl.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
            ("FONTSIZE",(0,0),(-1,-1),10),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("GRID",(0,0),(-1,-1),0.5,GRIS_BORD),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[GRIS_CLAIR]),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.1*cm))

    scale_row("1","Quelle est l'intensité de votre douleur en ce moment ? (0 = pas de douleur, 10 = insupportable)")
    scale_row("2","Dans quelle mesure votre douleur est-elle permanente ? (0 = jamais, 10 = toujours)")
    scale_row("3","La douleur perturbe-t-elle votre sommeil ? (0 = pas du tout, 10 = complètement)")
    scale_row("4","Avez-vous peur que l'activité aggrave votre douleur ? (0 = pas du tout, 10 = extrêmement)")
    scale_row("5","Pensez-vous que votre douleur va disparaître ? (0 = pas du tout, 10 = complètement)")
    scale_row("6","Quelle confiance avez-vous dans le fait de retourner au travail dans 3 mois ? (0 = aucune, 10 = totale)")
    scale_row("7","Dans quelle mesure pensez-vous pouvoir travailler malgré la douleur ? (0 = pas du tout, 10 = totalement)")

    story.append(Paragraph("Pour les activités suivantes, dans quelle mesure la douleur affecte-t-elle votre capacité ? (0 = pas d'effet, 10 = incapable)", styles["intro"]))
    activites = [
        "8. Activités légères à la maison (cuisiner, ranger)",
        "9. Activités lourdes (nettoyer, jardiner)",
        "10. Activités sociales (conversations, visites)",
        "11. Déplacements (transports, conduire)",
        "12. Loisirs légers",
        "13. Travail ou études",
    ]
    act_header = [["Activité"] + list(range(11))]
    act_rows   = [[act] + [CHECKBOX]*11 for act in activites]
    col_w = [7*cm] + [0.75*cm]*11
    act_tbl = Table(act_header + act_rows, colWidths=col_w)
    act_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),BLEU),
        ("TEXTCOLOR",(0,0),(-1,0),BLANC),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),7),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.3,GRIS_BORD),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[BLANC,GRIS_CLAIR]),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(act_tbl)
    story.append(Spacer(1, 0.4*cm))
    story += score_footer("Örebro", 100,
        "≤ 50 : risque faible  ·  51–74 : risque moyen  ·  ≥ 75 : risque élevé de chronicisation")

QUESTIONNAIRES_LOMB = {
    "odi":    ("Oswestry Disability Index",   build_odi),
    "tampa":  ("Tampa Scale (kinésiophobie)",  build_tampa),
    "orebro": ("Örebro",                      build_orebro),
}

def generate_questionnaires_lombalgie_pdf(selected, patient_info=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2*cm, bottomMargin=1.8*cm)
    styles = make_styles()
    story  = []
    hf = make_header_footer("36.9 Bilans — Questionnaires", f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else "")

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Questionnaires — Bilan Lombalgie",
        ParagraphStyle("gt", fontSize=22, fontName="Helvetica-Bold",
                       textColor=BLEU, alignment=TA_CENTER, spaceAfter=6)))
    if patient_info:
        story.append(Paragraph(
            f"Patient : {patient_info.get('nom','')} {patient_info.get('prenom','')}",
            ParagraphStyle("gs", fontSize=12, fontName="Helvetica",
                           textColor=colors.HexColor("#555"), alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLEU))
    story.append(Spacer(1, 0.4*cm))
    for key in selected:
        if key in QUESTIONNAIRES_LOMB:
            story.append(Paragraph(f"  ▸  {QUESTIONNAIRES_LOMB[key][0]}",
                ParagraphStyle("li", fontSize=10, fontName="Helvetica",
                               textColor=NOIR, spaceAfter=3)))
    story.append(PageBreak())

    for i, key in enumerate(selected):
        if key not in QUESTIONNAIRES_LOMB: continue
        QUESTIONNAIRES_LOMB[key][1](story, styles)
        if i < len(selected)-1: story.append(PageBreak())

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return buffer.getvalue()
"""
Questionnaires complets pour saisie in-app — Lombalgie
ODI, Tampa Scale (TSK-17), Örebro
Avec calcul automatique des scores.
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  OSWESTRY DISABILITY INDEX (ODI) — 10 sections, score 0–5 par section
# ═══════════════════════════════════════════════════════════════════════════════

ODI_SECTIONS = [
    ("odi_s1", "1. Intensité de la douleur", [
        "Pas de douleur actuellement",
        "La douleur est très légère actuellement",
        "La douleur est modérée actuellement",
        "La douleur est assez sévère actuellement",
        "La douleur est très sévère actuellement",
        "La douleur est la pire imaginable actuellement",
    ]),
    ("odi_s2", "2. Soins personnels (se laver, s'habiller…)", [
        "Je me prends en charge normalement sans douleur supplémentaire",
        "Je me prends en charge normalement mais c'est très douloureux",
        "Se prendre en charge est douloureux — je suis lent(e) et prudent(e)",
        "J'ai besoin d'aide mais j'arrive à gérer la plupart de mes soins",
        "J'ai besoin d'aide chaque jour pour la plupart de mes soins",
        "Je ne m'habille pas, me lave avec difficulté et reste au lit",
    ]),
    ("odi_s3", "3. Soulever des charges", [
        "Je peux soulever des charges lourdes sans douleur",
        "Je peux soulever des charges lourdes mais avec douleur supplémentaire",
        "La douleur m'empêche de soulever des charges lourdes du sol",
        "La douleur m'empêche de soulever des charges lourdes (je peux soulever du léger si bien placé)",
        "Je peux soulever des charges très légères uniquement",
        "Je ne peux rien soulever ni porter",
    ]),
    ("odi_s4", "4. Marche", [
        "La douleur ne m'empêche pas de marcher quelle que soit la distance",
        "La douleur m'empêche de marcher plus d'un kilomètre",
        "La douleur m'empêche de marcher plus de 500 mètres",
        "La douleur m'empêche de marcher plus de 100 mètres",
        "Je ne marche qu'avec une canne ou des béquilles",
        "Je suis au lit la plupart du temps et dois me traîner pour aller aux toilettes",
    ]),
    ("odi_s5", "5. Position assise", [
        "Je peux rester assis(e) aussi longtemps que je veux sans douleur",
        "Je peux rester assis(e) aussi longtemps que je veux avec légère douleur",
        "La douleur m'empêche de rester assis(e) plus d'une heure",
        "La douleur m'empêche de rester assis(e) plus de 30 minutes",
        "La douleur m'empêche de rester assis(e) plus de 10 minutes",
        "La douleur m'empêche totalement de m'asseoir",
    ]),
    ("odi_s6", "6. Position debout", [
        "Je peux rester debout aussi longtemps que je veux sans douleur",
        "Je peux rester debout aussi longtemps que je veux mais avec douleur",
        "La douleur m'empêche de rester debout plus d'une heure",
        "La douleur m'empêche de rester debout plus de 30 minutes",
        "La douleur m'empêche de rester debout plus de 10 minutes",
        "La douleur m'empêche totalement de rester debout",
    ]),
    ("odi_s7", "7. Sommeil", [
        "Mon sommeil n'est jamais perturbé par la douleur",
        "Mon sommeil est parfois perturbé par la douleur",
        "Je dors moins de 6 heures à cause de la douleur",
        "Je dors moins de 4 heures à cause de la douleur",
        "Je dors moins de 2 heures à cause de la douleur",
        "La douleur m'empêche totalement de dormir",
    ]),
    ("odi_s8", "8. Vie sexuelle (si applicable)", [
        "Ma vie sexuelle est normale sans douleur supplémentaire",
        "Ma vie sexuelle est normale mais provoque une douleur supplémentaire",
        "Ma vie sexuelle est presque normale mais est très douloureuse",
        "Ma vie sexuelle est sévèrement limitée par la douleur",
        "Ma vie sexuelle est presque absente en raison de la douleur",
        "La douleur empêche toute vie sexuelle",
    ]),
    ("odi_s9", "9. Vie sociale", [
        "Ma vie sociale est normale sans douleur supplémentaire",
        "Ma vie sociale est normale mais augmente le degré de douleur",
        "La douleur n'affecte pas les activités légères mais limite les activités énergiques",
        "La douleur a limité ma vie sociale — je sors moins souvent",
        "La douleur a limité ma vie sociale à ma maison",
        "Je n'ai pas de vie sociale à cause de la douleur",
    ]),
    ("odi_s10", "10. Voyages / transports", [
        "Je peux voyager n'importe où sans douleur supplémentaire",
        "Je peux voyager n'importe où mais avec douleur",
        "La douleur est sévère mais je gère les trajets de plus de 2 heures",
        "La douleur me restreint à des trajets de moins d'une heure",
        "La douleur me restreint à des trajets courts de moins de 30 minutes",
        "La douleur m'empêche de voyager sauf pour des soins médicaux",
    ]),
]

ODI_KEYS = [s[0] for s in ODI_SECTIONS]


def compute_odi(answers: dict) -> dict:
    """answers = {"odi_s1": 2, "odi_s2": 0, ...} (0–5 par section)"""
    scores = []
    for key, _, _ in ODI_SECTIONS:
        v = answers.get(key)
        if v is not None:
            scores.append(int(v))
    if not scores:
        return {"score": None, "interpretation": "", "color": "#888"}
    total = sum(scores)
    max_possible = len(scores) * 5
    pct = round(total / max_possible * 100)
    if pct <= 20:
        interp, color = "Incapacité minimale (0–20%)", "#388e3c"
    elif pct <= 40:
        interp, color = "Incapacité modérée (21–40%)", "#8bc34a"
    elif pct <= 60:
        interp, color = "Incapacité sévère (41–60%)", "#f57c00"
    elif pct <= 80:
        interp, color = "Incapacité très sévère (61–80%)", "#e64a19"
    else:
        interp, color = "Grabataire / exagération (>80%)", "#d32f2f"
    return {"score": pct, "interpretation": interp, "color": color, "raw": total}


# ═══════════════════════════════════════════════════════════════════════════════
#  TAMPA SCALE FOR KINESIOPHOBIA (TSK-17) — 17 items, score 1–4
# ═══════════════════════════════════════════════════════════════════════════════

TAMPA_SCALE = ["1 — Pas du tout d'accord", "2 — Plutôt pas d'accord",
               "3 — Plutôt d'accord", "4 — Tout à fait d'accord"]
TAMPA_SCALE_VALUES = [1, 2, 3, 4]

# Items inversés (R) : scores inversés pour le calcul (1→4, 2→3, 3→2, 4→1)
TAMPA_REVERSED = {8, 12, 16}  # indices 1-based

TAMPA_ITEMS = [
    ("tampa_1",  False, "J'ai peur de me blesser si je fais de l'exercice."),
    ("tampa_2",  False, "Si j'essayais de surmonter ma douleur, celle-ci augmenterait."),
    ("tampa_3",  False, "Mon corps me dit que quelque chose ne va pas vraiment."),
    ("tampa_4",  False, "Ma blessure a mis mon corps en danger toute ma vie."),
    ("tampa_5",  False, "Les gens ne prennent pas ma condition médicale assez au sérieux."),
    ("tampa_6",  False, "Ma blessure a mis mon corps en danger de façon permanente."),
    ("tampa_7",  False, "La douleur signifie toujours que j'ai subi une blessure corporelle."),
    ("tampa_8",  True,  "Simplement parce que quelque chose aggrave ma douleur ne signifie pas qu'elle est dangereuse."),
    ("tampa_9",  False, "J'ai peur de me blesser accidentellement."),
    ("tampa_10", False, "Le plus sûr est de faire attention à ne pas faire de mouvements inutiles."),
    ("tampa_11", False, "Je n'aurais pas autant de douleur si quelque chose de potentiellement grave ne se passait pas."),
    ("tampa_12", True,  "Bien que ma condition soit douloureuse, je me sentirais mieux si j'étais plus actif(ve)."),
    ("tampa_13", False, "La douleur me signale que je dois arrêter ce que je fais pour ne pas me blesser."),
    ("tampa_14", False, "Ce n'est pas vraiment sûr pour quelqu'un avec ma condition d'être physiquement actif(ve)."),
    ("tampa_15", False, "Je risque trop facilement de me blesser."),
    ("tampa_16", True,  "Même si quelque chose me fait très mal, je ne pense pas que ce soit dangereux."),
    ("tampa_17", False, "Personne ne devrait faire de l'exercice physique quand il souffre de douleur."),
]

TAMPA_KEYS = [t[0] for t in TAMPA_ITEMS]


def compute_tampa(answers: dict) -> dict:
    """answers = {"tampa_1": 3, "tampa_2": 1, ...} (1–4)"""
    total = 0
    count = 0
    for i, (key, reversed_item, _) in enumerate(TAMPA_ITEMS):
        v = answers.get(key)
        if v is not None:
            score = int(v)
            if reversed_item:
                score = 5 - score  # inversion : 1→4, 2→3, 3→2, 4→1
            total += score
            count += 1
    if count == 0:
        return {"score": None, "interpretation": "", "color": "#888"}
    if count < 17:
        # Extrapolation si items manquants
        total = round(total / count * 17)
    if total <= 37:
        interp, color = "Kinésiophobie faible (≤ 37)", "#388e3c"
    elif total <= 44:
        interp, color = "Kinésiophobie modérée (38–44)", "#f57c00"
    else:
        interp, color = "Kinésiophobie élevée (> 44)", "#d32f2f"
    return {"score": total, "interpretation": interp, "color": color}


# ═══════════════════════════════════════════════════════════════════════════════
#  ÖREBRO — items sur échelle 0–10
# ═══════════════════════════════════════════════════════════════════════════════

OREBRO_ITEMS = [
    ("orebro_1",
     "Quelle est l'intensité de votre douleur en ce moment ?",
     "0 = pas de douleur  ·  10 = douleur insupportable"),
    ("orebro_2",
     "Dans quelle mesure votre douleur est-elle présente en permanence pendant vos heures d'éveil ?",
     "0 = jamais  ·  10 = toujours"),
    ("orebro_3",
     "Dans quelle mesure la douleur perturbe-t-elle votre sommeil ?",
     "0 = pas du tout  ·  10 = complètement"),
    ("orebro_4",
     "Dans quelle mesure avez-vous peur que l'activité physique aggrave votre douleur ?",
     "0 = pas du tout  ·  10 = extrêmement"),
    ("orebro_5",
     "Dans quelle mesure pensez-vous que votre douleur disparaîtra ?",
     "0 = pas du tout  ·  10 = complètement"),
    ("orebro_6",
     "Quelle confiance avez-vous dans le fait de retourner au travail dans les 3 prochains mois ?",
     "0 = aucune confiance  ·  10 = très confiant(e)"),
    ("orebro_7",
     "Dans quelle mesure pensez-vous que vous pouvez effectuer un travail malgré la douleur ?",
     "0 = pas du tout  ·  10 = totalement"),
    ("orebro_8",
     "Activités légères à la maison (cuisiner, ranger) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_9",
     "Activités lourdes à la maison (nettoyer, jardiner) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_10",
     "Activités sociales (conversations, visites) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_11",
     "Déplacements (transports en commun, conduire) — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_12",
     "Loisirs légers — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
    ("orebro_13",
     "Travail ou études — dans quelle mesure la douleur affecte-t-elle votre capacité ?",
     "0 = pas d'effet  ·  10 = incapable de faire"),
]

# Items à inverser pour le scoring (5, 6, 7 : plus = mieux → on inverse)
OREBRO_INBLEUED = {"orebro_5", "orebro_6", "orebro_7"}

OREBRO_KEYS = [o[0] for o in OREBRO_ITEMS]


def compute_orebro(answers: dict) -> dict:
    """answers = {"orebro_1": 6, "orebro_2": 4, ...} (0–10)"""
    total = 0
    count = 0
    for key, _, _ in OREBRO_ITEMS:
        v = answers.get(key)
        if v is not None:
            score = int(v)
            if key in OREBRO_INBLEUED:
                score = 10 - score
            total += score
            count += 1
    if count == 0:
        return {"score": None, "interpretation": "", "color": "#888"}
    # Normalisation sur 100
    pct = round(total / (count * 10) * 100)
    if pct <= 50:
        interp, color = "Risque faible de chronicisation (≤ 50)", "#388e3c"
    elif pct <= 74:
        interp, color = "Risque moyen de chronicisation (51–74)", "#f57c00"
    else:
        interp, color = "Risque élevé de chronicisation (≥ 75)", "#d32f2f"
    return {"score": pct, "interpretation": interp, "color": color, "raw": total}
