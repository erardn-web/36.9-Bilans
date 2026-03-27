"""tests/tests_cliniques/classification_epaule.py — Classification clinique + raisonnement épaule douloureuse"""
import streamlit as st
from core.test_base import BaseTest
from core.registry  import register_test

CLASSIFICATIONS_EPAULE = [
    ("—",        "— Non classifié —",              ""),
    ("conflit",  "🔴 Syndrome de conflit sous-acromial",
     "Douleur à l'arc douloureux (60–120°), tests de conflit positifs (Neer, Hawkins). "
     "→ Travail en dessous du conflit, renforcement coiffe, correction posturale scapulaire."),
    ("coiffe",   "🟠 Lésion de la coiffe des rotateurs",
     "Tests coiffe positifs (Jobe, Patte, Gerber), faiblesse en rotation. "
     "→ Programme progressif de renforcement excentrique/concentrique, stabilisation scapulaire."),
    ("ac",       "🟡 Pathologie acromio-claviculaire",
     "Douleur AC, crossed arm test positif, O'Brien positif en rotation externe. "
     "→ Éviter adduction horizontale, renforcement scapulaire, mobilisation prudente."),
    ("biceps",   "🔵 Tendinopathie du biceps / SLAP",
     "Speed et Yergason positifs, douleur gouttière bicipitale. "
     "→ Travail excentrique biceps, éviter supination forcée, correction biomécanique."),
    ("frozen",   "🟣 Épaule gelée (capsulite rétractile)",
     "Limitation dans tous les plans (capsulaire pattern), douleur nocturne, raideur progressive. "
     "→ Phase I: antalgique / phase II: mobilisation progressive / phase III: renforcement."),
    ("instab",   "⚪ Instabilité gléno-humérale",
     "Appréhension, relocation test positif, hyperlaxité ligamentaire. "
     "→ Renforcement coiffe et stabilisateurs scapulaires, proprioception, éviter positions à risque."),
]
GROUPES_OPTIONS = [g[1] for g in CLASSIFICATIONS_EPAULE]
GROUPES_CODES   = [g[0] for g in CLASSIFICATIONS_EPAULE]
GROUPES_DESC    = {g[0]: g[2] for g in CLASSIFICATIONS_EPAULE}
GROUPES_COLORS  = {"conflit":"#d32f2f","coiffe":"#f57c00","ac":"#fbc02d",
                   "biceps":"#1565c0","frozen":"#7b1fa2","instab":"#616161","—":"#888"}
DRAPEAUX_EPAULE = [
    "Traumatisme violent récent (fracture/luxation)",
    "Douleur nocturne sévère constante non mécanique",
    "Masse palpable ou déformation osseuse",
    "Fièvre / état général altéré",
    "Antécédent de cancer",
    "Déficit neurologique (parésie, anesthésie brachiale)",
    "Douleur irradiée cervicale évocatrice de radiculopathie",
    "Syndrome de la veine axillaire (œdème, cyanose bras)",
]

@register_test
class ClassificationEpaule(BaseTest):
    @classmethod
    def meta(cls):
        return {"id":"classification_epaule","nom":"Classification & Raisonnement épaule",
                "tab_label":"🩺 Classification","categorie":"test_clinique",
                "description":"Classification clinique épaule + drapeaux rouges + raisonnement + plan"}

    @classmethod
    def fields(cls):
        return ["ep_groupe_clinique","ep_drapeaux_list","ep_diag_notes",
                "ep_appreciation","ep_objectifs","ep_traitement",
                "ep_frequence","ep_duree","ep_education","ep_autogestion"]

    def render(self, lv, key_prefix):
        collected = {}

        # Drapeaux rouges
        st.markdown('<div class="section-title">🚩 Drapeaux rouges</div>',
                    unsafe_allow_html=True)
        dr_stored = [x for x in str(lv("ep_drapeaux_list","")).split("|")
                     if x in DRAPEAUX_EPAULE]
        dr_sel = []
        dc1, dc2 = st.columns(2)
        for i, item in enumerate(DRAPEAUX_EPAULE):
            with (dc1 if i%2==0 else dc2):
                if st.checkbox(item, value=item in dr_stored,
                               key=f"{key_prefix}_dr_{i}"):
                    dr_sel.append(item)
        if dr_sel:
            st.markdown(f'<div class="info-box" style="background:#fff3f3;">'
                        f'🔴 <b>{len(dr_sel)} drapeau(x) rouge(s)</b></div>',
                        unsafe_allow_html=True)
        collected["ep_drapeaux_list"] = "|".join(dr_sel)
        st.markdown("---")

        # Classification
        st.markdown('<div class="section-title">🩺 Classification clinique</div>',
                    unsafe_allow_html=True)
        stored_g = lv("ep_groupe_clinique","—")
        idx_g = GROUPES_OPTIONS.index(stored_g) if stored_g in GROUPES_OPTIONS else 0
        chosen_g = st.radio("Tableau clinique", GROUPES_OPTIONS, index=idx_g,
                            key=f"{key_prefix}_groupe", horizontal=False)
        code = GROUPES_CODES[GROUPES_OPTIONS.index(chosen_g)]
        if code != "—" and GROUPES_DESC.get(code):
            color = GROUPES_COLORS[code]
            st.markdown(f'<div class="info-box" style="border-left:4px solid {color};">'
                        f'{GROUPES_DESC[code]}</div>', unsafe_allow_html=True)
        collected["ep_groupe_clinique"] = chosen_g
        st.markdown("---")

        # Raisonnement
        st.markdown('<div class="section-title">Raisonnement clinique</div>',
                    unsafe_allow_html=True)
        collected["ep_diag_notes"] = st.text_area(
            "Hypothèses / diagnostics différentiels",
            value=lv("ep_diag_notes",""), height=160,
            key=f"{key_prefix}_diag",
            placeholder="Arguments pour/contre chaque hypothèse, examens complémentaires...")
        st.markdown("---")

        # Pronostic
        st.markdown('<div class="section-title">A — Pronostic</div>', unsafe_allow_html=True)
        collected["ep_appreciation"] = st.text_area(
            "Appréciation clinique", value=lv("ep_appreciation",""), height=100,
            key=f"{key_prefix}_appr",
            placeholder="Pronostic, facteurs favorables/défavorables...")
        st.markdown("---")

        # Plan
        st.markdown('<div class="section-title">P — Plan thérapeutique</div>',
                    unsafe_allow_html=True)
        pc1, pc2 = st.columns(2)
        with pc1:
            collected["ep_objectifs"] = st.text_area("Objectifs", value=lv("ep_objectifs",""),
                height=80, key=f"{key_prefix}_obj")
            collected["ep_traitement"] = st.text_area("Modalités", value=lv("ep_traitement",""),
                height=80, key=f"{key_prefix}_trait")
        with pc2:
            collected["ep_frequence"] = st.text_input("Fréquence", value=lv("ep_frequence",""),
                key=f"{key_prefix}_freq")
            collected["ep_duree"] = st.text_input("Durée", value=lv("ep_duree",""),
                key=f"{key_prefix}_duree")
            collected["ep_education"] = st.text_area("Éducation", value=lv("ep_education",""),
                height=60, key=f"{key_prefix}_edu")
            collected["ep_autogestion"] = st.text_area("Autogestion / exercices domicile",
                value=lv("ep_autogestion",""), height=60, key=f"{key_prefix}_auto")
        return collected

    @classmethod
    def is_filled(cls, bilan_data):
        g = bilan_data.get("ep_groupe_clinique","")
        return bool(g and g not in ("—","— Non classifié —",""))

    @classmethod
    def render_evolution(cls, bilans_df, labels):
        import pandas as pd
        rows = [{"Bilan":lbl,
                 "Classification":row.get("ep_groupe_clinique","—"),
                 "Pronostic":str(row.get("ep_appreciation",""))[:80]}
                for lbl,(_,row) in zip(labels,bilans_df.iterrows())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
