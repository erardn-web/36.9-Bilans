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
    HRFlowable, PageBreak, KeepTogether, Image,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

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


def sf12_color(score):
    s = safe_num(score)
    if s is None: return GRIS_TEXTE
    if s >= 66:   return VERT
    if s >= 33:   return ORANGE
    return ROUGE


# ─── Utilitaires graphiques ───────────────────────────────────────────────────

CHART_COLORS = ["#1a3c5e", "#f57c00", "#388e3c", "#7b1fa2", "#d32f2f",
                "#0097a7", "#e64a19", "#5d4037"]

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
    synth_rows.append(synth_row("SF12 – Fonct. physique",    "sf12_pf"))
    synth_rows.append(synth_row("SF12 – Limit. physique",    "sf12_rp"))
    synth_rows.append(synth_row("SF12 – Douleur",            "sf12_bp"))
    synth_rows.append(synth_row("SF12 – Santé générale",     "sf12_gh"))
    synth_rows.append(synth_row("SF12 – Vitalité",           "sf12_vt"))
    synth_rows.append(synth_row("SF12 – Vie sociale",        "sf12_sf"))
    synth_rows.append(synth_row("SF12 – Limit. émotionnel",  "sf12_re"))
    synth_rows.append(synth_row("SF12 – Santé psychique",    "sf12_mh"))
    synth_rows.append([""] + [""] * n_bilans)
    synth_rows.append(synth_row("PCS-12 (score physique)",   "sf12_pcs"))
    synth_rows.append(synth_row("MCS-12 (score mental)",     "sf12_mcs"))
    synth_rows.append([""] + [""] * n_bilans)
    synth_rows.append(synth_row("HVT – Retour normal (min)", "hvt_duree_retour", " min"))
    synth_rows.append([""] + [""] * n_bilans)
    synth_rows.append(synth_row("Nijmegen (/64)",            "nij_score"))
    synth_rows.append(synth_row("ETCO₂ repos (mmHg)",        "etco2_repos"))
    synth_rows.append(synth_row("FR (cyc/min)",              "pattern_frequence"))
    synth_rows.append(synth_row("PImax % prédit",            "pimax_pct", "%"))
    synth_rows.append(synth_row("PEmax % prédit",            "pemax_pct", "%"))
    synth_rows.append(synth_row("MRC Dyspnée (grade)",       "mrc_score"))

    col_w = [6*cm] + [(w - 6*cm) / n_bilans] * n_bilans

    # Construire les commandes de style de base
    base_cmds = [
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANC, GRIS_CLAIR]),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND",  (0, 0), (-1, 0), BLEU_FONCE),
        ("TEXTCOLOR",   (0, 0), (-1, 0), BLANC),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
    ]

    # Coloriser les valeurs selon les seuils cliniques
    sf12_key_map = {
        "SF12 – Fonct. physique": "sf12_pf",
        "SF12 – Limit. physique": "sf12_rp",
        "SF12 – Douleur":         "sf12_bp",
        "SF12 – Santé générale":  "sf12_gh",
        "SF12 – Vitalité":        "sf12_vt",
        "SF12 – Vie sociale":     "sf12_sf",
        "SF12 – Limit. émotionnel": "sf12_re",
        "SF12 – Santé psychique": "sf12_mh",
    }
    had_key_map = {
        "HAD Anxiété (/21)":    "had_score_anxiete",
        "HAD Dépression (/21)": "had_score_depression",
    }

    offset = 1
    for i, row_data in enumerate(synth_rows):
        row_idx = i + offset
        label   = row_data[0] if row_data else ""
        for j in range(1, n_bilans + 1):
            bilan_row = bilans_df.iloc[j - 1]
            if label in had_key_map:
                c = had_color(bilan_row.get(had_key_map[label]))
            elif label == "BOLT (secondes)":
                c = bolt_color(bilan_row.get("bolt_score"))
            elif label in sf12_key_map:
                c = sf12_color(bilan_row.get(sf12_key_map[label]))
            else:
                continue
            if c != GRIS_TEXTE:
                base_cmds.append(("TEXTCOLOR", (j, row_idx), (j, row_idx), c))
                base_cmds.append(("FONTNAME",  (j, row_idx), (j, row_idx), "Helvetica-Bold"))

    synth_table = Table(synth_header + synth_rows, colWidths=col_w, repeatRows=1)
    synth_table.setStyle(TableStyle(base_cmds))
    story.append(synth_table)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Légende HAD : vert = normal (0–7) · orange = douteux (8–10) · rouge = pathologique (11–21)   |   "
        "BOLT : rouge < 10s · orange < 20s · jaune < 40s · vert ≥ 40s   |   "
        "SF12 : vert ≥ 66 · orange ≥ 33 · rouge < 33",
        styles["small"],
    ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  GRAPHIQUES D'ÉVOLUTION
    # ══════════════════════════════════════════════════════════════════
    story.append(Paragraph("Graphiques d'évolution", styles["section"]))
    story.append(Spacer(1, 0.3*cm))

    # HAD
    story.append(Paragraph("Anxiété & Dépression — HAD", styles["subsection"]))
    try:
        story.append(make_chart_had(bilans_df, labels))
    except Exception:
        story.append(Paragraph("Graphique non disponible.", styles["small"]))
    story.append(Spacer(1, 0.5*cm))

    # BOLT
    story.append(Paragraph("BOLT — Body Oxygen Level Test", styles["subsection"]))
    try:
        story.append(make_chart_bolt(bilans_df, labels))
    except Exception:
        story.append(Paragraph("Graphique non disponible.", styles["small"]))
    story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # SF-12 barres
    story.append(Paragraph("SF-12 — Évolution par dimension", styles["subsection"]))
    try:
        story.append(make_chart_sf12_bars(bilans_df, labels))
    except Exception:
        story.append(Paragraph("Graphique non disponible.", styles["small"]))
    story.append(Spacer(1, 0.5*cm))

    # SF-12 radar (si >= 2 bilans)
    if n_bilans >= 2:
        story.append(Paragraph("SF-12 — Comparaison radar", styles["subsection"]))
        try:
            story.append(make_chart_sf12_radar(bilans_df, labels))
        except Exception:
            story.append(Paragraph("Graphique non disponible.", styles["small"]))
        story.append(Spacer(1, 0.5*cm))

    # HVT
    try:
        hvt_img = make_chart_hvt(bilans_df, labels)
        if hvt_img:
            story.append(Paragraph("Test HV — Durée de retour à la normale", styles["subsection"]))
            story.append(hvt_img)
    except Exception:
        pass

    # Nijmegen
    nij_vals = [safe_num(r.get("nij_score")) for _, r in bilans_df.iterrows()]
    if any(nij_vals):
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Score de Nijmegen", styles["subsection"]))
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig_n, ax_n = plt.subplots(figsize=(10, 3.5))
            x_n = range(len(labels))
            bar_cols_n = []
            for v in nij_vals:
                if v is None:   bar_cols_n.append("#cccccc")
                elif v >= 23:   bar_cols_n.append("#d32f2f")
                elif v >= 15:   bar_cols_n.append("#f57c00")
                else:           bar_cols_n.append("#388e3c")
            bars_n = ax_n.bar(x_n, [v or 0 for v in nij_vals], color=bar_cols_n, width=0.5)
            for bar, v in zip(bars_n, nij_vals):
                if v:
                    ax_n.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                              str(int(v)), ha="center", fontsize=10, fontweight="bold")
            import numpy as np2
            ax_n.axhline(23, color="#d32f2f", linestyle="--", linewidth=1.5, label="Seuil 23 (SHV+)")
            ax_n.axhline(15, color="#f57c00", linestyle="--", linewidth=1.5, label="Seuil 15 (borderline)")
            xlbls_n = [l.split("—")[0].strip() for l in labels]
            ax_n.set_xticks(list(x_n)); ax_n.set_xticklabels(xlbls_n, rotation=15, ha="right")
            ax_n.set_ylim(0, 68); ax_n.set_ylabel("Score /64")
            ax_n.set_title("Évolution Nijmegen", fontsize=12, fontweight="bold",
                           color="#1a3c5e", pad=10)
            ax_n.legend(fontsize=8); ax_n.spines[["top","right"]].set_visible(False)
            ax_n.set_facecolor("white"); fig_n.tight_layout()
            buf_n = io.BytesIO()
            fig_n.savefig(buf_n, format="png", dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig_n); buf_n.seek(0)
            story.append(Image(buf_n, width=17*cm, height=6*cm))
        except Exception:
            pass

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

        # ── SF-12 ───────────────────────────────────────────────────
        story.append(Paragraph("SF-12 — Qualité de vie", styles["subsection"]))
        sf_dims = [
            ("Fonctionnement physique",       "sf12_pf"),
            ("Limitations physiques",          "sf12_rp"),
            ("Douleur physique",               "sf12_bp"),
            ("Santé générale",                 "sf12_gh"),
            ("Vitalité",                       "sf12_vt"),
            ("Vie et relations sociales",      "sf12_sf"),
            ("Limitations émotionnelles",      "sf12_re"),
            ("Santé psychique",                "sf12_mh"),
        ]
        sf_header = [["Dimension", "Score /100"]]
        sf_rows   = [[label, val_str(row.get(key))] for label, key in sf_dims]
        # Scores composites
        sf_rows.append(["── Scores composites ──", ""])
        pcs_val = val_str(row.get("sf12_pcs"))
        mcs_val = val_str(row.get("sf12_mcs"))
        sf_rows.append([f"PCS-12 — Score composite physique", f"{pcs_val}  (réf. 50)"])
        sf_rows.append([f"MCS-12 — Score composite mental",   f"{mcs_val}  (réf. 50)"])
        t = make_table(sf_header + sf_rows, col_widths=[10*cm, w - 10*cm])
        story.append(t)

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

        # ── Nijmegen ─────────────────────────────────────────────────────────
        nij_score = val_str(row.get("nij_score"))
        if nij_score != "—":
            story.append(Paragraph("Questionnaire de Nijmegen", styles["subsection"]))
            nij_data = [
                ["Score Nijmegen", "Interprétation"],
                [f"{nij_score} / 64", str(row.get("nij_interpretation","—") or "—")],
            ]
            story.append(make_table(nij_data, col_widths=[4*cm, w - 4*cm]))

        # ── Capnographie ─────────────────────────────────────────────────────
        etco2_r = val_str(row.get("etco2_repos"))
        if etco2_r != "—":
            story.append(Paragraph("Capnographie — ETCO₂", styles["subsection"]))
            etco2_data = [
                ["Paramètre", "Valeur"],
                ["ETCO₂ repos (mmHg)",       etco2_r],
                ["ETCO₂ post-effort (mmHg)", val_str(row.get("etco2_post_effort"))],
                ["Pattern",                  str(row.get("etco2_pattern","—") or "—")],
            ]
            if row.get("etco2_notes"):
                etco2_data.append(["Notes", str(row["etco2_notes"])])
            story.append(make_table(etco2_data, col_widths=[6*cm, w - 6*cm]))

        # ── Pattern respiratoire ─────────────────────────────────────────────
        pat_freq = val_str(row.get("pattern_frequence"))
        if pat_freq != "—":
            story.append(Paragraph("Pattern respiratoire", styles["subsection"]))
            pat_data = [
                ["Paramètre", "Valeur"],
                ["Fréquence (cyc/min)", pat_freq],
                ["Mode",      str(row.get("pattern_mode","—")     or "—")],
                ["Amplitude", str(row.get("pattern_amplitude","—")or "—")],
                ["Rythme",    str(row.get("pattern_rythme","—")   or "—")],
                ["Paradoxal", str(row.get("pattern_paradoxal","—")or "—")],
            ]
            if row.get("pattern_notes"):
                pat_data.append(["Notes", str(row["pattern_notes"])])
            story.append(make_table(pat_data, col_widths=[5*cm, w - 5*cm]))

        # ── Gazométrie ───────────────────────────────────────────────────────
        if row.get("gazo_ph"):
            story.append(Paragraph("Gazométrie", styles["subsection"]))
            gazo_data = [
                ["Paramètre", "Valeur", "Référence"],
                ["Type",          str(row.get("gazo_type","—") or "—"),  ""],
                ["pH",            val_str(row.get("gazo_ph")),           "7.35–7.45"],
                ["PaCO₂ (mmHg)",  val_str(row.get("gazo_paco2")),        "35–45"],
                ["PaO₂ (mmHg)",   val_str(row.get("gazo_pao2")),         "75–100"],
                ["HCO₃⁻ (mmol/L)",val_str(row.get("gazo_hco3")),         "22–26"],
                ["SatO₂ (%)",     val_str(row.get("gazo_sato2")),        "≥ 95"],
            ]
            story.append(make_table(gazo_data, col_widths=[5*cm, 4*cm, w - 9*cm]))

        # ── SNIF / PImax / PEmax ─────────────────────────────────────────────
        if row.get("pimax_val") or row.get("snif_val"):
            story.append(Paragraph("SNIF · PImax · PEmax", styles["subsection"]))
            musc_data = [
                ["Test", "Mesuré (cmH₂O)", "Prédit (cmH₂O)", "% prédit"],
                ["SNIF",  val_str(row.get("snif_val")),
                          val_str(row.get("snif_pred")),  val_str(row.get("snif_pct"),"%")],
                ["PImax", val_str(row.get("pimax_val")),
                          val_str(row.get("pimax_pred")), val_str(row.get("pimax_pct"),"%")],
                ["PEmax", val_str(row.get("pemax_val")),
                          val_str(row.get("pemax_pred")), val_str(row.get("pemax_pct"),"%")],
            ]
            story.append(make_table(musc_data,
                         col_widths=[3*cm, (w-3*cm)/3, (w-3*cm)/3, (w-3*cm)/3]))

        # ── MRC ──────────────────────────────────────────────────────────────
        mrc_val = row.get("mrc_score")
        if mrc_val is not None and str(mrc_val) != "":
            story.append(Paragraph("Échelle MRC Dyspnée", styles["subsection"]))
            mrc_labels = ["0 — Pas de dyspnée sauf effort intense",
                          "1 — Dyspnée à la montée rapide",
                          "2 — Marche plus lentement que les autres",
                          "3 — S'arrête après 100 m à plat",
                          "4 — Trop essoufflé pour quitter la maison"]
            try:
                mrc_label = mrc_labels[int(mrc_val)]
            except (IndexError, ValueError):
                mrc_label = str(mrc_val)
            story.append(make_table([["Grade MRC", mrc_label]],
                                    col_widths=[3*cm, w - 3*cm]))

        # ── Comorbidités ─────────────────────────────────────────────────────
        comorb = str(row.get("comorb_list","") or "").replace("|", " · ")
        trait  = str(row.get("comorb_traitements","") or "").replace("|", " · ")
        if comorb or trait:
            story.append(Paragraph("Comorbidités & traitements", styles["subsection"]))
            cm_rows = []
            if comorb:
                cm_rows.append(["Comorbidités", comorb])
            if trait:
                cm_rows.append(["Traitements",  trait])
            if row.get("comorb_notes"):
                cm_rows.append(["Notes", str(row["comorb_notes"])])
            story.append(make_table(cm_rows, col_widths=[4*cm, w - 4*cm]))

        if i < n_bilans - 1:
            story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    #  BUILD
    # ══════════════════════════════════════════════════════════════════
    doc.build(story, onFirstPage=make_header_footer, onLaterPages=make_header_footer)
    return buffer.getvalue()
