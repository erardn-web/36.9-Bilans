"""
Génération du rapport PDF d'évolution — Bilan Lombalgie
"""
import sys, os as _os
_here = _os.path.dirname(_os.path.abspath(__file__))
_root = _os.path.dirname(_here)
if _root not in sys.path: sys.path.insert(0, _root)


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

from pdf_theme import (
    TERRA, TERRA_LIGHT, BLEU, BLEU_LIGHT, GRIS, GRIS_BORD, GRIS_TEXTE,
    NOIR, BLANC, BLEU, ORANGE, ROUGE, JAUNE,
    USEFUL_W, MARGIN,
    make_header_footer, make_styles, make_table, section_band, make_cover,
    get_logo,
)
# Aliases
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
