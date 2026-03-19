"""
Génération du rapport PDF d'évolution — Bilan Lombalgie
"""

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

# ─── Couleurs ─────────────────────────────────────────────────────────────────
VERT        = colors.HexColor("#2e5a1c")
VERT_CLAIR  = colors.HexColor("#e8f5e0")
GRIS_CLAIR  = colors.HexColor("#f5f5f5")
GRIS_BORD   = colors.HexColor("#cccccc")
BLANC       = colors.white
NOIR        = colors.HexColor("#222222")
ROUGE       = colors.HexColor("#d32f2f")
ORANGE      = colors.HexColor("#f57c00")
W = A4[0] - 3*cm


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
def make_styles():
    base = getSampleStyleSheet()
    return {
        "title":      ParagraphStyle("t", fontSize=20, fontName="Helvetica-Bold",
                                     textColor=VERT, alignment=TA_CENTER, spaceAfter=4),
        "subtitle":   ParagraphStyle("s", fontSize=10, fontName="Helvetica",
                                     textColor=colors.HexColor("#555"), alignment=TA_CENTER),
        "section":    ParagraphStyle("sec", fontSize=12, fontName="Helvetica-Bold",
                                     textColor=BLANC),
        "subsection": ParagraphStyle("sub", fontSize=10, fontName="Helvetica-Bold",
                                     textColor=VERT, spaceBefore=8, spaceAfter=4),
        "normal":     ParagraphStyle("n", fontSize=9, fontName="Helvetica",
                                     textColor=NOIR, spaceAfter=2),
        "small":      ParagraphStyle("sm", fontSize=8, fontName="Helvetica",
                                     textColor=colors.HexColor("#666")),
        "note":       ParagraphStyle("nt", fontSize=8, fontName="Helvetica",
                                     textColor=colors.HexColor("#444"), leftIndent=8),
    }


def section_header(title):
    tbl = Table([[Paragraph(title, ParagraphStyle("th", fontSize=12,
        fontName="Helvetica-Bold", textColor=BLANC))]], colWidths=[W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), VERT),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ]))
    return tbl


def make_table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS_CLAIR]),
        ("GRID",          (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("BACKGROUND",    (0,0),(-1,0),  VERT),
        ("TEXTCOLOR",     (0,0),(-1,0),  BLANC),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
    ]))
    return t


def make_hf(patient_info):
    nom = f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else ""
    def hf(c, doc):
        c.saveState()
        w, h = A4
        c.setFillColor(VERT); c.rect(0, h-1.1*cm, w, 1.1*cm, fill=1, stroke=0)
        c.setFillColor(BLANC); c.setFont("Helvetica-Bold", 9)
        c.drawString(1.5*cm, h-0.75*cm, "36.9 Bilans — Rapport Lombalgie")
        if nom.strip():
            c.setFont("Helvetica", 9)
            c.drawCentredString(w/2, h-0.75*cm, f"Patient : {nom}")
        c.setFont("Helvetica", 8)
        c.drawRightString(w-1.5*cm, h-0.75*cm, f"Page {doc.page}")
        c.setStrokeColor(GRIS_BORD); c.setLineWidth(0.5)
        c.line(1.5*cm, 1.1*cm, w-1.5*cm, 1.1*cm)
        c.setFillColor(colors.HexColor("#888")); c.setFont("Helvetica", 7)
        c.drawString(1.5*cm, 0.6*cm, "Document confidentiel — usage médical")
        c.drawRightString(w-1.5*cm, 0.6*cm, f"Généré le {date.today().strftime('%d/%m/%Y')}")
        c.restoreState()
    return hf


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

    # ── Page de garde ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Rapport d'évolution — Lombalgie", styles["title"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=VERT))
    story.append(Spacer(1, 0.4*cm))

    pat_rows = [
        ["Patient",          f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"],
        ["Date de naissance",str(patient_info.get("date_naissance","—"))],
        ["Sexe",             patient_info.get("sexe","—")],
        ["Profession",       patient_info.get("profession","—") or "—"],
        ["Nombre de bilans", str(n)],
        ["Rapport généré le",date.today().strftime("%d/%m/%Y")],
    ]
    pt = Table(pat_rows, colWidths=[5*cm, W-5*cm])
    pt.setStyle(TableStyle([
        ("FONTNAME",  (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (1,0),(1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0),(-1,-1), 9),
        ("TEXTCOLOR", (0,0),(0,-1),  VERT),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[BLANC, GRIS_CLAIR]),
        ("GRID",      (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",(0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.5*cm))

    # Liste des bilans
    story.append(Paragraph("Bilans inclus", styles["subsection"]))
    bil_rows = [["#","Date","Type","Groupe","Praticien"]]
    for i, (_, row) in enumerate(bilans_df.iterrows()):
        d = row["date_bilan"]
        ds = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        bil_rows.append([str(i+1), ds, row.get("type_bilan","—"),
                         row.get("groupe_clinique","—") or "—",
                         row.get("praticien","—") or "—"])
    story.append(make_table(bil_rows, col_widths=[1*cm,3*cm,5*cm,3*cm,W-12*cm]))
    story.append(PageBreak())

    # ── Tableau de synthèse ───────────────────────────────────────────────────
    story.append(section_header("Synthèse des scores"))
    story.append(Spacer(1, 0.2*cm))

    col_w = [6*cm] + [(W-6*cm)/n]*n
    synth_header = [["Indicateur"] + [f"B{i+1}" for i in range(n)]]
    synth_rows = []

    def srow(label, key, suffix=""):
        return [label] + [val_s(r.get(key), suffix) for _, r in bilans_df.iterrows()]

    synth_rows += [
        srow("EVA Repos (/10)",     "s_eva_repos"),
        srow("EVA Mouvement (/10)", "s_eva_mouvement"),
        srow("EVA Nuit (/10)",      "s_eva_nuit"),
        ["Groupe clinique"] + [r.get("groupe_clinique","—") or "—" for _, r in bilans_df.iterrows()],
        [""] + [""]*n,
        srow("ODI (%)",             "odi_score",   "%"),
        srow("Tampa (/68)",         "tampa_score"),
        srow("Örebro",              "orebro_score"),
        [""] + [""]*n,
        srow("Luomajoki (/6 échecs)","o_luomajoki_score"),
        srow("Schober (cm)",        "o_schober",   " cm"),
        srow("Extension",           "o_extension_mob"),
        srow("Latéroflexion Droite","o_lat_droite_mob"),
        srow("Latéroflexion Gauche","o_lat_gauche_mob"),
        srow("Rotation Droite",     "o_rot_droite_mob"),
        srow("Rotation Gauche",     "o_rot_gauche_mob"),
        [""] + [""]*n,
        ["Arrêt travail"] + [r.get("s_arret_travail","—") or "—" for _, r in bilans_df.iterrows()],
        ["Réveil nocturne"] + [r.get("s_reveil_nuit","—") or "—" for _, r in bilans_df.iterrows()],
        ["Drapeaux rouges (nb)"] + [
            str(len([x for x in str(r.get("drapeaux_rouges_list","")).split("|") if x]))
            for _, r in bilans_df.iterrows()],
        ["Drapeaux jaunes (nb)"] + [
            str(len([x for x in str(r.get("drapeaux_jaunes_list","")).split("|") if x]))
            for _, r in bilans_df.iterrows()],
    ]

    synth_tbl = make_table(synth_header + synth_rows, col_widths=col_w)
    story.append(synth_tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "ODI : 0–20% minimal · 21–40% modéré · 41–60% sévère · >60% très sévère  |  "
        "Tampa : ≤37 faible · 38–44 modéré · >44 élevé  |  "
        "Örebro : ≤50 faible · 51–74 moyen · ≥75 élevé  |  "
        "Luomajoki : ≥3 échecs = dysfonction significative",
        styles["small"]))
    story.append(PageBreak())

    # ── Graphiques ────────────────────────────────────────────────────────────
    story.append(section_header("Graphiques d'évolution"))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("EVA — Douleur", styles["subsection"]))
    try: story.append(chart_eva(bilans_df, labels))
    except: story.append(Paragraph("Graphique non disponible.", styles["small"]))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Questionnaires fonctionnels", styles["subsection"]))
    try: story.append(chart_questionnaires(bilans_df, labels))
    except: story.append(Paragraph("Graphique non disponible.", styles["small"]))

    story.append(PageBreak())

    story.append(Paragraph("Mobilité lombaire", styles["subsection"]))
    try: story.append(chart_mobilite(bilans_df, labels))
    except: story.append(Paragraph("Graphique non disponible.", styles["small"]))

    story.append(Spacer(1, 0.5*cm))
    luom_img = None
    try: luom_img = chart_luomajoki(bilans_df, labels)
    except: pass
    if luom_img:
        story.append(Paragraph("Tests de Luomajoki", styles["subsection"]))
        story.append(luom_img)

    story.append(PageBreak())

    # ── Détail bilan par bilan ────────────────────────────────────────────────
    story.append(section_header("Détail des bilans"))
    for i, (_, row) in enumerate(bilans_df.iterrows()):
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"Bilan {i+1} — {labels[i]}", styles["subsection"]))

        groupe = row.get("groupe_clinique","—") or "—"
        story.append(Paragraph(f"Groupe clinique : {groupe}", styles["normal"]))

        # Subjectif
        story.append(Paragraph("Subjectif", ParagraphStyle("sh", fontSize=9,
            fontName="Helvetica-Bold", textColor=VERT, spaceBefore=6, spaceAfter=2)))
        s_rows = [["Paramètre","Valeur"]]
        for lbl, key in [
            ("Motif",          "s_motif_consultation"),
            ("Localisation",   "s_douleur_localisation"),
            ("Type douleur",   "s_type_douleur"),
            ("EVA repos",      "s_eva_repos"),
            ("EVA mouvement",  "s_eva_mouvement"),
            ("EVA nuit",       "s_eva_nuit"),
            ("Arrêt travail",  "s_arret_travail"),
            ("Réveil nocturne","s_reveil_nuit"),
            ("Antécédents",    "s_antecedents"),
            ("Traitements",    "s_traitements_en_cours"),
        ]:
            v = str(row.get(key,"") or "—").replace("|"," · ")
            if v and v != "—":
                s_rows.append([lbl, v])
        if len(s_rows) > 1:
            story.append(make_table(s_rows, col_widths=[4.5*cm, W-4.5*cm]))

        # Objectif scores
        story.append(Paragraph("Objectif — Scores", ParagraphStyle("sh2", fontSize=9,
            fontName="Helvetica-Bold", textColor=VERT, spaceBefore=6, spaceAfter=2)))
        o_rows = [["Test","Score","Interprétation"]]
        for lbl, sk, ik in [
            ("ODI",   "odi_score",    "odi_interpretation"),
            ("Tampa", "tampa_score",  "tampa_interpretation"),
            ("Örebro","orebro_score", "orebro_interpretation"),
        ]:
            if row.get(sk):
                o_rows.append([lbl, val_s(row.get(sk)), str(row.get(ik,"—") or "—")])
        if row.get("o_luomajoki_score"):
            o_rows.append(["Luomajoki", f"{val_s(row.get('o_luomajoki_score'))}/6 échecs",
                           "Significatif" if safe_n(row.get("o_luomajoki_score","0")) and
                           safe_n(row.get("o_luomajoki_score","0")) >= 3 else "Non significatif"])
        if len(o_rows) > 1:
            story.append(make_table(o_rows, col_widths=[3*cm,3*cm,W-6*cm]))

        # Appréciation + Plan
        if row.get("a_appreciation"):
            story.append(Paragraph("Appréciation", ParagraphStyle("sh3", fontSize=9,
                fontName="Helvetica-Bold", textColor=VERT, spaceBefore=6, spaceAfter=2)))
            story.append(Paragraph(str(row["a_appreciation"]), styles["note"]))
        if row.get("p_objectifs") or row.get("p_traitement"):
            story.append(Paragraph("Plan", ParagraphStyle("sh4", fontSize=9,
                fontName="Helvetica-Bold", textColor=VERT, spaceBefore=6, spaceAfter=2)))
            p_rows = [["Paramètre","Contenu"]]
            for lbl, key in [("Objectifs","p_objectifs"),("Traitement","p_traitement"),
                              ("Fréquence","p_frequence"),("Durée","p_duree")]:
                if row.get(key):
                    p_rows.append([lbl, str(row[key])])
            if len(p_rows) > 1:
                story.append(make_table(p_rows, col_widths=[3.5*cm, W-3.5*cm]))

        # Drapeaux
        dr = [x for x in str(row.get("drapeaux_rouges_list","")).split("|") if x]
        dj = [x for x in str(row.get("drapeaux_jaunes_list","")).split("|") if x]
        if dr or dj:
            flag_rows = [["Type","Facteurs détectés"]]
            if dr: flag_rows.append(["🔴 Rouges", " · ".join(dr)])
            if dj: flag_rows.append(["🟡 Jaunes",  " · ".join(dj)])
            story.append(Paragraph("Drapeaux", ParagraphStyle("sh5", fontSize=9,
                fontName="Helvetica-Bold", textColor=VERT, spaceBefore=6, spaceAfter=2)))
            story.append(make_table(flag_rows, col_widths=[3*cm, W-3*cm]))

        if i < n - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=make_hf(patient_info), onLaterPages=make_hf(patient_info))
    return buffer.getvalue()
