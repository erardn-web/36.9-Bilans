"""
equilibre_pdf.py — Génération PDF Équilibre / Gériatrie
"""
import io
import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable,
)

from reportlab.platypus import Flowable as _FlowableEQ

class Checkbox(_FlowableEQ):
    """Case à cocher dessinée."""
    def __init__(self, size=8):
        _FlowableEQ.__init__(self)
        self.size = size; self.width = size + 4; self.height = size
    def draw(self):
        self.canv.setStrokeColor(colors.HexColor("#333"))
        self.canv.setLineWidth(0.7)
        self.canv.rect(1, 0, self.size, self.size, fill=0, stroke=1)


# ── Thème ──────────────────────────────────────────────────────────────────────
TERRA = colors.HexColor("#C4603A"); BLEU = colors.HexColor("#2B57A7")
GRIS  = colors.HexColor("#F4F4F4"); GRIS_BORD = colors.HexColor("#DEDEDE")
GRIS_TEXTE = colors.HexColor("#555555"); BLANC = colors.white
NOIR  = colors.HexColor("#1A1A1A"); BLEU_LIGHT = colors.HexColor("#E8EEF9")
VERT  = colors.HexColor("#388e3c"); ORANGE = colors.HexColor("#f57c00")
ROUGE = colors.HexColor("#d32f2f")

W = A4[0] - 3*cm; USEFUL_W=W; MARGIN = 1.5*cm; HEADER_H = 1.5*cm

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_369.png")

def _find_logo():
    for p in [LOGO_PATH, "assets/logo_369.png", "/mount/src/36.9-bilans/assets/logo_369.png"]:
        if os.path.exists(p): return p
    return None

def _make_hf(patient_name=""):
    def _draw(canvas, doc):
        canvas.saveState()
        w, h = A4
        logo = _find_logo()
        if logo:
            try: canvas.drawImage(logo, MARGIN, h-1.4*cm, width=2.6*cm, height=1.0*cm,
                                  preserveAspectRatio=True, mask="auto")
            except: pass
        canvas.setFillColor(GRIS_TEXTE); canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(w/2, h-1.1*cm, "36.9 Bilans — Rapport Équilibre / Gériatrie")
        if patient_name:
            canvas.setFillColor(BLEU); canvas.setFont("Helvetica-Bold", 8)
            canvas.drawRightString(w-MARGIN, h-1.1*cm, patient_name)
        canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(0.5)
        canvas.line(MARGIN, h-1.5*cm, w-MARGIN, h-1.5*cm)
        canvas.line(MARGIN, 0.9*cm, w-MARGIN, 0.9*cm)
        canvas.setFillColor(GRIS_TEXTE); canvas.setFont("Helvetica", 7)
        canvas.drawString(MARGIN, 0.35*cm, "Document confidentiel — Usage médical")
        canvas.drawCentredString(w/2, 0.35*cm, "36.9 Bilans")
        canvas.drawRightString(w-MARGIN, 0.35*cm, f"Page {doc.page}  ·  {date.today().strftime('%d/%m/%Y')}")
        canvas.restoreState()
    return _draw

def _styles():
    return {
        "title": ParagraphStyle("eq_title", fontSize=22, fontName="Helvetica-Bold",
            textColor=BLEU, alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle("eq_sub", fontSize=11, fontName="Helvetica",
            textColor=GRIS_TEXTE, alignment=TA_CENTER, spaceAfter=4),
        "section": ParagraphStyle("eq_sec", fontSize=10, fontName="Helvetica-Bold",
            textColor=BLANC, backColor=BLEU, spaceBefore=10, spaceAfter=5,
            leftIndent=-6, rightIndent=-6, borderPadding=(5,8,5,8)),
        "subsection": ParagraphStyle("eq_subsec", fontSize=10, fontName="Helvetica-Bold",
            textColor=TERRA, spaceBefore=8, spaceAfter=4),
        "normal": ParagraphStyle("eq_norm", fontSize=9, fontName="Helvetica",
            textColor=NOIR, spaceAfter=2),
        "small": ParagraphStyle("eq_sm", fontSize=7.5, fontName="Helvetica", textColor=GRIS_TEXTE),
        "intro":    ParagraphStyle("eq_intro", fontSize=9, fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#444"), spaceAfter=6, leftIndent=4),
        "question": ParagraphStyle("eq_question", fontSize=10, fontName="Helvetica-Bold",
            textColor=NOIR, spaceBefore=8, spaceAfter=3, leftIndent=4),
        "option":   ParagraphStyle("eq_option", fontSize=9, fontName="Helvetica",
            textColor=NOIR, spaceAfter=2, leftIndent=20),
    }

# Alias pour les builders partagés
def section_band(title):
    return _section(title)

def _section(title):
    row = [[Paragraph(f"<font color='#C4603A'>▌</font>&nbsp;&nbsp;<b>{title}</b>",
        ParagraphStyle("eq_sh", fontSize=10, fontName="Helvetica-Bold", textColor=BLANC, leading=14))]]
    t = Table(row, colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10)]))
    return t

def _make_table(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),8),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ROWBACKGROUNDS",(0,1),(-1,-1),[BLANC,GRIS]),
            ("LINEBELOW",(0,0),(-1,-1),0.3,GRIS_BORD),("TOPPADDING",(0,0),(-1,-1),5),
            ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),7)]
    if header:
        cmds += [("BACKGROUND",(0,0),(-1,0), BLEU_LIGHT),("TEXTCOLOR", (0,0),(-1,0), BLEU),
            ("LINEBELOW",(0,0),(-1,0), 1.0, BLEU),
                 ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
                 ("TOPPADDING",(0,0),(-1,0),7),("BOTTOMPADDING",(0,0),(-1,0),7)]
    t.setStyle(TableStyle(cmds)); return t

def _safe_n(v):
    try: r=float(v); return r if r!=0 else None
    except: return None

def _val(v, suffix=""):
    n=_safe_n(v)
    if n is None: return "—"
    return f"{int(n)}{suffix}" if n==int(n) else f"{n}{suffix}"



def build_muscle(story, styles, with_legpress=True):
    """Fiche testing musculaire MI imprimable."""
    from utils.muscle_data import MUSCLE_GROUPS, MMT_SCALE
    story.append(_section("Testing musculaire — Membres inférieurs"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Échelle MRC 0–5 : 0 = aucune contraction · 1 = contraction sans mouvement · "
        "2 = mouvement sans gravité · 3 = contre gravité · 4 = contre résistance partielle · "
        "5 = normal",
        ParagraphStyle("mmt_leg", fontSize=8, fontName="Helvetica-Oblique",
                       textColor=GRIS_TEXTE, spaceAfter=6)))
    story.append(Spacer(1, 0.2*cm))



    def score_box():
        return Table([[Checkbox(8)] + [
            Paragraph(str(s), ParagraphStyle("sc", fontSize=7, fontName="Helvetica",
                      textColor=NOIR, alignment=1)) for s,_ in MMT_SCALE]],
            colWidths=[0.5*cm] + [1.0*cm]*6)

    header = [["Groupe musculaire", "Innervation",
               "Droit (0–5)", "", "Gauche (0–5)", ""]]
    rows = []
    for key, label, innervation in MUSCLE_GROUPS:
        row = [
            Paragraph(f"<b>{label}</b>", ParagraphStyle(
                "ml", fontSize=8, fontName="Helvetica-Bold", textColor=BLEU, leading=11)),
            Paragraph(innervation, ParagraphStyle(
                "mi", fontSize=7, fontName="Helvetica", textColor=GRIS_TEXTE, leading=10)),
            Paragraph("D : ______", ParagraphStyle(
                "ms", fontSize=9, fontName="Helvetica", textColor=NOIR)),
            Paragraph("", ParagraphStyle("_", fontSize=7)),
            Paragraph("G : ______", ParagraphStyle(
                "ms2", fontSize=9, fontName="Helvetica", textColor=NOIR)),
            Paragraph("", ParagraphStyle("_2", fontSize=7)),
        ]
        rows.append(row)

    col_w = [4.5*cm, 3*cm, 1.5*cm, 2.5*cm, 1.5*cm, W-13*cm]
    tbl = Table(header + rows, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  8),
        ("BACKGROUND",(0,0),(-1,0), BLEU_LIGHT),
        ("TEXTCOLOR", (0,0),(-1,0), BLEU),
            ("LINEBELOW",(0,0),(-1,0), 1.0, BLEU),
        ("ALIGN",         (2,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("SPAN",          (2,0),(3,0)),
        ("SPAN",          (4,0),(5,0)),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    # Score total
    score_tbl = Table([[
        Paragraph("Score total MMT :", ParagraphStyle(
            "st_l", fontSize=10, fontName="Helvetica-Bold", textColor=NOIR)),
        Paragraph("_______ / 80", ParagraphStyle(
            "st_v", fontSize=10, fontName="Helvetica", textColor=NOIR)),
        Paragraph("(0–40 sévère · 40–60 modéré · 60–80 normal)", ParagraphStyle(
            "st_n", fontSize=8, fontName="Helvetica-Oblique", textColor=GRIS_TEXTE)),
    ]], colWidths=[4*cm, 3*cm, W-7*cm])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), BLEU_LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(score_tbl)

    if with_legpress:
        story.append(Spacer(1, 0.6*cm))
        story.append(Paragraph("🏋️ 1RM Leg Press",
            ParagraphStyle("lp_t", fontSize=11, fontName="Helvetica-Bold",
                           textColor=TERRA, spaceBefore=4, spaceAfter=6)))
        lp_rows = [
            ["Charge 1RM (kg)", "_______ kg",
             "Protocole", "______________________"],
            ["Notes", "", "", ""],
        ]
        lp_tbl = Table(lp_rows, colWidths=[3*cm, 4*cm, 3*cm, W-10*cm])
        lp_tbl.setStyle(TableStyle([
            ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
            ("FONTNAME",      (2,0),(2,-1), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),(-1,-1), 9),
            ("ROWBACKGROUNDS",(0,0),(-1,-1), [BLANC, GRIS]),
            ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("SPAN",          (1,1),(3,1)),
        ]))
        story.append(lp_tbl)

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Observations :", ParagraphStyle(
        "obs", fontSize=9, fontName="Helvetica-Bold", textColor=NOIR)))
    story.append(Spacer(1, 0.2*cm))
    for _ in range(3):
        story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_BORD))
        story.append(Spacer(1, 0.4*cm))


def generate_pdf_equilibre(bilans_df, patient_info: dict, analyse_text: str = "") -> bytes:
    import pandas as pd
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=2.2*cm, bottomMargin=1.8*cm)

    styles = _styles()
    story  = []
    hf     = _make_hf(f"{patient_info.get('nom','')} {patient_info.get('prenom','')}")

    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)
    n = len(bilans_df)
    labels = [f"{r['date_bilan'].strftime('%d/%m/%Y')} — {r.get('type_bilan','')}"
              for _, r in bilans_df.iterrows()]
    short_lbl = [f"{r['date_bilan'].strftime('%d/%m/%y')}" for _, r in bilans_df.iterrows()]

    # ── Page de garde ──────────────────────────────────────────────────────────
    band = Table([[Paragraph("<font color='white'><b>Rapport d'évolution — Équilibre / Gériatrie</b></font>",
        ParagraphStyle("ct", fontSize=20, fontName="Helvetica-Bold", textColor=BLANC, alignment=TA_CENTER))]],
        colWidths=[W])
    band.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),18),("BOTTOMPADDING",(0,0),(-1,-1),18)]))
    sub = Table([[Paragraph("<font color='white'>Bilan physiothérapeutique</font>",
        ParagraphStyle("cs", fontSize=11, fontName="Helvetica", textColor=BLANC, alignment=TA_CENTER))]],
        colWidths=[W])
    sub.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),TERRA),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))

    story.append(Spacer(1, 0.8*cm))
    story.append(band); story.append(sub)
    story.append(Spacer(1, 0.5*cm))

    logo = _find_logo()
    if logo:
        lt = Table([[Image(logo, width=5*cm, height=2*cm, kind="proportional")]], colWidths=[W])
        lt.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")])); story.append(lt)
        story.append(Spacer(1, 0.4*cm))

    pat = [["Patient", f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"],
           ["Date de naissance", str(patient_info.get("date_naissance","—"))],
           ["Sexe", patient_info.get("sexe","—")],
           ["Nombre de bilans", str(n)],
           ["Généré le", date.today().strftime("%d/%m/%Y")]]
    pt = Table(pat, colWidths=[4.5*cm, W-4.5*cm])
    pt.setStyle(TableStyle([("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(1,0),(1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),9),
        ("TEXTCOLOR",(0,0),(0,-1),BLEU),("ROWBACKGROUNDS",(0,0),(-1,-1),[BLANC,BLEU_LIGHT]),
        ("LINEBELOW",(0,0),(-1,-1),0.3,GRIS_BORD),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10)]))
    story.append(pt)
    story.append(Spacer(1, 0.5*cm))

    bil = [["#","Date","Type","Praticien"]]
    for i,(_,row) in enumerate(bilans_df.iterrows()):
        d = row["date_bilan"]; ds = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        bil.append([str(i+1), ds, row.get("type_bilan","—") or "—", row.get("praticien","—") or "—"])
    story.append(_make_table(bil, col_widths=[1.2*cm,3.2*cm,5*cm,W-9.4*cm]))
    # ── Synthèse IA ───────────────────────────────────────────────────────────
    if analyse_text and str(analyse_text).strip():
        story.append(Spacer(1, 0.5*cm))
        story.append(_section("Synthèse physiothérapeutique"))
        story.append(Spacer(1, 0.3*cm))
        for para in str(analyse_text).strip().split("\n\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para,
                    ParagraphStyle("ai_cv2", fontSize=9.5, fontName="Helvetica",
                        textColor=NOIR, leading=14, spaceAfter=8)))
        story.append(Paragraph(
            f"Synthèse générée par IA le {date.today().strftime('%d/%m/%Y')} — À valider par le thérapeute.",
            ParagraphStyle("ai_cv2_foot", fontSize=7.5, fontName="Helvetica-Oblique",
                textColor=GRIS_TEXTE)))

    story.append(PageBreak())

    # ── Synthèse ───────────────────────────────────────────────────────────────
    story.append(_section("Synthèse des scores"))
    story.append(Spacer(1, 0.3*cm))
    col_w = [6*cm] + [(W-6*cm)/n]*n
    synth_hdr = [["Indicateur"] + [f"B{i+1}" for i in range(n)]]
    synth_rows = []
    def add_row(label, key, suffix=""):
        vals = [_val(r.get(key), suffix) for _,r in bilans_df.iterrows()]
        if any(v != "—" for v in vals):
            synth_rows.append([label] + vals)
    add_row("Tinetti total /28", "tinetti_total")
    add_row("Tinetti équilibre /16", "tinetti_eq_score")
    add_row("Tinetti marche /12", "tinetti_ma_score")
    add_row("STS 1 min (rép)", "sts_1min_reps")
    add_row("TUG (sec)", "tug_temps")
    add_row("Berg /56", "berg_score")
    add_row("SPPB /12", "sppb_score")
    add_row("Unipodal D ouvert (sec)", "unipodal_d_ouvert")
    add_row("Unipodal G ouvert (sec)", "unipodal_g_ouvert")
    if synth_rows:
        story.append(_make_table(synth_hdr + synth_rows, col_widths=col_w))
    story.append(PageBreak())

    # ── Graphiques ─────────────────────────────────────────────────────────────
    def fig_img(fig, w=16, h=5.5):
        b = io.BytesIO()
        fig.savefig(b, format="png", dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig); b.seek(0)
        return Image(b, width=w*cm, height=h*cm)

    charts = [
        ("Tinetti total /28", "tinetti_total", "#2B57A7"),
        ("Berg /56", "berg_score", "#C4603A"),
        ("SPPB /12", "sppb_score", "#388e3c"),
        ("TUG (sec)", "tug_temps", "#f57c00"),
        ("STS 1 min (rép)", "sts_1min_reps", "#7b1fa2"),
    ]
    has_chart = False
    for name, key, color in charts:
        vals = [_safe_n(r.get(key)) for _,r in bilans_df.iterrows()]
        if not any(v is not None for v in vals): continue
        if not has_chart:
            story.append(_section("Graphiques d'évolution"))
            story.append(Spacer(1, 0.3*cm))
            has_chart = True
        fig, ax = plt.subplots(figsize=(12, 4))
        xp=[i for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        ax.plot(xp, yp, "o-", color=color, lw=2.5, ms=9)
        for xi, yi in zip(xp, yp):
            ax.annotate(str(int(yi)) if yi==int(yi) else str(yi), (xi,yi),
                textcoords="offset points", xytext=(0,8), ha="center",
                fontsize=9, fontweight="bold", color=color)
        ax.set_xticks(range(len(short_lbl))); ax.set_xticklabels(short_lbl, rotation=15, ha="right")
        ax.set_title(name, fontsize=11, fontweight="bold", color="#2B57A7")
        ax.spines[["top","right"]].set_visible(False); ax.set_facecolor("white")
        ax.grid(axis="y", alpha=0.3); fig.tight_layout()
        story.append(Paragraph(name, styles["subsection"]))
        story.append(fig_img(fig)); story.append(Spacer(1, 0.4*cm))

    if has_chart: story.append(PageBreak())

    # ── Détail bilan par bilan ─────────────────────────────────────────────────
    story.append(_section("Détail des bilans"))
    for i, (_,row) in enumerate(bilans_df.iterrows()):
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"Bilan {i+1} — {labels[i]}", styles["subsection"]))
        detail = [["Test", "Résultat", "Interprétation"]]
        for lbl, key, ikey in [
            ("Tinetti total", "tinetti_total", "tinetti_interpretation"),
            ("STS 1 min", "sts_1min_reps", "sts_1min_interpretation"),
            ("TUG", "tug_temps", "tug_interpretation"),
            ("Berg", "berg_score", "berg_interpretation"),
            ("SPPB", "sppb_score", "sppb_interpretation"),
        ]:
            v = _val(row.get(key))
            if v != "—":
                detail.append([lbl, v, str(row.get(ikey,"—") or "—")])
        if len(detail) > 1:
            story.append(_make_table(detail, col_widths=[4*cm, 3*cm, W-7*cm]))
        if row.get("notes_generales"):
            story.append(Paragraph(f"Notes : {row['notes_generales']}", styles["normal"]))
        if i < n-1: story.append(PageBreak())



    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return buf.getvalue()


# ─── Questionnaire imprimable Testing MI + Leg Press ─────────────────────────

def _eq_section_band(title):
    row = [[_Para(f"<font color='#C4603A'>▌</font>&nbsp;&nbsp;<b>{title}</b>",
        _PS("eq_sh2", fontSize=10, fontName="Helvetica-Bold", textColor=BLANC, leading=14))]]
    t = _Table(row, colWidths=[W])
    t.setStyle(_TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10)]))
    return t

def build_muscle_eq(story, styles):
    """Fiche testing MI + Leg Press — Équilibre."""
    _build_mt_eq(story, styles, W, _eq_section_band, include_leg_press=True)

QUESTIONNAIRES_EQ = {
    "muscle": ("Testing musculaire MI + Leg Press", build_muscle_eq),
}

def generate_questionnaires_equilibre_pdf(selected, patient_info=None) -> bytes:
    """Génère les questionnaires imprimables Équilibre."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=2.2*cm, bottomMargin=1.8*cm)
    styles = _styles()
    story = []
    hf = _make_hf(f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else "")
    for i, key in enumerate(selected):
        if key in QUESTIONNAIRES_EQ:
            QUESTIONNAIRES_EQ[key][1](story, styles)
            if i < len(selected) - 1:
                story.append(PageBreak())
    if not story:
        return b""
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
#  Fiches imprimables
# ═══════════════════════════════════════════════════════════════════════════════

def _build_muscle_testing(story, styles):
    """Délègue à shv_pdf.build_muscle_testing."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.shv_pdf import build_muscle_testing
    build_muscle_testing(story, styles)

def _build_leg_press(story, styles):
    from utils.shv_pdf import build_leg_press
    build_leg_press(story, styles)


def build_tinetti(story, styles):
    """Grille Tinetti imprimable."""
    from utils.equilibre_data import TINETTI_EQUILIBRE, TINETTI_MARCHE, TINETTI_EQ_MAX, TINETTI_MA_MAX
    story.append(section_band("Tinetti — Performance Oriented Mobility Assessment (POMA)"))
    story.append(Spacer(1, 0.3*cm))

    for part_title, items, max_score in [
        ("Partie A — Équilibre (0–" + str(TINETTI_EQ_MAX) + ")", TINETTI_EQUILIBRE, TINETTI_EQ_MAX),
        ("Partie B — Marche (0–" + str(TINETTI_MA_MAX) + ")", TINETTI_MARCHE, TINETTI_MA_MAX),
    ]:
        story.append(Paragraph(part_title,
            ParagraphStyle("tin_pt",fontSize=10,fontName="Helvetica-Bold",
                textColor=TERRA,spaceBefore=8,spaceAfter=4)))
        header = [[
            Paragraph("<b>Item</b>", ParagraphStyle("th1",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC)),
            Paragraph("<b>Score</b>", ParagraphStyle("th2",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
        ]]
        rows = []
        for key, label, options in items:
            opt_text = "   ".join([f"{s}={desc[:25]}" for s,desc in options])
            rows.append([
                Paragraph(f"<b>{label}</b><br/><font size='7' color='#777'>{opt_text}</font>",
                    ParagraphStyle("ti",fontSize=8,fontName="Helvetica",textColor=NOIR,leading=11)),
                "",
            ])
        tbl = Table(header + rows, colWidths=[USEFUL_W-2*cm, 2*cm], repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), BLEU_LIGHT),
            ("TEXTCOLOR", (0,0),(-1,0), BLEU),
            ("LINEBELOW",(0,0),(-1,0), 1.0, BLEU),
            ("ALIGN",         (1,0),(1,-1),  "CENTER"),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS]),
            ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ]))
        story.append(tbl)
        story.append(Paragraph(
            f"Sous-total {part_title.split('—')[0].strip()} : _____ / {max_score}",
            ParagraphStyle("tin_sub",fontSize=9,fontName="Helvetica-Bold",
                textColor=BLEU,spaceAfter=6,spaceBefore=4)))

    story.append(Paragraph(
        "Score TOTAL : _____ / 28    "
        "Seuils : < 19 = risque élevé · 19–23 = risque modéré · ≥ 24 = risque faible",
        ParagraphStyle("tin_tot",fontSize=8,fontName="Helvetica-Oblique",textColor=GRIS_TEXTE)))


def build_tug_fiche(story, styles):
    """Fiche TUG imprimable."""
    story.append(section_band("TUG — Timed Up and Go"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Le patient se lève d'une chaise (sans aide des bras si possible), "
        "marche 3 mètres, fait demi-tour, revient et se rassied. "
        "Chronométrer du signal de départ jusqu'au contact du dos avec la chaise.",
        styles["intro"]))
    story.append(Spacer(1, 0.3*cm))
    rows = [
        ["Temps (secondes)", ""],
        ["Aide technique", "Aucune   /   Canne   /   Déambulateur"],
        ["Chaussures / orthèses", ""],
        ["Observations", ""],
    ]
    tbl = Table(rows, colWidths=[5*cm, USEFUL_W-5*cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("TEXTCOLOR",     (0,0),(0,-1), BLEU),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 9),
        ("BOTTOMPADDING", (0,0),(-1,-1), 9),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Seuils : < 10 sec = normal · 10–19 sec = risque modéré · ≥ 20 sec = risque élevé de chute",
        ParagraphStyle("tug_n",fontSize=8,fontName="Helvetica-Oblique",textColor=GRIS_TEXTE)))


def build_berg_print(story, styles):
    """Berg Balance Scale imprimable — version simplifiée (sans descriptions complètes)."""
    from utils.equilibre_data import BERG_ITEMS
    story.append(section_band("Berg Balance Scale (0–56)"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "14 items cotés de 0 à 4. Score total sur 56. "
        "Seuils : ≤ 20 risque élevé · 21–40 modéré · ≥ 41 risque faible.",
        styles["intro"]))
    story.append(Spacer(1, 0.2*cm))
    header = [[
        Paragraph("<b>Item</b>", ParagraphStyle("bh1",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC)),
        Paragraph("<b>0</b>", ParagraphStyle("bh2",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
        Paragraph("<b>1</b>", ParagraphStyle("bh3",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
        Paragraph("<b>2</b>", ParagraphStyle("bh4",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
        Paragraph("<b>3</b>", ParagraphStyle("bh5",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
        Paragraph("<b>4</b>", ParagraphStyle("bh6",fontSize=8,fontName="Helvetica-Bold",textColor=BLANC,alignment=1)),
    ]]
    rows = []
    for key, label, options in BERG_ITEMS:
        rows.append([
            Paragraph(label, ParagraphStyle("bi",fontSize=8,fontName="Helvetica",textColor=NOIR,leading=11)),
            Checkbox(size=8), Checkbox(size=8), Checkbox(size=8), Checkbox(size=8), Checkbox(size=8),
        ])
    col_w = [USEFUL_W - 5*1.2*cm] + [1.2*cm]*5
    tbl = Table(header + rows, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), BLEU_LIGHT),
        ("TEXTCOLOR", (0,0),(-1,0), BLEU),
            ("LINEBELOW",(0,0),(-1,0), 1.0, BLEU),
        ("ALIGN",         (1,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Score TOTAL : _____ / 56",
        ParagraphStyle("berg_tot",fontSize=10,fontName="Helvetica-Bold",textColor=BLEU)))


def build_sts_eq_fiche(story, styles):
    """Fiche STS 1 minute — Équilibre."""
    story.append(section_band("STS — Sit to Stand 1 minute"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Chaise standard sans appui-bras (~46 cm). "
        "Compter le nombre de levers complets en 1 minute.",
        styles["intro"]))
    story.append(Spacer(1, 0.3*cm))
    rows = [
        ["Nombre de répétitions / minute", ""],
        ["Utilisation des bras", "Oui   /   Non"],
        ["Observations", ""],
    ]
    tbl = Table(rows, colWidths=[6*cm, USEFUL_W-6*cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("TEXTCOLOR",     (0,0),(0,-1), BLEU),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [BLANC, GRIS]),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, GRIS_BORD),
        ("TOPPADDING",    (0,0),(-1,-1), 9),
        ("BOTTOMPADDING", (0,0),(-1,-1), 9),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Normes orientatives gériatrie : < 10 rép/min = limitée · 10–13 = modérée · ≥ 14 = bonne",
        ParagraphStyle("sts_eq_n",fontSize=8,fontName="Helvetica-Oblique",textColor=GRIS_TEXTE)))


QUESTIONNAIRES_PRINT = {
    "muscle":    ("Testing musculaire MI",  _build_muscle_testing),
    "leg_press": ("1RM Leg Press",          _build_leg_press),
    "tinetti":   ("Grille Tinetti",         build_tinetti),
    "tug":       ("Fiche TUG",              build_tug_fiche),
    "berg":      ("Berg Balance Scale",     build_berg_print),
    "sts":       ("STS 1 minute",           build_sts_eq_fiche),
}

def generate_questionnaires_pdf(selected, patient_info=None):
    """Génère un PDF avec les fiches imprimables sélectionnées."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=2.2*cm, bottomMargin=1.8*cm)
    styles = _styles()
    story  = []
    hf     = _make_hf(f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else "")
    for i, key in enumerate(selected):
        if key not in QUESTIONNAIRES_PRINT: continue
        QUESTIONNAIRES_PRINT[key][1](story, styles)
        if i < len(selected)-1: story.append(PageBreak())
    if not story: story.append(Paragraph("Aucun questionnaire sélectionné.", _styles()["normal"]))
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return buffer.getvalue()
