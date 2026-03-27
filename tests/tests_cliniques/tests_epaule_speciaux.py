"""tests/tests_cliniques/tests_epaule_speciaux.py — Tests spéciaux épaule (coiffe, conflit, biceps, AC)"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

RESULTATS = ["—","Négatif","Positif","Douloureux","Non réalisé"]
RESULTATS_SIDE = ["—","Négatif","Positif droit","Positif gauche","Positif bilatéral","Non réalisé"]

TESTS_COIFFE = [
    ("ep_jobe",       "Jobe (Empty can)",        "Abduction 90°, rotation interne (pouce vers le bas), résistance en abduction — sus-épineux"),
    ("ep_full_can",   "Full can",                 "Abduction 90°, rotation externe (pouce vers le haut), résistance — sus-épineux (moins douloureux)"),
    ("ep_patte",      "Patte (Hornblower)",       "Rotation externe passive → relâchement → test sous-épineux/petit rond"),
    ("ep_gerber",     "Gerber (Lift-off)",        "Main dans le dos, décoller contre résistance — subscapulaire"),
    ("ep_belly_press","Belly press",              "Presser l'abdomen en rotation interne — subscapulaire"),
    ("ep_bear_hug",   "Bear hug",                 "Main sur épaule opposée, résistance à l'élévation — subscapulaire"),
]
TESTS_CONFLIT = [
    ("ep_neer",       "Neer",                     "Élévation passive bras tendu, rotation interne — conflit sous-acromial"),
    ("ep_hawkins",    "Hawkins-Kennedy",           "Flexion 90°, rotation interne forcée — conflit sous-acromial"),
    ("ep_yocum",      "Yocum",                    "Main sur épaule opposée, élévation du coude — conflit sous-acromial"),
]
TESTS_BICEPS = [
    ("ep_speed",      "Speed",                    "Flexion contre résistance, coude tendu, paume vers le haut — biceps/SLAP"),
    ("ep_yergason",   "Yergason",                 "Supination contre résistance, coude fléchi à 90° — biceps/SLAP"),
    ("ep_obrien",     "O'Brien (SLAP)",            "Flexion 90°, adduction 10°, rotation interne puis externe — SLAP/AC"),
]
TESTS_AC = [
    ("ep_cross_arm",  "Crossed arm (Adduction)",  "Adduction horizontale passive — articulation AC"),
    ("ep_obrien_ac",  "O'Brien (AC)",              "Même test que SLAP mais positif en rotation externe → AC"),
    ("ep_palpation_ac","Palpation AC",             "Douleur locale à la palpation de l'articulation AC"),
]
ALL_TESTS = TESTS_COIFFE + TESTS_CONFLIT + TESTS_BICEPS + TESTS_AC
ALL_KEYS = [t[0] for t in ALL_TESTS] + ["ep_tests_notes"]

@register_test
class TestsEpauleSpeciaux(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"tests_epaule_speciaux","nom":"Tests spéciaux épaule",
                "tab_label":"🔬 Tests spéciaux","categorie":"test_clinique",
                "description":"Coiffe (Jobe, Patte, Gerber), conflit (Neer, Hawkins), biceps/SLAP, AC"}

    @classmethod
    def fields(cls):
        return ALL_KEYS

    def render(self, lv, key_prefix):
        collected = {}
        for section_title, tests in [
            ("Coiffe des rotateurs", TESTS_COIFFE),
            ("Conflit sous-acromial", TESTS_CONFLIT),
            ("Biceps / SLAP", TESTS_BICEPS),
            ("Articulation acromio-claviculaire (AC)", TESTS_AC),
        ]:
            st.markdown(f'<div class="section-title">{section_title}</div>',
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            for i, (key, label, desc) in enumerate(tests):
                stored = lv(key,"")
                idx = RESULTATS.index(stored) if stored in RESULTATS else 0
                with (c1 if i%2==0 else c2):
                    st.markdown(f"**{label}**")
                    st.markdown(f"<small style='color:#666'>{desc}</small>",
                                unsafe_allow_html=True)
                    chosen = st.radio("", RESULTATS, index=idx, horizontal=True,
                                      key=f"{key_prefix}_{key}", label_visibility="collapsed")
                    collected[key] = "" if chosen == "—" else chosen
            st.markdown("---")

        collected["ep_tests_notes"] = st.text_area(
            "Notes complémentaires", value=lv("ep_tests_notes",""),
            height=60, key=f"{key_prefix}_ep_tests_notes")
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        return any(str(bilan_data.get(t[0],"")).strip() not in ("","—","None","nan")
                   for t in ALL_TESTS)

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import pandas as pd
        key_tests = [("ep_jobe","Jobe"),("ep_hawkins","Hawkins"),
                     ("ep_neer","Neer"),("ep_gerber","Gerber"),
                     ("ep_speed","Speed"),("ep_obrien","O'Brien")]
        rows = []
        for lbl,(_,row) in zip(labels,bilans_df.iterrows()):
            r = {"Bilan":lbl}
            for k,n in key_tests:
                r[n] = row.get(k,"—") or "—"
            rows.append(r)
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
