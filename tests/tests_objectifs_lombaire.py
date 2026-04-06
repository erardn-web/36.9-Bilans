"""tests/tests_objectifs_lombaire.py — Tests objectifs lombalgie (copie fidèle v1)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

TESTS_CLINIQUES = {
    "Tests neurologiques": [
        "Lasègue (SLR) droit","Lasègue (SLR) gauche","Lasègue croisé",
        "Test de Bragard","Réflexe rotulien","Réflexe achilléen",
        "Sensibilité dermatomes L4/L5/S1","Force quadriceps / tibial ant. / triceps sural",
    ],
    "Tests sacro-iliaques": [
        "FABER (Patrick)","Gaenslen","Compression sacro-iliaque",
        "Distraction sacro-iliaque","Test de Gillet (marche)",
    ],
    "Tests de provocation discale": [
        "Valsalva","Compression axiale","Décompression axiale",
    ],
}
RESULTATS_TEST = ["—","Négatif","Positif droit","Positif gauche","Positif bilatéral","Non réalisé"]

def _sk(test):
    return "o_tol_" + test.lower().replace(" ","_").replace("/","_").replace("(","").replace(")","").replace(".","")[:25]

ALL_TEST_FIELDS = [_sk(t) for tests in TESTS_CLINIQUES.values() for t in tests]
ALL_FIELDS      = ["o_posture_notes"] + ALL_TEST_FIELDS + ["o_tests_notes"]

@register_test
class TestsObjectifsLombaire(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tests_objectifs_lombaire","nom":"Tests objectifs lombaires",
                "tab_label":"🔬 Tests objectifs lombaires","categorie":"test_clinique","tags":["lombalgie", "neurologique", "sacro-iliaque", "clinique", "tests"],
                "description":"Tests neurologiques, sacro-iliaques, discaux"}

    @classmethod
    def fields(cls):
        return ALL_FIELDS

    def render(self, lv, key_prefix):
        collected={}
        st.markdown('<div class="section-title">Observation posturale</div>', unsafe_allow_html=True)
        collected["o_posture_notes"]=st.text_area("Observation posturale",
            value=lv("o_posture_notes",""),height=80,key=f"{key_prefix}_posture")
        st.markdown("---")
        for section_name,tests in TESTS_CLINIQUES.items():
            with st.expander(section_name,expanded=False):
                tc1,tc2=st.columns(2)
                for i,test in enumerate(tests):
                    sk=_sk(test)
                    sv=lv(sk,"")
                    idx=RESULTATS_TEST.index(sv) if sv in RESULTATS_TEST else 0
                    with (tc1 if i%2==0 else tc2):
                        chosen=st.selectbox(test,RESULTATS_TEST,index=idx,
                                            key=f"{key_prefix}_{sk}")
                    collected[sk]="" if chosen=="—" else chosen
        collected["o_tests_notes"]=st.text_area("Notes complémentaires",
            value=lv("o_tests_notes",""),height=60,key=f"{key_prefix}_tests_notes")
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        return any(str(bilan_data.get(_sk(t),"")).strip() not in ("","—","None","nan")
                   for tests in TESTS_CLINIQUES.values() for t in tests)

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import pandas as pd
        for section,tests in TESTS_CLINIQUES.items():
            st.markdown(f"**{section}**")
            for test in tests:
                sk=_sk(test)
                vals=[str(row.get(sk,"")) for _,row in bilans_df.iterrows()]
                if any(v not in ("","—","None","nan") for v in vals):
                    st.markdown("*"+test+"* : "+" · ".join(
                        f"{lbl}: **{v}**" for lbl,v in zip(labels,vals)
                        if v not in ("","—","None","nan")))

    @classmethod
    def render_print_sheet(cls, story: list, styles: dict) -> None:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm; from reportlab.lib import colors
        LINE = colors.HexColor("#CCCCCC"); BLEU = colors.HexColor("#2B57A7")
        story.append(Paragraph("Tests Objectifs Lombaires", styles["section"]))
        story.append(Paragraph("Tests cliniques spécifiques pour l'évaluation de la lombalgie.", styles["intro"]))
        hdr = Table([["Patient : "+"_"*28,"Date : "+"_"*14,"Praticien : "+"_"*14]],colWidths=[8*cm,4.5*cm,4.5*cm])
        hdr.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#555"))]))
        story.append(hdr); story.append(Spacer(1,0.3*cm))
        def section(titre, tests):
            story.append(Paragraph(titre, styles["subsection"]))
            rows = [["Test","D","G","Bilatéral","Résultat/Notes"]] +                    [[t,"☐","☐","☐","_"*20] for t in tests]
            tb = Table(rows, colWidths=[6*cm,1.2*cm,1.2*cm,2.2*cm,6.4*cm])
            tb.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EEF9")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("GRID",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                ("ALIGN",(1,0),(3,-1),"CENTER")]))
            story.append(tb); story.append(Spacer(1,0.2*cm))
        section("Tests neurologiques", [
            "Lasègue (SLR)", "Lasègue croisé", "Slump test",
            "Test de Wassermann (fémoral)", "Réflexe rotulien", "Réflexe achilléen",
            "Force L4 (extension genou)", "Force L5 (dorsiflexion pied)", "Force S1 (flexion plantaire)"])
        section("Tests sacro-iliaques", [
            "FABER / Patrick", "FADIR", "Compression SI", "Distraction SI",
            "Gaenslen", "Thigh thrust", "Test de Gillet"])
        story.append(Paragraph("Notes : "+"_"*70, styles["normal"]))

