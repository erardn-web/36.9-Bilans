"""tests/tests_cliniques/drapeaux.py — Drapeaux rouges/jaunes Lombalgie (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

DRAPEAUX_ROUGES = [
    "Âge < 20 ans ou > 55 ans avec douleur nouvelle",
    "Traumatisme violent récent",
    "Douleur non mécanique (constante, nocturne, indépendante de la position)",
    "Douleur thoracique associée","Antécédent de cancer",
    "Usage prolongé de corticoïdes","Consommation de drogues IV / immunodépression",
    "Perte de poids inexpliquée",
    "Syndrome de la queue de cheval (troubles sphinctériens, anesthésie en selle)",
    "Déficit neurologique progressif","Déformation structurale sévère","Fièvre / état général altéré",
]
DRAPEAUX_JAUNES = [
    "Croyances négatives sur la douleur (catastrophisme)",
    "Peur du mouvement / kinésiophobie","Comportement d'évitement marqué",
    "Dépression / anxiété associée","Faible soutien social ou familial",
    "Insatisfaction au travail / conflit professionnel",
    "Litige juridique ou compensation en cours","Attentes thérapeutiques irréalistes",
    "Historique de douleur chronique","Hypervigilance corporelle",
]

@register_test
class Drapeaux(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"drapeaux","nom":"Drapeaux rouges/jaunes","tab_label":"🚩 Drapeaux",
                "categorie":"test_clinique","tags":["lombalgie", "drapeaux", "urgence", "biopsychosocial"],"description":"Drapeaux rouges (urgence) et jaunes (biopsychosocial)"}

    @classmethod
    def fields(cls):
        return ["drapeaux_rouges_list","drapeaux_rouges_notes",
                "drapeaux_jaunes_list","drapeaux_jaunes_notes"]

    @classmethod
    def print_options(cls) -> list:
        return [
            {"key": "liste", "label": "Drapeaux cochés", "default": True},
        ]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🚩 Drapeaux rouges</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box" style="background:#fff3f3;border-left:4px solid #d32f2f;">'
                    '⚠️ Présence de drapeaux rouges → investigation médicale urgente.</div>',
                    unsafe_allow_html=True)
        dr_stored=[x for x in str(lv("drapeaux_rouges_list","")).split("|") if x in DRAPEAUX_ROUGES]
        dr_sel=[]
        cols_dr=st.columns(2)
        for i,item in enumerate(DRAPEAUX_ROUGES):
            with cols_dr[i%2]:
                if st.checkbox(item,value=item in dr_stored,key=f"{key_prefix}_dr_{i}"):
                    dr_sel.append(item)
        if dr_sel:
            st.markdown(f'<div class="info-box" style="background:#fff3f3;">'
                        f'🔴 <b>{len(dr_sel)} drapeau(x) rouge(s) détecté(s)</b></div>',
                        unsafe_allow_html=True)
        dr_notes=st.text_area("Notes drapeaux rouges",value=lv("drapeaux_rouges_notes",""),
                               height=60,key=f"{key_prefix}_dr_notes")
        st.markdown("---")
        st.markdown('<div class="section-title">🟡 Drapeaux jaunes</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Drapeaux jaunes → approche biopsychosociale.</div>',
                    unsafe_allow_html=True)
        dj_stored=[x for x in str(lv("drapeaux_jaunes_list","")).split("|") if x in DRAPEAUX_JAUNES]
        dj_sel=[]
        cols_dj=st.columns(2)
        for i,item in enumerate(DRAPEAUX_JAUNES):
            with cols_dj[i%2]:
                if st.checkbox(item,value=item in dj_stored,key=f"{key_prefix}_dj_{i}"):
                    dj_sel.append(item)
        if dj_sel:
            st.markdown(f'<div class="info-box">'
                        f'🟡 <b>{len(dj_sel)} drapeau(x) jaune(s)</b></div>',
                        unsafe_allow_html=True)
        dj_notes=st.text_area("Notes drapeaux jaunes",value=lv("drapeaux_jaunes_notes",""),
                               height=60,key=f"{key_prefix}_dj_notes")
        return {"drapeaux_rouges_list":"|".join(dr_sel),"drapeaux_rouges_notes":dr_notes,
                "drapeaux_jaunes_list":"|".join(dj_sel),"drapeaux_jaunes_notes":dj_notes}

    @classmethod
    def is_filled(cls, bilan_data):
        dr=str(bilan_data.get("drapeaux_rouges_list","")).strip()
        dj=str(bilan_data.get("drapeaux_jaunes_list","")).strip()
        return bool(dr) or bool(dj)

    @classmethod
    def render_evolution(cls, bilans_df, labels,
                         show_print_controls=False, cas_id=''):
        import pandas as pd
        rows=[]
        for lbl,(_,row) in zip(labels,bilans_df.iterrows()):
            dr=str(row.get("drapeaux_rouges_list","")).strip()
            dj=str(row.get("drapeaux_jaunes_list","")).strip()
            n_dr=len([x for x in dr.split("|") if x]) if dr else 0
            n_dj=len([x for x in dj.split("|") if x]) if dj else 0
            rows.append({"Bilan":lbl,"🔴 Drapeaux rouges":n_dr,"🟡 Drapeaux jaunes":n_dj})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        for lbl,(_,row) in zip(labels,bilans_df.iterrows()):
            dr=str(row.get("drapeaux_rouges_list",""))
            if dr.strip():
                items=[x for x in dr.split("|") if x]
                if items:
                    st.markdown(f"**{lbl}** — Rouges : {', '.join(items)}")

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        RED = colors.HexColor("#FCEBEB"); ORANGE = colors.HexColor("#FAEEDA"); YELLOW = colors.HexColor("#FFFDE7")
        story.append(Paragraph("Drapeaux — Identification des signaux d'alarme", styles["section"]))
        story.append(Paragraph("Identifier les facteurs nécessitant une attention particulière ou une orientation.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        def section(titre, items, bg):
            story.append(Paragraph(titre, styles["subsection"]))
            rows = [[f"☐  {item}"] for item in items]
            t = Table(rows, colWidths=[17*cm])
            t.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("BACKGROUND",(0,0),(-1,-1),bg),
                ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                ("LEFTPADDING",(0,0),(-1,-1),8)]))
            story.append(t); story.append(Spacer(1,0.2*cm))
        section("🚩 Drapeaux ROUGES — Urgence médicale (orienter immédiatement)", [
            "Traumatisme important récent","Perte de poids inexpliquée (> 5 kg en 3 mois)",
            "Fièvre / frissons inexpliqués","Douleur nocturne intense non mécanique",
            "Troubles sphinctériens (vessie/intestin)","Déficit neurologique progressif",
            "Antécédents de cancer","Utilisation prolongée de corticoïdes","Immunosuppression / VIH",
        ], RED)
        section("🟠 Drapeaux ORANGES — Facteurs psychologiques à considérer", [
            "Dépression clinique / anxiété sévère","Comportement douloureux excessif",
            "Problèmes psychiatriques non traités","Pensées suicidaires",
        ], ORANGE)
        section("🟡 Drapeaux JAUNES — Facteurs psychosociaux (risque chronicisation)", [
            "Croyances négatives sur la douleur / kinésiophobie","Catastrophisme",
            "Attentes négatives de rétablissement","Évitement des activités par peur",
            "Insatisfaction au travail / problèmes professionnels","Isolement social",
            "Soutien familial insuffisant ou surimplication","Antécédents de douleur chronique",
        ], YELLOW)
        story.append(Paragraph("Observations : "+"_"*70, styles["normal"]))

