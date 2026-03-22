"""
bpco_pdf.py — Génération PDF BPCO
"""
import io, os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image,
)

TERRA=colors.HexColor("#C4603A"); BLEU=colors.HexColor("#2B57A7")
GRIS=colors.HexColor("#F4F4F4"); GRIS_BORD=colors.HexColor("#DEDEDE")
GRIS_TEXTE=colors.HexColor("#555555"); BLANC=colors.white
NOIR=colors.HexColor("#1A1A1A"); BLEU_LIGHT=colors.HexColor("#E8EEF9")
VERT=colors.HexColor("#388e3c"); ORANGE=colors.HexColor("#f57c00"); ROUGE=colors.HexColor("#d32f2f")

W=A4[0]-3*cm; MARGIN=1.5*cm

LOGO_PATH=os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","logo_369.png")

def _find_logo():
    for p in [LOGO_PATH,"assets/logo_369.png","/mount/src/36.9-bilans/assets/logo_369.png"]:
        if os.path.exists(p): return p
    return None

def _make_hf(patient_name=""):
    def _draw(canvas,doc):
        canvas.saveState(); w,h=A4
        canvas.setFillColor(TERRA); canvas.rect(0,h-0.35*cm,w,0.35*cm,fill=1,stroke=0)
        logo=_find_logo()
        if logo:
            try: canvas.drawImage(logo,MARGIN,h-1.4*cm,width=2.6*cm,height=1.0*cm,
                                  preserveAspectRatio=True,mask="auto")
            except: pass
        canvas.setFillColor(GRIS_TEXTE); canvas.setFont("Helvetica",8)
        canvas.drawCentredString(w/2,h-1.1*cm,"36.9 Bilans — Rapport BPCO")
        if patient_name:
            canvas.setFillColor(BLEU); canvas.setFont("Helvetica-Bold",8)
            canvas.drawRightString(w-MARGIN,h-1.1*cm,patient_name)
        canvas.setStrokeColor(GRIS_BORD); canvas.setLineWidth(0.5)
        canvas.line(MARGIN,h-1.5*cm,w-MARGIN,h-1.5*cm)
        canvas.line(MARGIN,0.9*cm,w-MARGIN,0.9*cm)
        canvas.setFillColor(GRIS_TEXTE); canvas.setFont("Helvetica",7)
        canvas.drawString(MARGIN,0.35*cm,"Document confidentiel — Usage médical")
        canvas.drawCentredString(w/2,0.35*cm,"36.9 Bilans")
        canvas.drawRightString(w-MARGIN,0.35*cm,f"Page {doc.page}  ·  {date.today().strftime('%d/%m/%Y')}")
        canvas.restoreState()
    return _draw

def _styles():
    return {
        "title": ParagraphStyle("bp_t",fontSize=22,fontName="Helvetica-Bold",
            textColor=BLEU,alignment=TA_CENTER,spaceAfter=4),
        "section": ParagraphStyle("bp_s",fontSize=10,fontName="Helvetica-Bold",
            textColor=BLANC,backColor=BLEU,spaceBefore=10,spaceAfter=5,
            leftIndent=-6,rightIndent=-6,borderPadding=(5,8,5,8)),
        "subsection": ParagraphStyle("bp_ss",fontSize=10,fontName="Helvetica-Bold",
            textColor=TERRA,spaceBefore=8,spaceAfter=4),
        "normal": ParagraphStyle("bp_n",fontSize=9,fontName="Helvetica",textColor=NOIR,spaceAfter=2),
        "small": ParagraphStyle("bp_sm",fontSize=7.5,fontName="Helvetica",textColor=GRIS_TEXTE),
    }

def _section(title):
    row=[[Paragraph(f"<font color='#C4603A'>▌</font>&nbsp;&nbsp;<b>{title}</b>",
        ParagraphStyle("bp_sh",fontSize=10,fontName="Helvetica-Bold",textColor=BLANC,leading=14))]]
    t=Table(row,colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),10)]))
    return t

def _tbl(data,col_widths=None,header=True):
    t=Table(data,colWidths=col_widths,repeatRows=1 if header else 0)
    cmds=[("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),8),
          ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ROWBACKGROUNDS",(0,1),(-1,-1),[BLANC,GRIS]),
          ("LINEBELOW",(0,0),(-1,-1),0.3,GRIS_BORD),("TOPPADDING",(0,0),(-1,-1),5),
          ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),7)]
    if header:
        cmds+=[("BACKGROUND",(0,0),(-1,0),BLEU),("TEXTCOLOR",(0,0),(-1,0),BLANC),
               ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),
               ("TOPPADDING",(0,0),(-1,0),7),("BOTTOMPADDING",(0,0),(-1,0),7)]
    t.setStyle(TableStyle(cmds)); return t

def _sn(v):
    try: r=float(v); return r if r!=0 else None
    except: return None

def _val(v,suffix=""):
    n=_sn(v)
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

    from reportlab.platypus import Flowable as _F
    class Checkbox(_F):
        def __init__(self, size=8):
            _F.__init__(self); self.size=size; self.width=size+4; self.height=size
        def draw(self):
            self.canv.setStrokeColor(_colors.HexColor("#333")); self.canv.setLineWidth(0.7)
            self.canv.rect(1,0,self.size,self.size,fill=0,stroke=1)

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
        ("BACKGROUND",    (0,0),(-1,0),  BLEU),
        ("TEXTCOLOR",     (0,0),(-1,0),  BLANC),
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


def generate_pdf_bpco(bilans_df, patient_info: dict) -> bytes:
    import pandas as pd
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,
        leftMargin=MARGIN,rightMargin=MARGIN,topMargin=2.2*cm,bottomMargin=1.8*cm)
    styles=_styles(); story=[]; hf=_make_hf(f"{patient_info.get('nom','')} {patient_info.get('prenom','')}")

    bilans_df=bilans_df.copy()
    bilans_df["date_bilan"]=pd.to_datetime(bilans_df["date_bilan"],errors="coerce")
    bilans_df=bilans_df.sort_values("date_bilan").reset_index(drop=True)
    n=len(bilans_df)
    labels=[f"{r['date_bilan'].strftime('%d/%m/%Y')} — {r.get('type_bilan','')}"
            for _,r in bilans_df.iterrows()]
    short=[f"{r['date_bilan'].strftime('%d/%m/%y')}" for _,r in bilans_df.iterrows()]

    # Page de garde
    band=Table([[Paragraph("<font color='white'><b>Rapport d'évolution — BPCO</b></font>",
        ParagraphStyle("ct",fontSize=20,fontName="Helvetica-Bold",textColor=BLANC,alignment=TA_CENTER))]],
        colWidths=[W])
    band.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU),
        ("TOPPADDING",(0,0),(-1,-1),18),("BOTTOMPADDING",(0,0),(-1,-1),18)]))
    sub=Table([[Paragraph("<font color='white'>Bilan physiothérapeutique — Pneumologie</font>",
        ParagraphStyle("cs",fontSize=11,fontName="Helvetica",textColor=BLANC,alignment=TA_CENTER))]],
        colWidths=[W])
    sub.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),TERRA),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story.append(Spacer(1,0.8*cm)); story.append(band); story.append(sub); story.append(Spacer(1,0.5*cm))
    logo=_find_logo()
    if logo:
        lt=Table([[Image(logo,width=5*cm,height=2*cm,kind="proportional")]],colWidths=[W])
        lt.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")])); story.append(lt)
        story.append(Spacer(1,0.4*cm))
    pat=[["Patient",f"{patient_info.get('nom','')} {patient_info.get('prenom','')}"],
         ["Date de naissance",str(patient_info.get("date_naissance","—"))],
         ["Sexe",patient_info.get("sexe","—")],
         ["Nombre de bilans",str(n)],
         ["Généré le",date.today().strftime("%d/%m/%Y")]]
    pt=Table(pat,colWidths=[4.5*cm,W-4.5*cm])
    pt.setStyle(TableStyle([("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(1,0),(1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),9),
        ("TEXTCOLOR",(0,0),(0,-1),BLEU),("ROWBACKGROUNDS",(0,0),(-1,-1),[BLANC,BLEU_LIGHT]),
        ("LINEBELOW",(0,0),(-1,-1),0.3,GRIS_BORD),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),10)]))
    story.append(pt); story.append(Spacer(1,0.5*cm))
    bil=[["#","Date","Type","Praticien"]]
    for i,(_,row) in enumerate(bilans_df.iterrows()):
        d=row["date_bilan"]; ds=d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        bil.append([str(i+1),ds,row.get("type_bilan","—") or "—",row.get("praticien","—") or "—"])
    story.append(_tbl(bil,col_widths=[1.2*cm,3.2*cm,5*cm,W-9.4*cm])); story.append(PageBreak())

    # Synthèse
    story.append(_section("Synthèse des scores")); story.append(Spacer(1,0.3*cm))
    col_w=[6*cm]+[(W-6*cm)/n]*n
    shdr=[["Indicateur"]+[f"B{i+1}" for i in range(n)]]
    srows=[]
    def add(label,key,suffix=""):
        vals=[_val(r.get(key),suffix) for _,r in bilans_df.iterrows()]
        if any(v!="—" for v in vals): srows.append([label]+vals)
    add("6MWT (m)","mwt_distance"); add("SpO₂ repos (%)","spo2_repos")
    add("SpO₂ min effort","mwt_spo2_min"); add("STS 1 min (rép)","sts_1min_reps")
    add("mMRC","mmrc_grade"); add("CAT /40","cat_score")
    add("VEMS % prédit","spiro_vems_pct"); add("VEMS (L)","spiro_vems")
    add("CVF (L)","spiro_cvf"); add("VEMS/CVF (%)","spiro_ratio")
    add("BODE /10","bode_score"); add("IMC","bmi")
    if srows: story.append(_tbl(shdr+srows,col_widths=col_w))
    story.append(PageBreak())

    # Graphiques
    def fig_img(fig,w=16,h=5):
        b=io.BytesIO()
        fig.savefig(b,format="png",dpi=150,bbox_inches="tight",facecolor="white")
        plt.close(fig); b.seek(0); return Image(b,width=w*cm,height=h*cm)

    charts=[("6MWT (m)","mwt_distance","#2B57A7"),("STS 1 min","sts_1min_reps","#C4603A"),
            ("CAT /40","cat_score","#f57c00"),("VEMS % prédit","spiro_vems_pct","#388e3c"),
            ("BODE /10","bode_score","#7b1fa2")]
    has_chart=False
    for name,key,color in charts:
        vals=[_sn(r.get(key)) for _,r in bilans_df.iterrows()]
        if not any(v is not None for v in vals): continue
        if not has_chart:
            story.append(_section("Graphiques d'évolution")); story.append(Spacer(1,0.3*cm))
            has_chart=True
        fig,ax=plt.subplots(figsize=(12,4))
        xp=[i for i,v in enumerate(vals) if v is not None]
        yp=[v for v in vals if v is not None]
        ax.plot(xp,yp,"o-",color=color,lw=2.5,ms=9)
        for xi,yi in zip(xp,yp):
            ax.annotate(str(int(yi)) if yi==int(yi) else str(yi),(xi,yi),
                textcoords="offset points",xytext=(0,8),ha="center",fontsize=9,fontweight="bold",color=color)
        ax.set_xticks(range(len(short))); ax.set_xticklabels(short,rotation=15,ha="right")
        ax.set_title(name,fontsize=11,fontweight="bold",color="#2B57A7")
        ax.spines[["top","right"]].set_visible(False); ax.set_facecolor("white")
        ax.grid(axis="y",alpha=0.3); fig.tight_layout()
        story.append(Paragraph(name,styles["subsection"])); story.append(fig_img(fig))
        story.append(Spacer(1,0.4*cm))
    if has_chart: story.append(PageBreak())

    # Détail
    story.append(_section("Détail des bilans"))
    for i,(_,row) in enumerate(bilans_df.iterrows()):
        story.append(Spacer(1,0.3*cm))
        story.append(Paragraph(f"Bilan {i+1} — {labels[i]}",styles["subsection"]))
        det=[["Paramètre","Valeur","Détail"]]
        for lbl,k,ik in [("6MWT","mwt_distance","mwt_interpretation"),
                         ("SpO₂ repos","spo2_repos",""),("SpO₂ effort min","mwt_spo2_min",""),
                         ("STS 1 min","sts_1min_reps","sts_1min_interpretation"),
                         ("mMRC","mmrc_grade",""),("CAT","cat_score","cat_interpretation"),
                         ("VEMS %","spiro_vems_pct","spiro_gold"),("BODE","bode_score","bode_interpretation")]:
            v=_val(row.get(k))
            if v!="—": det.append([lbl,v,str(row.get(ik,"—") or "—")])
        if len(det)>1: story.append(_tbl(det,col_widths=[4*cm,3*cm,W-7*cm]))
        if row.get("notes_generales"):
            story.append(Paragraph(f"Notes : {row['notes_generales']}",styles["normal"]))
        if i<n-1: story.append(PageBreak())

    doc.build(story,onFirstPage=hf,onLaterPages=hf)
    return buf.getvalue()


def generate_questionnaires_bpco_pdf(selected, patient_info=None) -> bytes:
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,
        leftMargin=MARGIN,rightMargin=MARGIN,topMargin=2.2*cm,bottomMargin=1.8*cm)
    hf=_make_hf(f"{patient_info.get('nom','')} {patient_info.get('prenom','')}" if patient_info else "")
    from utils.bpco_pdf import _styles
    styles=_styles()
    story=[]
    for i,key in enumerate(selected):
        if key in QUESTIONNAIRES_PRINT:
            QUESTIONNAIRES_PRINT[key][1](story,styles)
            if i<len(selected)-1:
                from reportlab.platypus import PageBreak
                story.append(PageBreak())
    if not story: return b""
    doc.build(story,onFirstPage=hf,onLaterPages=hf)
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

QUESTIONNAIRES_PRINT = {
    "muscle":    ("Testing musculaire MI",  _build_muscle_testing),
    "leg_press": ("1RM Leg Press",          _build_leg_press),
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
