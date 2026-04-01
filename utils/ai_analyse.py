"""
utils/ai_analyse.py — Analyse IA de l'évolution (copie fidèle v1, adapté v2)
Stockage : colonne analyse_ia dans la feuille Cas (une synthèse par cas)
"""
import streamlit as st

MODEL      = "claude-haiku-4-5"
MAX_TOKENS = 1200

SYSTEM_PROMPT = """Tu es un assistant physiothérapeute expert. Tu rédiges des synthèses \
d'évolution clinique en français, destinées à des médecins. 

Règles absolues :
- Tu ne poses AUCUN diagnostic médical
- Tu décris des évolutions fonctionnelles et des tendances cliniques
- Tu utilises un vocabulaire physiothérapeutique précis
- Tu mentionnes les seuils cliniques pertinents quand ils sont franchis
- Tu signales les points de vigilance ou plateaux d'évolution
- Tu restes factuel, sobre et professionnel
- La longueur cible est 200-300 mots
- Pas de titres ni de bullet points — texte courant structuré en 2-3 paragraphes"""

MODULE_CONTEXT = {
    "shv": "Syndrome d'Hyperventilation (SHV). Scores : HAD anxiété (/21, seuil pathologique >10), "
           "HAD dépression (/21, seuil >10), BOLT (secondes, normal >25s), Nijmegen (/64, seuil "
           "pathologique >23), SF-12 PCS et MCS (score composite physique/mental, moyenne "
           "population = 50), EtCO2 (mmHg, normal 35-45), pattern respiratoire, "
           "SNIF/PImax/PEmax (% valeur prédite).",
    "lombalgie": "Lombalgie. Scores : EVA repos/mouvement/nuit (/10), ODI Oswestry (/100, seuil "
                 "clinique >20%), Tampa (kinésiophobie, seuil >37), Örebro (risque chronification, "
                 "seuil >50/210), mobilité lombaire (Schober, flexion cm).",
    "equilibre": "Bilan d'équilibre et de marche. Scores : Tinetti total (/28, seuil risque élevé "
                 "<19, modéré <24), Berg Balance Scale (/56, risque élevé ≤20, modéré ≤40), "
                 "TUG en secondes (normal <10s, risque élevé ≥20s), STS 1 minute (répétitions).",
    "bpco": "BPCO / pathologie respiratoire chronique. Scores : 6MWT distance (m, bon pronostic "
            "≥400m), CAT (/40, seuil faible ≤10, sévère >20), mMRC grade (0-4), VEMS % prédit, "
            "STS 1 minute, SpO2 effort.",
    "cervicalgie": "Cervicalgie. Scores : NRS repos/mouvement/nuit (/10), NDI (/100, seuil légère "
                   ">8%, modérée >28%), HAD anxiété/dépression (/21), PSFS (activités spécifiques "
                   "/10), GROC (changement perçu -7 à +7).",
    "genou": "Genou post-chirurgical (LCA, PTG, ménisque). Scores : KOOS sous-échelles /100 "
             "(douleur, AVQ, sport, QoL — seuil bonne fonction ≥70), Lysholm /100 (excellent ≥95, "
             "bon ≥84), NRS douleur /10, TUG (secondes, normal <10s), STS 1 min (répétitions).",
    "hanche": "Hanche post-chirurgicale (PTH, fracture). Scores : HOOS sous-échelles /100 "
              "(douleur, AVQ, sport, QoL — seuil bonne fonction ≥70), NRS douleur /10, "
              "6MWT distance (m, bon pronostic ≥400m), TUG (secondes).",
    "membre_superieur": "Membre supérieur (épaule, coude, poignet). Scores : DASH /100 "
                        "(seuil légère ≤10, modérée ≤30, sévère >50), NRS douleur /10, "
                        "PSFS activités spécifiques /10, GROC changement perçu -7 à +7.",
    "epaule_douloureuse": "Épaule douloureuse. Scores : ASES /100, QuickDASH /100, "
                          "amplitudes articulaires, testing musculaire coiffe des rotateurs.",
    "genou_sport": "Genou sportif. Scores : IKDC /100, Lysholm /100, Kujala /100 (PFPS), ACL-RSI /100 (préparation psychologique retour sport, seuil ≥56).",
    "cheville": "Cheville. Scores : FAOS /100 (sous-échelles douleur/AVQ/sport), CAIT /30 (instabilité, seuil ≤27), ATRS /100 (rupture Achille).",
    "cou_tete": "Cervical/tête. Scores : NDI /100 (incapacité cervicale), DHI /100 (vertiges, seuil sévère ≥60), HIT-6 /78 (céphalées, seuil impact sévère ≥60).",
    "coude": "Coude. Scores : PRTEE /100 (épicondylalgie latérale, douleur + fonction).",
    "main": "Main/poignet. Scores : BCTQ SSS /5 et FSS /5 (canal carpien, seuil symptômes modérés ≥2.5).",
    "general_msk": "Général MSK. Scores : WOMAC /100 (arthrose genou/hanche), LEFS /80 (membres inférieurs, seuil ≥54), STarT Back (risque faible/moyen/élevé), FABQ-PA /24 (seuil ≥15) et FABQ-W /42 (seuil ≥34), DN4 /10 (neuropathique, seuil ≥4), CSI /100 (sensibilisation centrale, seuil ≥40), Roland-Morris /24 (lombalgie), QBPDS /100.",
    "urogyneco": "Urogynécologie / plancher pelvien. Scores : ICIQ-UI /21 (incontinence, seuil ≥1), PFDI-20 /300 (sous-échelles UDI, POPDI, CRADI).",
    "cardiopulmo": "Cardiopulmonaire. Scores : SGRQ /100 (qualité vie respiratoire, MCID=4), LCADL /75 (limitations AVQ respiratoires), Borg dyspnée 0-10, PSQI /21 (sommeil, seuil ≤5 bonne qualité), PCFS grade 0-4 (post-COVID).",
    "neuro_avc": "Neurologie/AVC. Scores : Barthel /100 (indépendance AVQ, seuil ≥95 indépendant), 10MWT vitesse m/s (seuil communautaire ≥0.8 m/s), Mini-BESTest /28 (équilibre, seuil chutes ≤20), FES-I /64 (peur tomber, seuil ≥23).",
    "geriatrie": "Gériatrie. Scores : Clinical Frailty Scale grade 1-9 (fragile ≥5), FRAIL Scale /5 (fragile ≥3), Vitesse marche 4m m/s (fragilité <0.8 m/s), ABC Scale % (risque chutes <67%).",
    "rhumatologie": "Rhumatologie. Scores : HAQ-DI /3 (incapacité PR, MCID=0.22), BASDAI /10 (spondylarthrite, activité élevée ≥4).",
    "douleur_chro": "Douleur chronique. Scores : PCS /52 (catastrophisation, seuil ≥30), BPI sévérité/retentissement /10, PHQ-9 /27 (dépression, seuil ≥10), GAD-7 /21 (anxiété, seuil ≥10), ISI /28 (insomnie, seuil ≥15)."}


def _format_bilans(bilans_df, module: str) -> str:
    import pandas as pd
    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)

    import json as _json_ai

    # Mapping test_id → préfixes de colonnes (filtre les tests désactivés)
    _TID_PREFIXES = {
        "spirometrie": ["spiro_"], "six_mwt": ["mwt_"], "sts": ["sts_"],
        "mmrc": ["mmrc_"], "cat": ["cat_score","cat_interpretation"],
        "bode": ["bode_"], "tinetti": ["tinetti_"], "berg": ["berg_"],
        "tug": ["tug_"], "unipodal": ["unipodal_"], "bolt": ["bolt_"],
        "nijmegen": ["nij_"], "hvt": ["hvt_"], "eva": ["eva"],
        "lombalgie": ["schober","luomajoki"], "testing_mi": ["musc_"],
        "leg_press": ["lp_"], "had": ["had_a_score","had_d_score"],
        "sf12": ["sf12_pcs","sf12_mcs"],
        # Nouveaux tests
        "nrs":     ["nrs_repos","nrs_mouvement","nrs_nuit"],
        "psfs":    ["psfs_score_moyen","psfs_activite_"],
        "groc":    ["groc_score","groc_appreciation"],
        "eq5d":    ["eq5d_"],
        "ndi":     ["ndi_score_total","ndi_score_pct"],
        "koos":    ["koos_pain","koos_symptoms","koos_adl","koos_sport","koos_qol"],
        "hoos":    ["hoos_pain","hoos_symptoms","hoos_adl","hoos_sport","hoos_qol"],
        "lysholm": ["lysholm_score_total"],
        "dash":    ["dash_score"],
        # Nouveaux tests (batch 2)
        "lefs":          ["lefs_score"],
        "womac":         ["womac_total","womac_pain","womac_func"],
        "spadi":         ["spadi_total","spadi_pain","spadi_disability"],
        "constant_murley":["cm_score_total"],
        "prtee":         ["prtee_total"],
        "bctq":          ["bctq_sss","bctq_fss"],
        "roland_morris": ["rmq_score"],
        "start_back":    ["sb_total","sb_risque"],
        "fabq":          ["fabq_pa_score","fabq_work_score"],
        "dn4":           ["dn4_score"],
        "faos":          ["faos_pain","faos_adl","faos_sport","faos_qol"],
        "kujala":        ["kujala_score"],
        "acl_rsi":       ["acl_rsi_score"],
        "visa_a":        ["visa_a_score"],
        "visa_p":        ["visa_p_score"],
        "visa_h":        ["visa_h_score"],
        "visa_g":        ["visa_g_score"],
        "cait":          ["cait_score"],
        "tegner":        ["tegner_actuel","tegner_avant"],
        "dhi":           ["dhi_score"],
        "hit6":          ["hit6_score"],
        "hagos":         ["hagos_pain","hagos_adl","hagos_sport","hagos_qol"],
        "ikdc":          ["ikdc_score"],
        "csi":           ["csi_score"],
        "qbpds":         ["qbpds_score"],
        "atrs":          ["atrs_score"],
        "wosi":          ["wosi_pct"],
    }

    lines = []
    for i, (_, row) in enumerate(bilans_df.iterrows()):
        d       = row["date_bilan"]
        dstr    = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"
        type_b  = row.get("type_bilan","") or ""
        lines.append(f"\n--- Bilan {i+1} — {dstr} ({type_b}) ---")

        # Tests actifs de CE bilan spécifiquement
        _ta_raw = str(row.get("tests_actifs","") or "")
        _active_tids = set()
        if _ta_raw and _ta_raw not in ("","[]","None","nan"):
            try:
                _active_tids = set(_json_ai.loads(_ta_raw))
            except Exception:
                pass

        skip = {"bilan_id","cas_id","patient_id","cabinet_id","date_bilan",
                "type_bilan","praticien","notes_generales","date_creation",
                "donnees","analyse_ia","tests_actifs"}

        def _col_active_for_row(col):
            if not _active_tids:
                return True  # rétro-compat : pas de filtre si tests_actifs absent
            _always = {"diagnostic_prescription","diag_notes","poids_kg","taille_cm",
                       "bmi","fc_repos","fr_repos","ta_repos","spo2_repos"}
            if col in _always:
                return True
            for tid, pfxs in _TID_PREFIXES.items():
                if any(col == p or col.startswith(p) for p in pfxs):
                    return tid in _active_tids
            return True  # colonnes non mappées → inclure

        for col in bilans_df.columns:
            if col in skip: continue
            if not _col_active_for_row(col): continue
            val = row.get(col,"")
            if val is None or str(val).strip() in ("","0","0.0","None","nan"): continue
            # Exclure les items individuels (had_a1, sf12_q1…)
            if any(col.endswith(f"_{x}") for x in
                   list("abcdefghij") + [str(i) for i in range(1,20)]):
                continue
            lines.append(f"  {col}: {val}")
    return "\n".join(lines)


def generate_analyse(bilans_df, patient_info: dict, module: str) -> str:
    patient_name = f"{patient_info.get('nom','')} {patient_info.get('prenom','')}".strip()
    n_bilans = len(bilans_df)
    context  = MODULE_CONTEXT.get(module, "")
    data_str = _format_bilans(bilans_df, module)

    user_prompt = f"""Rédige une synthèse physiothérapeutique de l'évolution du patient \
{patient_name} sur {n_bilans} bilan(s).

Contexte clinique : {context}

Données des bilans :
{data_str}

Rédige une synthèse clinique structurée destinée au médecin traitant. \
Décris l'évolution fonctionnelle, les progrès ou stagnations observés, \
les seuils cliniques franchis, et les points de vigilance. \
N'émets aucun diagnostic médical."""

    try:
        try:
            api_key = str(st.secrets["ANTHROPIC_API_KEY"]).strip()
        except KeyError:
            return "⚠️ Clé API Anthropic manquante — ajoutez ANTHROPIC_API_KEY dans les secrets Streamlit."

        import anthropic
        client  = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role":"user","content":user_prompt}],
        )
        return message.content[0].text
    except Exception as e:
        return f"⚠️ Erreur lors de la génération : {str(e)}"


def load_analyse_cas(cas_id: str) -> str:
    """Charge la synthèse IA stockée dans la feuille Cas."""
    from utils.db import get_cas
    cas = get_cas(cas_id)
    return cas.get("analyse_ia","") if cas else ""


def save_analyse_cas(cas_id: str, texte: str) -> bool:
    """Sauvegarde la synthèse IA dans la feuille Cas.
    Si la colonne analyse_ia manque, la crée d'abord."""
    from utils.db import _update_row, _invalidate_read_cache, _ws, _get_spreadsheet
    ok = _update_row("Cas", "cas_id", cas_id, {"analyse_ia": texte})
    if not ok:
        # Colonne manquante — ajouter et réessayer
        try:
            ws = _ws("Cas")
            headers = ws.row_values(1)
            if "analyse_ia" not in headers:
                ws.resize(cols=len(headers)+1)
                import gspread
                ws.update_cell(1, len(headers)+1, "analyse_ia")
                _invalidate_read_cache()
            ok = _update_row("Cas", "cas_id", cas_id, {"analyse_ia": texte})
        except Exception:
            pass
    if ok:
        _invalidate_read_cache()
    return ok


def render_analyse_section(bilans_df, patient_info: dict, module: str, cas_id: str):
    """
    Affiche le bloc analyse IA dans la page d'évolution.
    Gère la génération, l'édition et la sauvegarde.
    """
    st.markdown("---")
    st.markdown("### 🤖 Synthèse physiothérapeutique (IA)")

    session_key = f"analyse_text_{cas_id}"
    stale_key   = f"analyse_stale_{cas_id}"
    is_stale    = st.session_state.get(stale_key, False)

    if session_key not in st.session_state:
        st.session_state[session_key] = load_analyse_cas(cas_id)

    analyse_text = st.session_state[session_key]

    if is_stale:
        btn_label = "🔄 Regénérer (bilan modifié)"
    elif not analyse_text:
        btn_label = "🤖 Générer la synthèse"
    else:
        btn_label = "🔄 Regénérer"

    col_gen, col_save, col_info = st.columns([2, 1.5, 4])
    with col_gen:
        confirm_key = f"confirm_regen_{cas_id}"
        if st.button(btn_label, key=f"btn_gen_{cas_id}", type="primary"):
            if analyse_text and not is_stale:
                # Synthèse existante éditée manuellement — demander confirmation
                st.session_state[confirm_key] = True
            else:
                with st.spinner("Analyse en cours…"):
                    # Utiliser bilans_df déjà filtré (bilans sélectionnés + tests actifs)
                    new_text = generate_analyse(bilans_df, patient_info, module)
                st.session_state[session_key] = new_text
                save_analyse_cas(cas_id, new_text)
                st.session_state.pop(stale_key, None)
                st.session_state.pop(confirm_key, None)
                st.rerun()

        if st.session_state.get(confirm_key):
            st.warning("⚠️ Vous avez une synthèse éditée. La regénérer l\'écrasera définitivement.")
            ca, cb = st.columns(2)
            if ca.button("✅ Regénérer quand même", key=f"confirm_yes_{cas_id}"):
                with st.spinner("Analyse en cours…"):
                    # Utiliser bilans_df déjà filtré (bilans sélectionnés + tests actifs)
                    new_text = generate_analyse(bilans_df, patient_info, module)
                st.session_state[session_key] = new_text
                save_analyse_cas(cas_id, new_text)
                st.session_state.pop(stale_key, None)
                st.session_state.pop(confirm_key, None)
                st.rerun()
            if cb.button("❌ Annuler", key=f"confirm_no_{cas_id}"):
                st.session_state.pop(confirm_key, None)
                st.rerun()

    with col_info:
        if is_stale:
            st.warning("⚠️ Un bilan a été modifié — synthèse à régénérer.")
        elif not analyse_text:
            st.caption("Cliquez sur 'Générer' pour produire une synthèse.")

    if analyse_text:
        edited = st.text_area(
            "Synthèse", value=analyse_text, height=220,
            key=f"ta_{cas_id}", label_visibility="collapsed",
        )
        with col_save:
            if st.button("💾 Sauvegarder", key=f"save_ia_{cas_id}"):
                st.session_state[session_key] = edited
                ok = save_analyse_cas(cas_id, edited)
                if ok:
                    st.success("✅ Sauvegardé.")
                else:
                    st.error("❌ Échec sauvegarde GSheets.")
        st.caption("💡 Cette synthèse sera incluse dans le prochain export PDF.")
