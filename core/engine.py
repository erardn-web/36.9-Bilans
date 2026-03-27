"""
core/engine.py — Moteur générique de formulaire et d'évolution.

Rend n'importe quelle liste de tests sans connaître leur contenu.
C'est le cœur de la nouvelle architecture.
"""

import streamlit as st
import json
from datetime import date


# ── Moteur de formulaire ──────────────────────────────────────────────────────

def render_bilan_form(bilan_id: str, bilan_data: dict, test_classes: list,
                      key_prefix: str) -> dict:
    """
    Affiche le formulaire d'un bilan avec un onglet par test.

    Args:
        bilan_id     : identifiant unique du bilan (pour les clés Streamlit)
        bilan_data   : données existantes du bilan (dict chargé depuis GSheets)
        test_classes : liste ordonnée des classes de tests à afficher
        key_prefix   : préfixe unique pour les widgets Streamlit

    Retourne : dict {clé: valeur} — toutes les valeurs à sauvegarder.
    """
    # Initialiser collected depuis les données existantes
    # (évite d'écraser les onglets non visités)
    collected = dict(bilan_data)

    def lv(key, default=""):
        """Charge une valeur depuis bilan_data."""
        v = bilan_data.get(key, default)
        return v if v is not None else default

    # Injecter le CSS pour les onglets remplis (calculé une fois)
    import json as _json

    # Lire les tests actifs sauvegardés (ou tous par défaut)
    current_active = bilan_data.get("_tests_actifs_list",
                                    [cls.test_id() for cls in test_classes])
    if isinstance(current_active, str):
        try:    current_active = _json.loads(current_active)
        except: current_active = [cls.test_id() for cls in test_classes]

    # Sélection dans un expander AVANT les onglets
    new_active = list(current_active)
    with st.expander("🔧 Tests actifs pour ce bilan", expanded=False):
        st.markdown(
            '<div class="info-box">Décochez les tests non réalisés. '
            "L'onglet disparaît immédiatement.</div>",
            unsafe_allow_html=True)
        new_active = []
        c1, c2 = st.columns(2)
        for i, cls in enumerate(test_classes):
            col = c1 if i % 2 == 0 else c2
            with col:
                if st.checkbox(cls.tab_label(),
                               value=cls.test_id() in current_active,
                               key=f"{key_prefix}_active_{cls.test_id()}"):
                    new_active.append(cls.test_id())
    collected["tests_actifs"] = _json.dumps(new_active)

    # Seuls les tests actifs ont un onglet
    active_classes = [cls for cls in test_classes if cls.test_id() in new_active]

    _inject_tab_highlight_css(active_classes, bilan_data, key_prefix)

    tab_labels = ["📝 Général"] + [cls.tab_label() for cls in active_classes]
    tabs = st.tabs(tab_labels) if len(tab_labels) > 1 else [st.container()]

    with tabs[0]:
        general = _render_general_tab(lv, key_prefix)
        collected.update(general)

    for i, test_cls in enumerate(active_classes):
        with tabs[i + 1]:
            test_data = test_cls().render(lv, f"{key_prefix}_{test_cls.test_id()}")
            collected.update(test_data)

    return collected


def _render_general_tab(lv, key_prefix: str) -> dict:
    """Onglet général commun à tous les bilans."""
    c1, c2 = st.columns(2)
    with c1:
        bilan_date = st.date_input(
            "Date du bilan",
            value=_parse_date(lv("date_bilan", str(date.today()))),
            key=f"{key_prefix}_date"
        )
        diagnostic_prescription = st.text_area(
            "Diagnostics indiqués sur la prescription",
            value=lv("diagnostic_prescription", ""),
            height=80,
            key=f"{key_prefix}_diag_prescription",
            placeholder="Ex : Lombalgie chronique, syndrome douloureux post-opératoire..."
        )

    with c2:
        praticien = st.text_input(
            "Praticien",
            value=lv("praticien", ""),
            key=f"{key_prefix}_prat"
        )
        notes = st.text_area(
            "Notes générales",
            value=lv("notes_generales", ""),
            height=80,
            key=f"{key_prefix}_notes"
        )
    return {
        "date_bilan":               str(bilan_date),
        "praticien":                praticien,
        "diagnostic_prescription":  diagnostic_prescription,
        "notes_generales":          notes,
    }


def _inject_tab_highlight_css(test_classes: list, bilan_data: dict,
                               key_prefix: str) -> None:
    """Injecte CSS pour mettre en vert les onglets remplis."""
    css_rules = []
    # Index 0 = Général (toujours blanc), index 1+ = tests
    for i, test_cls in enumerate(test_classes):
        if test_cls.is_filled(bilan_data):
            n = i + 2  # +1 pour tab Général, +1 car nth-child est 1-based
            css_rules.append(
                f"[data-baseweb='tab-list'] button:nth-child({n}) "
                "{background-color:#d4edda !important;"
                "border-bottom:3px solid #388e3c !important;}"
            )
    if css_rules:
        st.markdown(
            "<style>" + " ".join(css_rules) + "</style>",
            unsafe_allow_html=True
        )


# ── Moteur d'évolution ────────────────────────────────────────────────────────

def render_evolution_view(bilans_df, patient_info: dict,
                          test_classes: list, module_id: str,
                          patient_id: str, cas_id: str = "") -> None:
    """
    Affiche la vue d'évolution complète avec un onglet par test.

    Args:
        bilans_df    : DataFrame des bilans triés par date
        patient_info : dict avec nom, prénom, etc.
        test_classes : liste des classes de tests du template
        module_id    : identifiant du module (pour l'analyse IA)
        patient_id   : identifiant du patient
    """
    import pandas as pd
    import plotly.graph_objects as go

    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)

    labels = [
        r["date_bilan"].strftime("%d/%m/%Y")
        for _, r in bilans_df.iterrows()
    ]

    # Garder seulement les tests présents dans au moins un bilan
    import json as _j
    def _test_used(cls):
        """True si ce test a été actif dans au moins un bilan."""
        for _, row in bilans_df.iterrows():
            # Vérifier tests_actifs de ce bilan
            ta_raw = row.get("tests_actifs", "")
            if ta_raw and ta_raw not in ("","[]","None"):
                try:
                    ta = _j.loads(ta_raw)
                    if cls.test_id() in ta:
                        return True
                    # Si tests_actifs existe et ne contient pas ce test → skip
                    continue
                except Exception:
                    pass
            # Pas de tests_actifs → test considéré actif (anciens bilans)
            return True
        return False

    visible_classes = [cls for cls in test_classes if _test_used(cls)]

    # Onglets : Synthèse IA + tests visibles + Détail
    tab_labels = ["🤖 Synthèse IA"] + [cls.tab_label() for cls in visible_classes] + ["📋 Détail"]
    tabs = st.tabs(tab_labels)

    # Onglet Synthèse IA
    with tabs[0]:
        from utils.ai_analyse import render_analyse_section
        render_analyse_section(bilans_df, patient_info, module_id,
                               cas_id=cas_id or patient_id)

    # Onglets par test (visibles seulement)
    for i, test_cls in enumerate(visible_classes):
        with tabs[i + 1]:
            st.markdown(
                f'<div class="section-title">{test_cls.tab_label()} — Évolution</div>',
                unsafe_allow_html=True
            )
            test_cls.render_evolution(bilans_df, labels)

    # Onglet Détail
    with tabs[-1]:
        for i, (_, row) in enumerate(bilans_df.iterrows()):
            with st.expander(f"Bilan {i+1} — {labels[i]}"):
                if test_classes:
                    cols = st.columns(min(len(test_classes), 4))
                    for j, test_cls in enumerate(test_classes):
                        s = test_cls.score(dict(row))
                        if s["score"] is not None:
                            with cols[j % len(cols)]:
                                st.metric(test_cls.test_nom(), s["score"])
                if row.get("notes_generales"):
                    st.markdown(f"*{row['notes_generales']}*")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(val):
    """Parse une date depuis une chaîne ou retourne aujourd'hui."""
    import pandas as pd
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return date.today()


def _type_index(val: str) -> int:
    types = ["Bilan initial", "Bilan intermédiaire", "Bilan final"]
    return types.index(val) if val in types else 0


def build_tests_from_snapshot(snapshot_json: str, cabinet_config: dict = None) -> list:
    """
    Reconstruit la liste de classes de tests depuis le snapshot d'un bilan.

    Args:
        snapshot_json  : JSON stocké dans bilan_data["template_snapshot"]
        cabinet_config : config du cabinet (tests ajoutés/retirés par l'admin)

    Retourne : liste ordonnée de classes de tests.
    """
    from core.registry import get_test

    try:
        snapshot = json.loads(snapshot_json) if isinstance(snapshot_json, str) else snapshot_json
    except Exception:
        return []

    test_ids = snapshot.get("tests", [])

    # Appliquer les modifications du thérapeute si présentes
    if cabinet_config:
        for tid in cabinet_config.get("added_tests", []):
            if tid not in test_ids:
                test_ids.append(tid)
        for tid in cabinet_config.get("removed_tests", []):
            test_ids = [t for t in test_ids if t != tid]

    # Fallback uniquement si le snapshot est vide (ancien format sans tests)
    if not test_ids:
        from core.registry import all_templates
        template_id = snapshot.get("template_id", "")
        templates   = all_templates()
        if template_id in templates:
            test_ids = templates[template_id].test_ids()
        else:
            return []

    return [get_test(tid) for tid in test_ids if get_test(tid) is not None]
