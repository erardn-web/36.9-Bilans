"""tests/tests_cliniques/tests_objectifs_lombaire.py — Tests objectifs lombalgie (copie fidèle v1)"""
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
        return {"id":"tests_objectifs_lombaire","nom":"Tests objectifs",
                "tab_label":"🔬 Tests objectifs","categorie":"test_clinique",
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
