"""
Génération du rapport PDF d'évolution — Bilan Lombalgie
"""

import os as _os
from reportlab.lib import colors as _colors
from reportlab.lib.pagesizes import A4 as _A4
from reportlab.lib.units import cm as _cm
from reportlab.lib.enums import TA_CENTER as _TA_CENTER
from reportlab.lib.styles import ParagraphStyle as _PS
from reportlab.platypus import Table as _Table, TableStyle as _TableStyle, Paragraph as _Para, Image as _Image

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
        # Bandeau bleu
        canvas.setFillColor(BLEU)
        canvas.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)
        # Accent terracotta droite
        canvas.setFillColor(TERRA)
        canvas.rect(w - 5*_cm, h - HEADER_H, 5*_cm, HEADER_H, fill=1, stroke=0)
        # Logo
        logo_p = _find_logo()
        if logo_p:
            try:
                canvas.drawImage(logo_p, MARGIN, h - HEADER_H + 0.15*_cm,
                    width=2.8*_cm, height=HEADER_H - 0.3*_cm,
                    preserveAspectRatio=True, mask="auto")
            except Exception:
                pass
        # Titre
        canvas.setFillColor(BLANC)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(w/2, h - HEADER_H*0.65, report_title)
        # Patient
        if patient_name:
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(w - MARGIN, h - HEADER_H*0.65, patient_name)
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
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    hf     = make_hf(patient_info)

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
