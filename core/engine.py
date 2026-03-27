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

    # Tests disponibles dans la bibliothèque mais hors template
    from core.registry import all_tests as _all_tests
    all_test_ids   = list(_all_tests().keys())
    template_ids   = [cls.test_id() for cls in test_classes]
    extra_ids      = [tid for tid in all_test_ids if tid not in template_ids]
    extra_active   = [tid for tid in current_active if tid not in template_ids]

    # Sélection dans un expander AVANT les onglets
    new_active = list(current_active)
    with st.expander("🔧 Tests actifs pour ce bilan", expanded=False):
        st.markdown(
            '<div class="info-box">Décochez les tests non réalisés · '            "Cochez des tests supplémentaires depuis la bibliothèque.</div>",
            unsafe_allow_html=True)
        new_active = []

        # Tests du template
        st.markdown("**Tests du template**")
        c1, c2 = st.columns(2)
        for i, cls in enumerate(test_classes):
            col = c1 if i % 2 == 0 else c2
            with col:
                if st.checkbox(cls.tab_label(),
                               value=cls.test_id() in current_active,
                               key=f"{key_prefix}_active_{cls.test_id()}"):
                    new_active.append(cls.test_id())

        # Tests supplémentaires — recherche fuzzy + tags + IA
        if extra_ids:
            st.markdown("**Ajouter depuis la bibliothèque**")
            _all_tests_map = _all_tests()
            s1, s2 = st.columns([3, 2])
            search = s1.text_input("🔍 Rechercher un test",
                                   key=f"{key_prefix}_search_extra",
                                   placeholder="ex: épaule, équilibre, Berg, ODI…")
            ai_query = s2.text_input("🤖 Décrire le patient",
                                     key=f"{key_prefix}_ai_search",
                                     placeholder="ex: douleur épaule après chute")
            ai_result_key = f"{key_prefix}_ai_results"
            ai_prev_key   = f"{key_prefix}_ai_query_prev"
            if ai_query and st.session_state.get(ai_prev_key) != ai_query:
                st.session_state[ai_prev_key] = ai_query
                with st.spinner("Recherche IA en cours..."):
                    try:
                        import anthropic as _ant, json as _aj
                        _client = _ant.Anthropic()
                        _catalog = [{"id": tid,
                            "nom": _all_tests_map[tid].meta().get("nom",""),
                            "tags": _all_tests_map[tid].meta().get("tags",[]),
                            "desc": _all_tests_map[tid].meta().get("description","")}
                            for tid in extra_ids if tid in _all_tests_map]
                        _system = ("Tu es un assistant physiothérapeute expert. "
                            "On te donne un catalogue de tests cliniques et une description de patient. "
                            "Reponds UNIQUEMENT avec un JSON {\"ids\": [\"id1\",\"id2\",...]} "
                            "contenant les 3 a 6 IDs les plus pertinents. Rien d autre.")
                        _user = ("Catalogue: " + _aj.dumps(_catalog, ensure_ascii=False)
                            + "\n\nDescription patient: " + ai_query)
                        _msg = _client.messages.create(
                            model="claude-haiku-4-5", max_tokens=300,
                            system=_system,
                            messages=[{"role":"user","content":_user}])
                        _parsed = _aj.loads(_msg.content[0].text.strip())
                        st.session_state[ai_result_key] = _parsed.get("ids",[])
                    except Exception as _e:
                        st.session_state[ai_result_key] = []
                        st.caption(f"Erreur IA : {_e}")
            ai_suggested = st.session_state.get(ai_result_key, [])
            if ai_suggested:
                st.markdown("**Suggestions IA :**")
                a1, a2 = st.columns(2)
                for _i, _tid in enumerate(ai_suggested):
                    _ecls = _all_tests_map.get(_tid)
                    if not _ecls: continue
                    _col = a1 if _i % 2 == 0 else a2
                    with _col:
                        if st.checkbox(f"✨ {_ecls.tab_label()}",
                                       value=_tid in current_active,
                                       key=f"{key_prefix}_ai_{_tid}"):
                            if _tid not in new_active:
                                new_active.append(_tid)
                st.markdown("---")

            def _score(tid, query):
                """Retourne un score de pertinence (0=non pertinent)."""
                if not query: return 0
                ecls = _all_tests_map.get(tid)
                if not ecls: return 0
                m = ecls.meta()
                # Corpus de recherche : id + nom + tab_label + description + tags
                tags = " ".join(m.get("tags", []))
                corpus = " ".join([
                    tid, m.get("nom",""), m.get("tab_label",""),
                    m.get("description",""), tags
                ]).lower()
                words = query.lower().split()
                # Score : nombre de mots trouvés (exact ou partiel)
                score = sum(1 for w in words if w in corpus)
                # Bonus : correspondance exacte dans tags ou nom
                if any(query.lower() in t.lower() for t in m.get("tags",[])):
                    score += 3
                if query.lower() in m.get("nom","").lower():
                    score += 2
                return score

            if search:
                scored = [(tid, _score(tid, search)) for tid in extra_ids
                          if tid in _all_tests_map]
                matches = [tid for tid, s in sorted(scored, key=lambda x: -x[1]) if s > 0]
            else:
                matches = []

            if search and not matches:
                st.caption("Aucun test trouvé — essayez un autre mot-clé.")
            e1, e2 = st.columns(2)
            for i, tid in enumerate(matches):
                ecls = _all_tests_map[tid]
                col = e1 if i % 2 == 0 else e2
                with col:
                    if st.checkbox(ecls.tab_label(),
                                   value=tid in current_active,
                                   key=f"{key_prefix}_extra_{tid}"):
                        new_active.append(tid)
            # Garder cochés les extras déjà actifs même si hors recherche
            for tid in extra_active:
                if tid not in new_active and tid in _all_tests_map:
                    new_active.append(tid)

    collected["tests_actifs"] = _json.dumps(new_active)

    # Reconstruire active_classes en incluant les extras
    _all_tests_map = _all_tests()
    extra_classes  = [_all_tests_map[tid] for tid in new_active
                      if tid not in template_ids and tid in _all_tests_map]

    # Seuls les tests actifs ont un onglet (template + extras)
    active_classes = ([cls for cls in test_classes if cls.test_id() in new_active]
                      + extra_classes)

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

    # Inclure aussi les tests extras (hors template) cochés dans au moins un bilan
    from core.registry import all_tests as _all_ev_tests
    _all_ev_map    = _all_ev_tests()
    template_ids   = {cls.test_id() for cls in test_classes}
    # Collecter tous les test_ids actifs dans les bilans
    extra_ev_ids   = set()
    for _, row in bilans_df.iterrows():
        ta_raw = row.get("tests_actifs","")
        if ta_raw and ta_raw not in ("","[]","None"):
            try:
                for tid in _j.loads(ta_raw):
                    if tid not in template_ids:
                        extra_ev_ids.add(tid)
            except Exception:
                pass
    extra_ev_classes = [_all_ev_map[tid] for tid in extra_ev_ids if tid in _all_ev_map]
    all_ev_classes   = test_classes + extra_ev_classes
    visible_classes  = [cls for cls in all_ev_classes if _test_used(cls)]

    # Onglets : Synthèse IA + tests visibles
    tab_labels = ["🤖 Synthèse IA"] + [cls.tab_label() for cls in visible_classes]
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
