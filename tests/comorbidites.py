"""
tests/questionnaires/comorbidites.py — Comorbidités (copie fidèle v1)
"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test
from tests.tests_cliniques.shared_data import COMORB_CATEGORIES


@register_test
class Comorbidites(BaseTest):

    @classmethod
    def meta(cls):
        return {"id":"comorbidites","nom":"Comorbidités","tab_label":"🏥 Comorbidités",
                "categorie":"questionnaire","tags":["comorbidités", "antécédents", "contexte", "médical", "général"],"description":"Comorbidités et traitements en cours"}

    @classmethod
    def fields(cls):
        return ["comorb_list","comorb_traitements","comorb_notes"]

    def render(self, lv, key_prefix):
        st.markdown('<div class="section-title">🏥 Comorbidités & traitements</div>',
                    unsafe_allow_html=True)

        existing_comorb = str(lv("comorb_list","") or "").split("|")
        existing_trait  = str(lv("comorb_traitements","") or "").split("|")

        all_selected   = []
        treat_selected = []

        for category, items in COMORB_CATEGORIES.items():
            if category == "💊 Traitements en cours":
                with st.expander(category):
                    for item in items:
                        if st.checkbox(item, value=item in existing_trait,
                                       key=f"{key_prefix}_trait_{item.replace(' ','_')[:30]}"):
                            treat_selected.append(item)
            else:
                with st.expander(category):
                    for item in items:
                        if st.checkbox(item, value=item in existing_comorb,
                                       key=f"{key_prefix}_comorb_{item.replace(' ','_')[:30]}"):
                            all_selected.append(item)

        comorb_notes = st.text_area("Autres comorbidités / remarques",
                                    value=str(lv("comorb_notes","") or ""),
                                    height=80, key=f"{key_prefix}_comorb_notes")
        return {
            "comorb_list":        "|".join(all_selected),
            "comorb_traitements": "|".join(treat_selected),
            "comorb_notes":       comorb_notes,
        }

    @classmethod
    def is_filled(cls, bilan_data):
        return bool(str(bilan_data.get("comorb_list","")).strip())

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import pandas as pd
        rows = [{"Bilan":lbl,
                 "Comorbidités":str(row.get("comorb_list","—")).replace("|"," · "),
                 "Traitements":str(row.get("comorb_traitements","—")).replace("|"," · ")}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
