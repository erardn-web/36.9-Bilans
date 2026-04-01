"""
pages/1_Bilans.py — Dossier patient → Cas → Bilans (UX fidèle v1)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date

# ── Charger tests et templates (une seule fois par session) ──────────────────
@st.cache_resource
def _load_templates():
    """Chargé une seule fois par session — tous les tests + templates."""
    from tests.questionnaires.had              import HAD              # noqa
    from tests.questionnaires.sf12             import SF12             # noqa
    from tests.questionnaires.nijmegen         import Nijmegen         # noqa
    from tests.questionnaires.mrc_dyspnee      import MRCDyspnee      # noqa
    from tests.questionnaires.comorbidites     import Comorbidites     # noqa
    from tests.tests_cliniques.bolt             import BOLT             # noqa
    from tests.tests_cliniques.hvt              import HVT              # noqa
    from tests.tests_cliniques.gazometrie       import Gazometrie       # noqa
    from tests.tests_cliniques.pattern_respi    import PatternRespi     # noqa
    from tests.tests_cliniques.snif_pimax_pemax import SNIFPimaxPemax  # noqa
    from tests.tests_cliniques.testing_mi       import TestingMI        # noqa
    from tests.tests_cliniques.leg_press        import LegPress         # noqa
    from tests.tests_cliniques.tinetti          import Tinetti          # noqa
    from tests.tests_cliniques.berg             import Berg             # noqa
    from tests.tests_cliniques.tug              import TUG              # noqa
    from tests.tests_cliniques.sts              import STS              # noqa
    from tests.tests_cliniques.unipodal         import Unipodal         # noqa
    from tests.tests_cliniques.six_mwt          import SixMWT           # noqa
    from tests.tests_cliniques.sppb             import SPPB             # noqa
    from tests.tests_cliniques.spirometrie      import Spirometrie      # noqa
    from tests.tests_cliniques.mmrc             import MMRC             # noqa
    from tests.tests_cliniques.cat              import CAT              # noqa
    from tests.tests_cliniques.bode             import BODE             # noqa
    from tests.tests_cliniques.eva              import EVA              # noqa
    from tests.tests_cliniques.drapeaux         import Drapeaux         # noqa
    from tests.tests_cliniques.mobilite_lombaire import MobiliteLombaire # noqa
    from tests.tests_cliniques.odi              import ODI              # noqa
    from tests.tests_cliniques.tampa            import Tampa            # noqa
    from tests.tests_cliniques.orebro           import Orebro           # noqa
    import templates.shv        # noqa
    import templates.equilibre  # noqa
    import templates.bpco       # noqa
    import templates.lombalgie  # noqa
    import templates.neutre              # noqa
    from tests.tests_cliniques.quick_dash            import QuickDASH            # noqa
    from tests.tests_cliniques.ases                  import ASES                  # noqa
    from tests.tests_cliniques.amplitudes_epaule     import AmplitudesEpaule     # noqa
    from tests.tests_cliniques.testing_epaule        import TestingEpaule        # noqa
    from tests.tests_cliniques.tests_epaule_speciaux import TestsEpauleSpeciaux  # noqa
    from tests.tests_cliniques.classification_epaule import ClassificationEpaule # noqa
    import templates.epaule_douloureuse  # noqa
    return True

try:
    _load_templates()
except Exception as _e:
    import traceback
    st.error(f"Erreur chargement : {_e}")
    st.code(traceback.format_exc())
    st.stop()

from utils.pdf import generate_pdf, generate_questionnaires_pdf
from utils.ai_analyse import load_analyse_cas
from utils.db import (
    get_all_patients, create_patient, update_patient, search_patients,
    get_patient_cas, create_cas, get_cas, set_cas_statut,
    get_cas_bilans, get_cas_bilans_meta, create_bilan, get_bilan_donnees,
    save_bilan_donnees, get_tests_actifs, get_audit_log,
    get_bilan_tests_actifs, save_bilan_tests_actifs,
    delete_bilan,
    get_medecin_destinataire, save_medecin_destinataire,
)
from core.registry import all_templates
from core.engine   import render_bilan_form, render_evolution_view, build_tests_from_snapshot
from core.registry import all_tests as _all_tests


def _ensure_registry():
    """S'assure que le registre est peuplé — toujours vérifier le registre réel."""
    from core.registry import all_tests
    if all_tests():
        return  # Registre déjà peuplé
    # Registre vide — (re)importer les tests
    try:
        from tests.questionnaires.had              import HAD              # noqa
        from tests.questionnaires.sf12             import SF12             # noqa
        from tests.questionnaires.nijmegen         import Nijmegen         # noqa
        from tests.questionnaires.mrc_dyspnee      import MRCDyspnee      # noqa
        from tests.questionnaires.comorbidites     import Comorbidites     # noqa
        from tests.tests_cliniques.bolt             import BOLT             # noqa
        from tests.tests_cliniques.hvt              import HVT              # noqa
        from tests.tests_cliniques.gazometrie       import Gazometrie       # noqa
        from tests.tests_cliniques.pattern_respi    import PatternRespi     # noqa
        from tests.tests_cliniques.snif_pimax_pemax import SNIFPimaxPemax  # noqa
        from tests.tests_cliniques.testing_mi       import TestingMI        # noqa
        from tests.tests_cliniques.leg_press        import LegPress         # noqa
        from tests.tests_cliniques.tinetti          import Tinetti          # noqa
        from tests.tests_cliniques.berg             import Berg             # noqa
        from tests.tests_cliniques.tug              import TUG              # noqa
        from tests.tests_cliniques.sts              import STS              # noqa
        from tests.tests_cliniques.unipodal         import Unipodal         # noqa
        from tests.tests_cliniques.six_mwt          import SixMWT           # noqa
        from tests.tests_cliniques.sppb             import SPPB             # noqa
        from tests.tests_cliniques.spirometrie      import Spirometrie      # noqa
        from tests.tests_cliniques.mmrc             import MMRC             # noqa
        from tests.tests_cliniques.cat              import CAT              # noqa
        from tests.tests_cliniques.bode             import BODE             # noqa
        from tests.tests_cliniques.eva              import EVA              # noqa
        from tests.tests_cliniques.drapeaux         import Drapeaux         # noqa
        from tests.tests_cliniques.mobilite_lombaire        import MobiliteLombaire        # noqa
        from tests.tests_cliniques.luomajoki                import Luomajoki                # noqa
        from tests.tests_cliniques.tests_objectifs_lombaire import TestsObjectifsLombaire  # noqa
        from tests.tests_cliniques.classification_lombaire  import ClassificationLombaire  # noqa
        from tests.tests_cliniques.quick_dash            import QuickDASH            # noqa
        from tests.tests_cliniques.ases                  import ASES                  # noqa
        from tests.tests_cliniques.amplitudes_epaule     import AmplitudesEpaule     # noqa
        from tests.tests_cliniques.testing_epaule        import TestingEpaule        # noqa
        from tests.tests_cliniques.tests_epaule_speciaux import TestsEpauleSpeciaux  # noqa
        from tests.tests_cliniques.classification_epaule import ClassificationEpaule # noqa
        from tests.tests_cliniques.quick_dash            import QuickDASH            # noqa
        from tests.tests_cliniques.ases                  import ASES                  # noqa
        from tests.tests_cliniques.amplitudes_epaule     import AmplitudesEpaule     # noqa
        from tests.tests_cliniques.testing_epaule        import TestingEpaule        # noqa
        from tests.tests_cliniques.tests_epaule_speciaux import TestsEpauleSpeciaux  # noqa
        from tests.tests_cliniques.classification_epaule import ClassificationEpaule # noqa
        from tests.tests_cliniques.odi              import ODI              # noqa
        from tests.tests_cliniques.tampa            import Tampa            # noqa
        from tests.tests_cliniques.orebro           import Orebro           # noqa
    except Exception as _e:
        st.error(f"Erreur import tests : {_e}")
        return
    # Enregistrer les templates si manquants
    from core.registry import all_templates as _at
    _templates = _at()
    if "shv" not in _templates:
        import templates.shv        # noqa — auto-enregistre via register_template
    if "equilibre" not in _templates:
        import templates.equilibre  # noqa
    if "bpco" not in _templates:
        import templates.bpco       # noqa
    if "lombalgie" not in _templates:
        import templates.lombalgie           # noqa
        import templates.epaule_douloureuse  # noqa

# ── CSS (copie fidèle v1) ─────────────────────────────────────────────────────
st.markdown("""
<style>
.main .block-container { max-width:1200px; padding:1rem 3rem; }
.block-container { max-width:1200px !important; }
.page-title   { font-size:2rem; font-weight:700; color:#1a3c5e; }
.section-title{ font-size:1.15rem; font-weight:600; color:#1a3c5e;
                border-bottom:2px solid #e0ecf8; padding-bottom:4px; margin-bottom:1rem; }
.score-box    { border-radius:10px; padding:1rem; text-align:center; color:white;
                font-size:1.4rem; font-weight:700; }
.info-box     { background:#f0f7ff; border-left:4px solid #1a3c5e;
                padding:0.8rem 1rem; border-radius:0 8px 8px 0; margin-bottom:1rem; }
.warn-box     { background:#fff8e1; border-left:4px solid #f9a825;
                padding:0.8rem 1rem; border-radius:0 8px 8px 0; margin-bottom:1rem; }
.success-box  { background:#e8f5e9; border-left:4px solid #388e3c;
                padding:0.8rem 1rem; border-radius:0 8px 8px 0; margin-bottom:1rem; }
.patient-badge{ background:#1a3c5e; color:white; border-radius:8px;
                padding:0.4rem 1rem; display:inline-block; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Session ───────────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "mode":        "accueil",
        "patient_id":  None, "patient_info": {},
        "cas_id":      None, "cas_info":     {},
        "bilan_id":    None, "bilan_data":   {},
        "cabinet_id":  "default",
        "therapeute":  st.session_state.get("therapeute",""),
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()
S = st.session_state

def _go(mode, **kwargs):
    S.mode = mode
    for k,v in kwargs.items():
        S[k] = v
    st.rerun()

def _back_to_cas():
    if S.cas_id:
        cas_info = get_cas(S.cas_id)
        if cas_info: S.cas_info = cas_info
    _go("cas")


def _sidebar_context(unsaved=False):
    """Fil d'Ariane cliquable dans la sidebar."""
    import json as _jsc
    with st.sidebar:
        # Construire les segments
        _segs = []  # (label, action_fn or None)

        _segs.append(("🏥 Bilans", lambda: _go("accueil")))

        if S.get("patient_id") and S.get("patient_info"):
            _pi   = S.patient_info
            _nom  = f"{_pi.get('nom','')} {_pi.get('prenom','')}".strip()
            _segs.append((f"👤 {_nom}", lambda: _go("dossier")))

        if S.get("cas_id") and S.get("cas_info"):
            try:
                _snap = _jsc.loads(S.cas_info.get("template_snapshot","{}") or "{}")
            except Exception:
                _snap = {}
            _cname = _snap.get("nom", S.cas_info.get("template_id","—"))
            _segs.append((f"📂 {_cname}", lambda: _back_to_cas()))

        if S.mode == "formulaire":
            _segs.append(("📋 Bilan", None))
        elif S.mode == "evolution":
            _segs.append(("📈 Évolution", None))
        elif S.mode == "impression":
            # Bilan cliquable, puis Impression comme page active
            _bid = S.get("bilan_id")
            _segs.append(("📋 Bilan", lambda: _go("formulaire", bilan_id=_bid,
                                                   bilan_data=S.bilan_data)))
            _segs.append(("🖨️ Impression", None))

        # Confirmation navigation non sauvegardée
        if S.get("_sb_confirm"):
            st.warning("⚠️ Non sauvegardé — quitter ?")
            _c1, _c2 = st.columns(2)
            if _c1.button("✅ Oui", key="sb_yes", use_container_width=True):
                _dest_fn = S.pop("_sb_confirm")
                S.pop("_bilan_unsaved", None)
                _dest_fn()
            if _c2.button("❌ Non", key="sb_no", use_container_width=True):
                S.pop("_sb_confirm", None)
                st.rerun()
            st.markdown("---")
            return

        # Style liens discrets (masque l'apparence bouton)
        st.markdown("""<style>
        div[data-testid="stSidebar"] .bc-btn button {
            background: none !important;
            border: none !important;
            padding: 2px 0 !important;
            color: #2B57A7 !important;
            font-size: 0.85rem !important;
            font-weight: 400 !important;
            text-align: left !important;
            box-shadow: none !important;
            text-decoration: underline !important;
            cursor: pointer !important;
            width: auto !important;
        }
        div[data-testid="stSidebar"] .bc-btn button:hover {
            color: #1a3c5e !important;
        }
        </style>""", unsafe_allow_html=True)

        # Affichage fil d'Ariane sobre
        st.markdown(
            "<div style='font-size:0.7rem;color:#aaa;text-transform:uppercase;"
            "letter-spacing:.08em;margin-bottom:6px'>📍 Vous êtes ici</div>",
            unsafe_allow_html=True)
        for i, (label, fn) in enumerate(_segs):
            is_last = (i == len(_segs) - 1)
            _sep = " › " if i > 0 else ""
            if is_last or fn is None:
                st.markdown(
                    f"<span style='font-size:0.85rem;font-weight:600;"
                    f"color:#1a3c5e'>{_sep}{label}</span>",
                    unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bc-btn">', unsafe_allow_html=True)
                if st.button(f"{_sep}{label}", key=f"sb_{i}_{S.mode}"):
                    if unsaved:
                        S["_sb_confirm"] = fn
                        st.rerun()
                    else:
                        fn()
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

# ── ACCUEIL — recherche gauche / créer droite (v1) ────────────────────────────
def render_accueil():
    st.markdown('<div class="page-title">🏥 36.9 Bilans</div>', unsafe_allow_html=True)
    st.markdown("##### Plateforme de bilans physiothérapeutiques")
    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🔍 Rechercher un patient existant")
        search = st.text_input("Recherche (nom, prénom)…", key="search_input",
                               placeholder="Dupont, Marie…")
        if len(search.strip()) < 2:
            if not search.strip():
                st.caption("Tapez au moins 2 caractères pour rechercher.")
            else:
                st.caption("Continuez à taper…")
            filtered = None
        else:
            filtered = search_patients(search, S.cabinet_id)

            if filtered is None:
                pass
            elif filtered.empty:
                st.warning("Aucun résultat.")
            else:
                for _, row in filtered.iterrows():
                    c1, c2 = st.columns([3,1])
                    with c1:
                        n_open  = 0  # compté via dossier
                        badge   = f" &nbsp;<span style='color:#388e3c;font-size:.85rem'>● {n_open} cas</span>" if n_open else ""
                        st.markdown(
                            f"**{row['nom']} {row['prenom']}** &nbsp;|&nbsp; "
                            f"{row.get('date_naissance','—')}{badge}",
                            unsafe_allow_html=True)
                    with c2:
                        if st.button("Sélectionner", key=f"sel_{row['patient_id']}"):
                            _go("dossier", patient_id=row["patient_id"],
                                patient_info=row.to_dict())

    with col_b:
        st.markdown("#### ➕ Créer un nouveau patient")
        with st.form("form_new_patient", clear_on_submit=True):
            nom    = st.text_input("Nom *")
            prenom = st.text_input("Prénom *")
            ddn    = st.date_input("Date de naissance *",
                                   value=None,
                                   min_value=date(1900,1,1), max_value=date.today())
            sexe   = st.selectbox("Sexe", ["— Non renseigné —","Féminin","Masculin","Non-binaire"])
            submitted = st.form_submit_button("➕ Créer", type="primary")

        if submitted:
            if not nom or not prenom:
                st.error("Nom et prénom obligatoires.")
            else:
                sexe_val = "" if sexe == "— Non renseigné —" else sexe
                ddn_str = str(ddn) if ddn is not None else ""
                with st.spinner("Enregistrement…"):
                    pid = create_patient(nom, prenom, ddn_str, sexe_val, S.cabinet_id)
                patients_df2 = get_all_patients(S.cabinet_id)
                rows2 = patients_df2[patients_df2["patient_id"]==pid]
                if not rows2.empty:
                    _go("dossier", patient_id=pid, patient_info=rows2.iloc[0].to_dict())

# ── DOSSIER PATIENT ───────────────────────────────────────────────────────────
def render_dossier():
    _sidebar_context()
    info = S.patient_info
    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")} '
        f'— {info.get("date_naissance","—")} — ID : {info.get("patient_id","")}</div>',
        unsafe_allow_html=True)
    st.markdown("")

    col_new, col_edit, _ = st.columns([1,1,4])
    with col_new:
        if st.button("➕ Nouveau cas", type="primary"):
            _go("choisir_template")
    with col_edit:
        if st.button("✏️ Modifier patient"):
            S["show_edit_patient"] = not S.get("show_edit_patient", False)

    # Formulaire de modification patient
    if S.get("show_edit_patient"):
        with st.form("form_edit_patient"):
            st.markdown("**Modifier les informations du patient**")
            e1, e2 = st.columns(2)
            with e1:
                new_nom    = st.text_input("Nom", value=info.get("nom",""))
                new_prenom = st.text_input("Prénom", value=info.get("prenom",""))
            with e2:
                ddn_val = None
                try:
                    import pandas as _pd
                    ddn_val = _pd.to_datetime(info.get("date_naissance","")).date()
                except Exception:
                    pass
                new_ddn  = st.date_input("Date de naissance", value=ddn_val,
                                         min_value=date(1900,1,1), max_value=date.today())
                sexe_opts = ["— Non renseigné —","Féminin","Masculin","Non-binaire"]
                cur_sexe  = info.get("sexe","")
                sexe_idx  = sexe_opts.index(cur_sexe) if cur_sexe in sexe_opts else 0
                new_sexe  = st.selectbox("Sexe", sexe_opts, index=sexe_idx)
            save_btn = st.form_submit_button("💾 Sauvegarder", type="primary")
            if save_btn:
                sexe_val = "" if new_sexe == "— Non renseigné —" else new_sexe
                ok = update_patient(info["patient_id"], new_nom, new_prenom,
                                    str(new_ddn), sexe_val)
                if ok:
                    # Mettre à jour session_state
                    S.patient_info.update({
                        "nom": new_nom.upper().strip(),
                        "prenom": new_prenom.strip(),
                        "date_naissance": str(new_ddn),
                        "sexe": sexe_val,
                    })
                    S["show_edit_patient"] = False
                    st.success("✅ Patient mis à jour.")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la mise à jour.")

    st.markdown("---")
    cas_df = get_patient_cas(S.patient_id)
    if cas_df.empty:
        st.info("Aucun cas pour ce patient.")
        return

    ouverts = cas_df[cas_df["statut"]=="ouvert"]
    clos    = cas_df[cas_df["statut"]=="clos"]

    if not ouverts.empty:
        st.markdown("#### 📂 Cas ouverts")
        _render_cas_list(ouverts)
    if not clos.empty:
        st.markdown("#### 🗄️ Cas clos")
        _render_cas_list(clos, is_clos=True)


def _render_cas_list(df, is_clos=False):
    import json as _j
    for _, cas in df.iterrows():
        cid = cas["cas_id"]
        try:  snap = _j.loads(cas.get("template_snapshot","{}") or "{}")
        except: snap = {}
        nom_t    = snap.get("nom", cas.get("template_id","—"))
        date_ouv = cas.get("date_ouverture","")
        prat     = cas.get("praticien_creation","")
        # Count bilans without full load (use cached data)
        try:
            _bl = get_cas_bilans_meta(cid)
            n_bil = len(_bl)
        except Exception:
            n_bil = 0

        c1, c2, c3, c4 = st.columns([3,1,1,1])
        with c1:
            statut = ('<span style="color:#888">○ Clos</span>'
                      if is_clos else
                      '<span style="color:#388e3c;font-weight:600">● Ouvert</span>')
            st.markdown(
                f"**{nom_t}** &nbsp; {statut} &nbsp; "
                f"<small>{date_ouv} · {prat} · {n_bil} bilan(s)</small>",
                unsafe_allow_html=True)
        with c2:
            if st.button("📋 Ouvrir", key=f"cas_{cid}"):
                _go("cas", cas_id=cid, cas_info=cas.to_dict())
        with c3:
            if st.button("📈 Évolution", key=f"ev_{cid}"):
                sel_key = f"sel_bilans_{cid}"
                _go("evolution", cas_id=cid, cas_info=cas.to_dict(),
                    selected_bilans=S.get(sel_key,[]))
        with c4:
            if is_clos:
                if st.button("🔄 Rouvrir", key=f"ro_{cid}"):
                    set_cas_statut(cid,"ouvert",S.therapeute); st.rerun()
            else:
                if st.button("🔒 Clore", key=f"cl_{cid}"):
                    set_cas_statut(cid,"clos",S.therapeute); st.rerun()

        with st.expander("🕐 Historique", expanded=False):
            audit = get_audit_log(cid)
            if audit.empty: st.caption("Aucun historique.")
            else:
                st.dataframe(audit.rename(columns={
                    "timestamp":"Date/heure","therapeute":"Thérapeute","action":"Action"}),
                    hide_index=True, use_container_width=True)
        st.markdown("---")

# ── CHOISIR TEMPLATE ──────────────────────────────────────────────────────────
def render_choisir_template():
    _sidebar_context()
    info = S.patient_info
    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")}'
        f' — Nouveau cas</div>', unsafe_allow_html=True)

    _ensure_registry()
    templates = all_templates()
    if not templates:
        st.warning("Aucun template disponible."); return

    if S.get("_creating_cas"):
        st.info("Création en cours…"); return

    # ── Étape 1 : choisir le type de cas ─────────────────────────────────────
    st.markdown("### Choisir le type de cas")

    def _create_cas_go(tid, tmpl):
        S["_creating_cas"] = True
        with st.spinner(f"Création du cas {tmpl.nom}…"):
            cid = create_cas(S.patient_id, tmpl, S.therapeute, S.cabinet_id)
            cas_info = get_cas(cid)
        S["_creating_cas"] = False
        S.pop("ai_tmpl_results", None)
        _go("cas", cas_id=cid, cas_info=cas_info)

    # Neutre toujours en premier
    tmpl_list = []
    if "neutre" in templates:
        tmpl_list.append(("neutre", templates["neutre"]))
    for tid, tmpl in templates.items():
        if tid != "neutre":
            tmpl_list.append((tid, tmpl))

    # Barres de recherche
    sr1, sr2 = st.columns([3, 2])
    search_tmpl = sr1.text_input("🔍 Rechercher", key="search_tmpl",
                                  placeholder="ex: lombalgie, épaule, BPCO…")
    ai_tmpl_q   = sr2.text_input("🤖 Décrire le patient", key="ai_search_tmpl",
                                  placeholder="ex: douleur épaule droite")

    # Recherche IA
    if ai_tmpl_q and S.get("ai_tmpl_query_prev") != ai_tmpl_q:
        S["ai_tmpl_query_prev"] = ai_tmpl_q
        with st.spinner("Recherche IA…"):
            try:
                import anthropic as _ant, json as _aj, re as _re
                _catalog = [{"id": tid, "nom": tmpl.nom,
                             "description": tmpl.description}
                            for tid, tmpl in tmpl_list]
                _msg = _ant.Anthropic().messages.create(
                    model="claude-haiku-4-5", max_tokens=200,
                    system=('Tu es un assistant physiothérapeute. '
                            'Reponds UNIQUEMENT avec un JSON {"ids":[...]} '
                            'avec les IDs de templates les plus pertinents.'),
                    messages=[{"role":"user","content":
                        "Catalogue: " + _aj.dumps(_catalog, ensure_ascii=False) +
                        "\nPatient: " + ai_tmpl_q}])
                _m = _re.search(r'\{"ids":\s*\[[^\]]*\]\}', _msg.content[0].text)
                S["ai_tmpl_results"] = _aj.loads(_m.group()).get("ids",[]) if _m else []
            except Exception:
                S["ai_tmpl_results"] = []

    ai_suggested = S.get("ai_tmpl_results", [])
    if ai_suggested:
        st.markdown("**✨ Suggestions IA :**")
        ai_cols = st.columns(min(len(ai_suggested), 4))
        for i, tid in enumerate(ai_suggested):
            tmpl = templates.get(tid)
            if not tmpl: continue
            with ai_cols[i % 4]:
                if st.button(f"✨ {tmpl.icone} {tmpl.nom}",
                             key=f"ai_tmpl_{tid}", use_container_width=True):
                    _create_cas_go(tid, tmpl)
        st.markdown("---")

    # Filtrage textuel fuzzy
    if search_tmpl:
        from utils.search import search_items
        def _tmpl_key(t):
            return f"{t[1].nom} {t[1].description}", []
        visible = search_items(search_tmpl, tmpl_list, _tmpl_key)
    else:
        visible = tmpl_list

    if not visible:
        st.caption("Aucun template trouvé.")
    else:
        cols = st.columns(min(len(visible), 4))
        for i, (tid, tmpl) in enumerate(visible):
            with cols[i % 4]:
                if st.button(f"{tmpl.icone} {tmpl.nom}", key=f"tmpl_{tid}",
                             use_container_width=True):
                    _create_cas_go(tid, tmpl)

# ── VUE CAS — liste bilans gauche / créer droite (v1) ─────────────────────────
def render_cas():
    _sidebar_context()
    import json as _j
    info = S.patient_info
    cas  = S.cas_info
    try:  snap = _j.loads(cas.get("template_snapshot","{}") or "{}")
    except: snap = {}
    nom_t = snap.get("nom", cas.get("template_id","Cas"))

    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")} '
        f'— {nom_t}</div>', unsafe_allow_html=True)
    st.markdown("")

    # Barre d'actions
    col_evol, _ = st.columns([1.5,5])
    with col_evol:
        if st.button("📈 Voir l'évolution", type="primary"):
            sel_key = f"sel_bilans_{S.cas_id}"
            _go("evolution", cas_id=S.cas_id, cas_info=cas,
                selected_bilans=S.get(sel_key,[]))

    st.markdown("---")
    col_left, col_right = st.columns(2)

    # ── Gauche : bilans existants ─────────────────────────────────────────────
    with col_left:
        h1, h2 = st.columns([2, 1])
        with h1:
            st.markdown("#### 📋 Bilans existants")
        bilans_df = get_cas_bilans_meta(S.cas_id)
        if bilans_df.empty:
            st.info("Aucun bilan pour ce cas.")
        else:
            sel_key = f"sel_bilans_{S.cas_id}"
            if sel_key not in S:
                S[sel_key] = []
            for _, b in bilans_df.iterrows():
                bid2 = b["bilan_id"]
                d    = b.get("date_bilan","")
                ds   = d.strftime("%d/%m/%Y") if hasattr(d,"strftime") else str(d)[:10]
                prat = b.get("praticien","") or ""
                bc1, bc2, bc3, bc4 = st.columns([0.3, 2.5, 1, 1])
                with bc1:
                    checked = st.checkbox("", value=bid2 in S[sel_key],
                                         key=f"sel_{bid2}", label_visibility="collapsed")
                    if checked and bid2 not in S[sel_key]:
                        S[sel_key].append(bid2)
                    elif not checked and bid2 in S[sel_key]:
                        S[sel_key].remove(bid2)
                with bc2:
                    st.markdown(f"**{ds}** &nbsp; {prat}")
                with bc3:
                    if st.button("✏️", key=f"edit_{bid2}", help="Ouvrir"):
                        donnees = get_bilan_donnees(bid2)
                        _go("formulaire", bilan_id=bid2, bilan_data=donnees)
                with bc4:
                    if st.button("🗑️", key=f"del_{bid2}", help="Supprimer"):
                        S[f"confirm_del_{bid2}"] = True
                if S.get(f"confirm_del_{bid2}"):
                    st.warning(f"Supprimer le bilan du {ds} ?")
                    da, db2 = st.columns(2)
                    if da.button("✅ Oui", key=f"yes_del_{bid2}"):
                        from utils.db import delete_bilan
                        delete_bilan(bid2, S.therapeute)
                        S.pop(f"confirm_del_{bid2}", None)
                        get_cas_bilans_meta.clear()
                        get_cas_bilans.clear()
                        # Invalider le cache IA — les bilans ont changé
                        S.pop(f"analyse_text_{S.cas_id}", None)
                        S.pop(f"analyse_sig_{S.cas_id}", None)
                        st.rerun()
                    if db2.button("❌ Non", key=f"no_del_{bid2}"):
                        S.pop(f"confirm_del_{bid2}", None)
                        st.rerun()

    # ── Droite : créer un nouveau bilan ───────────────────────────────────────
    with col_right:
        st.markdown("#### ➕ Nouveau bilan")
        with st.form("form_new_bilan"):
            bilan_date = st.date_input("Date", value=date.today())
            praticien  = st.text_input("Praticien", value=S.therapeute or "")
            ok = st.form_submit_button("➕ Créer", type="primary")

    if ok:
        with st.spinner("Création du bilan…"):
            bid = create_bilan(S.cas_id, praticien,
                               bilan_date, S.cabinet_id)
        S.pop("_bilan_unsaved", None)
        _go("formulaire", bilan_id=bid, bilan_data={})

    # ── Médecin destinataire ──────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📋 Médecin destinataire (pour le PDF d'évolution)", expanded=False):
        _med = get_medecin_destinataire(S.cas_id)
        with st.form("form_medecin_destinataire"):
            m1, m2 = st.columns(2)
            with m1:
                _med_nom  = st.text_input("Nom du médecin",
                    value=_med.get("nom", ""),
                    placeholder="ex: Dupont")
                _med_spec = st.text_input("Spécialité",
                    value=_med.get("specialite", ""),
                    placeholder="ex: Médecin de famille")
            with m2:
                _med_adr  = st.text_input("Adresse",
                    value=_med.get("adresse", ""),
                    placeholder="ex: Rue de la Paix 1, 2300 La Chaux-de-Fonds")
            if st.form_submit_button("💾 Enregistrer le médecin", type="primary"):
                save_medecin_destinataire(S.cas_id, {
                    "nom": _med_nom,
                    "specialite": _med_spec,
                    "adresse": _med_adr,
                })
                st.success("✅ Médecin enregistré.")

# ── FORMULAIRE ────────────────────────────────────────────────────────────────
def render_formulaire():
    _sidebar_context(unsaved=S.get('_bilan_unsaved', False))
    import json as _j
    info = S.patient_info

    # ── Sidebar : choix du mode d'affichage ──────────────────────────────────
    with st.sidebar:
        st.markdown("**⚙️ Affichage du bilan**")
        _layout = st.radio(
            "Mode",
            options=["accordeon", "grille", "onglets"],
            format_func=lambda x: {"accordeon":"🪗 Accordéon","grille":"⊞ Grille","onglets":"📑 Onglets"}[x],
            index=["accordeon","grille","onglets"].index(
                st.session_state.get("bilan_layout_mode","accordeon")),
            key="bilan_layout_radio",
            label_visibility="collapsed"
        )
        st.session_state["bilan_layout_mode"] = _layout
        st.markdown("---")
    cas  = S.cas_info
    bid  = S.bilan_id
    try:  snap = _j.loads(cas.get("template_snapshot","{}") or "{}")
    except: snap = {}
    nom_t = snap.get("nom","Bilan")

    # Cache bilan_row en session pour éviter un appel GSheets à chaque rerun
    bilan_cache_key = f"bilan_row_{bid}"
    if bilan_cache_key not in S:
        from utils.db import get_bilan
        S[bilan_cache_key] = get_bilan(bid) or {}
    bilan_row = S[bilan_cache_key]
    date_b    = bilan_row.get("date_bilan","")

    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")} '
        f'— {nom_t} · {date_b}</div>',
        unsafe_allow_html=True)
    st.markdown("")

    col_save, col_print_b, _ = st.columns([1, 1.5, 4])
    with col_save:
        save_btn = st.button("💾 Sauvegarder", type="primary")
    with col_print_b:
        if st.button("🖨️ Imprimer fiches"):
            _ta_snap = (S.bilan_data.get("_tests_actifs_list")
                        or [cls.test_id() for cls in test_classes])
            _go("impression", bilan_id=bid, tests_actifs_snap=_ta_snap)

    # ── Confirmation retour sans sauvegarde ───────────────────────────────────
    if S.get("_confirm_back"):
        st.warning("⚠️ Modifications non sauvegardées — quitter quand même ?")
        ca, cb, _ = st.columns([1.5, 1.5, 5])
        with ca:
            if st.button("🚪 Quitter sans sauvegarder", type="primary"):
                S.pop("_confirm_back", None)
                S.pop("_bilan_unsaved", None)
                _back_to_cas()
        with cb:
            if st.button("✏️ Continuer l'édition"):
                S.pop("_confirm_back", None)
                st.rerun()
        return

    if S.get("_confirm_back_accueil"):
        st.warning("⚠️ Modifications non sauvegardées — quitter quand même ?")
        ca, cb, _ = st.columns([1.5, 1.5, 5])
        with ca:
            if st.button("🚪 Quitter sans sauvegarder", type="primary", key="cba_ok"):
                S.pop("_confirm_back_accueil", None)
                S.pop("_bilan_unsaved", None)
                _go("accueil")
        with cb:
            if st.button("✏️ Continuer l'édition", key="cba_no"):
                S.pop("_confirm_back_accueil", None)
                st.rerun()
        return

    st.markdown("---")

    _ensure_registry()
    # Cache test_classes par bilan — re-calculer si registre était vide
    tc_key = f"test_classes_{bid}"
    if tc_key not in S or not S[tc_key]:
        S[tc_key] = build_tests_from_snapshot(snap)
    test_classes = S[tc_key]
    # Template neutre (tests=[]) — OK, on continue sans warning
    _template_id_bilan = snap.get("template_id","")
    if not test_classes and _template_id_bilan != "neutre":
        from core.registry import all_tests
        reg = all_tests()
        if not reg:
            st.error("❌ Registre vide — les tests ne sont pas chargés.")
        else:
            st.warning(f"⚠️ Aucun test dans ce snapshot. Disponibles : {list(reg.keys())}")
        return

    # S'assurer que bilan_data est chargé UNE SEULE FOIS
    if not S.bilan_data and bid:
        S.bilan_data = get_bilan_donnees(bid)
    # Injecter la liste des tests actifs dans bilan_data pour engine.py
    if bid and "_tests_actifs_list" not in S.bilan_data:
        ta = get_bilan_tests_actifs(bid, snap)
        S.bilan_data["_tests_actifs_list"] = ta

    # ── Impression fiches (dynamique selon tests actifs) ─────────────────────
    collected = render_bilan_form(
        bilan_id=bid, bilan_data=S.bilan_data,
        test_classes=test_classes, key_prefix=f"frm_{bid}",
        patient_info=S.patient_info)

    # Sauvegarde déclenchée depuis le bouton principal OU depuis l'expander tests actifs
    _trigger_save = save_btn or st.session_state.pop(f"frm_{bid}_trigger_save", False)
    if _trigger_save:
        with st.spinner("Enregistrement…"):
            ok = save_bilan_donnees(bid, collected, S.therapeute)
        if ok:
            S.bilan_data = collected
            # Mettre à jour les tests actifs dans la feuille Bilans
            if "tests_actifs" in collected:
                import json as _j
                try:
                    ta_list = _j.loads(collected["tests_actifs"])
                    S.bilan_data["_tests_actifs_list"] = ta_list
                    save_bilan_tests_actifs(bid, ta_list)
                except Exception:
                    pass
            S.pop("_bilan_unsaved", None)
            # Invalider le cache PDF et la synthèse IA
            S[f"analyse_stale_{S.cas_id}"] = True
            # Supprimer tous les caches PDF de ce cas
            for k in list(S.keys()):
                if k.startswith(f"pdf_bytes_{S.cas_id}"):
                    del S[k]
            st.success("✅ Bilan sauvegardé !")
            st.balloons()
        else:
            st.error("❌ Erreur lors de la sauvegarde.")
    else:
        # Marquer comme non sauvegardé dès qu'on a des données chargées
        if S.bilan_data is not None:
            S["_bilan_unsaved"] = True

# ── ÉVOLUTION ─────────────────────────────────────────────────────────────────
def render_evolution():
    _sidebar_context()
    import json as _j
    info = S.patient_info
    cas  = S.cas_info
    cid  = S.cas_id
    try:  snap = _j.loads(cas.get("template_snapshot","{}") or "{}")
    except: snap = {}
    nom_t = snap.get("nom","Évolution")

    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")} '
        f'— Évolution {nom_t}</div>', unsafe_allow_html=True)
    st.markdown("")

    st.markdown("---")

    bilans_df = get_cas_bilans(cid)
    if bilans_df.empty:
        st.info("Aucun bilan dans ce cas."); return

    selected = S.get("selected_bilans",[])
    if selected:
        filt = bilans_df[bilans_df["bilan_id"].isin(selected)]
        if not filt.empty: bilans_df = filt
    n_tot = len(get_cas_bilans(cid)); n_sel = len(bilans_df)  # get_cas_bilans est caché
    if n_sel < n_tot:
        st.info(f"ℹ️ {n_sel}/{n_tot} bilans sélectionnés.")

    # Structure plate — tous les champs déjà dans get_cas_bilans
    be = bilans_df.copy()
    if "date_bilan" in be.columns:
        be["date_bilan"] = pd.to_datetime(be["date_bilan"], errors="coerce")
    be = be.sort_values("date_bilan").reset_index(drop=True)

    # PDF — généré sur clic uniquement (évite rerun en boucle)
    # Pré-charger la synthèse IA — invalider si les bilans ont changé
    _ai_key     = f"analyse_text_{cid}"
    _ai_sig_key = f"analyse_sig_{cid}"
    import json as _jj
    # Signature = liste triée des bilan_ids + tests_actifs de chacun
    _ai_sig_now = str(sorted([
        (r["bilan_id"], r.get("tests_actifs",""))
        for _, r in be.iterrows()
    ]))
    if S.get(_ai_sig_key) != _ai_sig_now:
        # Bilans ou tests ont changé → effacer TOUS les caches de la synthèse IA
        S.pop(_ai_key, None)
        S.pop(f"ta_{cid}", None)       # vider aussi le widget text_area
        S[_ai_sig_key] = _ai_sig_now
        S[f"analyse_stale_{cid}"] = True  # déclenche le warning "à régénérer" dans l'UI
    if _ai_key not in S:
        S[_ai_key] = load_analyse_cas(cid)

    _tid  = snap.get("template_id","") or cas.get("template_id","") or "shv"
    _tnom = snap.get("nom","Bilan")

    # ── Options du rapport PDF ────────────────────────────────────────────────
    # Options PDF : tests actifs du cas + graphiques
    _ensure_registry()
    _tc_key2 = f"test_classes_ev_{cid}"
    if _tc_key2 not in S or not S[_tc_key2]:
        S[_tc_key2] = build_tests_from_snapshot(snap)
    _active_tests = S[_tc_key2]
    # Labels des tests actifs → noms affichés dans les options
    _active_labels = [cls.tab_label() for cls in _active_tests if hasattr(cls, "tab_label")]

    # ── État PDF : inclusion + ordre ─────────────────────────────────────────
    _pdf_opts_key  = f"pdf_opts_{cid}"
    _pdf_order_key = f"pdf_order_{cid}"

    # Réinitialiser si la liste des tests a changé
    _known = set(S.get(_pdf_opts_key, {}).keys()) - {"Évolution graphique"}
    if _known != set(_active_labels):
        S[_pdf_opts_key]  = {lbl: True for lbl in _active_labels}
        S[_pdf_opts_key]["Évolution graphique"] = True
        S[_pdf_order_key] = list(_active_labels)

    # S'assurer que _pdf_order_key est initialisé et cohérent
    _current_order = S.get(_pdf_order_key, list(_active_labels))
    # Ajouter éventuels nouveaux tests à la fin, retirer les disparus
    _current_order = [l for l in _current_order if l in set(_active_labels)]
    _current_order += [l for l in _active_labels if l not in _current_order]
    S[_pdf_order_key] = _current_order

    # ── État : sélection ordonnée (confirmée) + draft (en cours d'édition) ───
    _pdf_selected_key = f"pdf_selected_{cid}"
    _pdf_draft_key    = f"pdf_draft_{cid}"
    _pdf_charts_key   = f"pdf_charts_{cid}"

    if _pdf_selected_key not in S:
        S[_pdf_selected_key] = []
    # Draft = copie de travail, initialisée depuis la sélection confirmée
    if _pdf_draft_key not in S:
        S[_pdf_draft_key] = list(S[_pdf_selected_key])

    # ── Tout calculé avant l'expander ───────────────────────────────────────
    _pdf_cache_key = f"pdf_cache_{cid}"
    _pdf_sig_key   = f"pdf_sig_{cid}"
    _label_to_tid  = {cls.tab_label(): cls.test_id()
                      for cls in _active_tests if hasattr(cls, "tab_label") and hasattr(cls, "test_id")}
    _selected_ordered = S.get(_pdf_selected_key, [])
    _selected_set     = set(_selected_ordered)
    _excluded         = {_label_to_tid[lbl] for lbl in _active_labels
                         if lbl not in _selected_set and lbl in _label_to_tid}
    _show_charts      = S.get(_pdf_charts_key, True)
    _ordered_tids     = [_label_to_tid[lbl] for lbl in _selected_ordered
                         if lbl in _label_to_tid]
    if not _selected_ordered:
        _excluded = set(); _ordered_tids = []
    _current_sig = str((
        sorted(be["bilan_id"].tolist()),
        tuple(sorted(_excluded)),
        tuple(_ordered_tids),
        _show_charts,
        (S.get(f"ta_{cid}") or S.get(f"analyse_text_{cid}", ""))[:50],
    ))
    if S.get(_pdf_sig_key) != _current_sig:
        S.pop(_pdf_cache_key, None)

    with st.expander("⚙️ Options du rapport PDF", expanded=False):
        _draft = S[_pdf_draft_key]
        _draft_set = set(_draft)
        _avail_draft = [lbl for lbl in _active_labels if lbl not in _draft_set]

        # ── Zone sélectionnée (draft) ──────────────────────────────────
        if _draft:
            st.caption("✅ **Dans le rapport** — cliquer ✕ pour retirer")
            for _si, _sname in enumerate(_draft):
                _col_num, _col_lbl, _col_rm = st.columns([0.4, 3.5, 0.8])
                _col_num.markdown(
                    f"<div style='padding-top:6px;color:#2B57A7;font-weight:700'>"
                    f"{_si+1}</div>", unsafe_allow_html=True)
                _col_lbl.markdown(
                    f"<div style='padding-top:6px'>{_sname}</div>",
                    unsafe_allow_html=True)
                if _col_rm.button("✕", key=f"pdf_rm_{cid}_{_si}",
                                   use_container_width=True):
                    S[_pdf_draft_key] = [x for x in _draft if x != _sname]
                    st.rerun()
        else:
            st.caption("*(aucun test sélectionné — cliquer ci-dessous pour ajouter)*")

        if _draft:
            st.markdown("---")

        # ── Zone disponible ────────────────────────────────────────────
        if _avail_draft:
            st.caption("➕ **Disponibles** — cliquer pour ajouter")
            _av_cols = st.columns(min(len(_avail_draft), 4))
            for _ai, _aname in enumerate(_avail_draft):
                if _av_cols[_ai % 4].button(
                        _aname, key=f"pdf_add_{cid}_{_ai}",
                        use_container_width=True):
                    S[_pdf_draft_key] = _draft + [_aname]
                    st.rerun()
        else:
            st.caption("*(tous les tests sont dans le rapport)*")

        st.markdown("---")
        _gc_val = S.get(_pdf_charts_key, True)
        _gc_new = st.checkbox("📈 Graphiques d'évolution", value=_gc_val,
                              key=f"pdfsec_{cid}_charts")

        # ── Bouton Sauvegarder ─────────────────────────────────────────
        _draft_changed = (S[_pdf_draft_key] != S[_pdf_selected_key]
                          or _gc_new != S.get(_pdf_charts_key, True))
        st.markdown("")
        _save_col, _reset_col = st.columns([2, 1])
        if _draft_changed:
            _apply_label = f"💾 Appliquer & générer PDF ({n_sel} bilan{'s' if n_sel>1 else ''})"
        elif S.get(_pdf_cache_key):
            _apply_label = None  # on affiche download_button
        else:
            _apply_label = f"📄 Générer PDF ({n_sel} bilan{'s' if n_sel>1 else ''})"

        if _apply_label:
            if _save_col.button(_apply_label, type="primary",
                                use_container_width=True, key=f"pdf_save_{cid}"):
                # 1. Sauvegarder la sélection si changée
                if _draft_changed:
                    S[_pdf_selected_key] = list(S[_pdf_draft_key])
                    S[_pdf_charts_key]   = _gc_new
                    S.pop(_pdf_cache_key, None)
                    S.pop(_pdf_sig_key, None)
                    # Recalculer exclusions/ordre avec la nouvelle sélection
                    _sel_new = S[_pdf_selected_key]
                    _excl_new = {_label_to_tid[lbl] for lbl in _active_labels
                                 if lbl not in set(_sel_new) and lbl in _label_to_tid}
                    _ord_new  = [_label_to_tid[lbl] for lbl in _sel_new if lbl in _label_to_tid]
                    if not _sel_new: _excl_new = set(); _ord_new = []
                else:
                    _excl_new = _excluded
                    _ord_new  = _ordered_tids
                # 2. Générer le PDF immédiatement
                with st.spinner("Génération du PDF…"):
                    try:
                        analyse_txt = (S.get(f"ta_{cid}")
                                       or S.get(f"analyse_text_{cid}")
                                       or load_analyse_cas(cid))
                        _medecin_info = get_medecin_destinataire(cid)
                        S[_pdf_cache_key] = generate_pdf(be, info,
                            analyse_text=analyse_txt,
                            template_id=_tid, template_nom=_tnom,
                            medecin_info=_medecin_info,
                            excluded_test_ids=_excl_new,
                            ordered_test_ids=_ord_new,
                            show_charts=S.get(_pdf_charts_key, True))
                        S[_pdf_sig_key] = _current_sig
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur PDF : {e}")
        else:
            # PDF en cache et rien à changer → download direct
            _save_col.download_button(
                label=f"📄 Télécharger PDF ({n_sel} bilan{'s' if n_sel>1 else ''})",
                data=S[_pdf_cache_key],
                file_name=f"evolution_{_tnom}_{info.get('nom','')}_{date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                key=f"dl_pdf_exp_{cid}",
            )
        if _reset_col.button("↺ Réinitialiser",
                              use_container_width=True,
                              key=f"pdf_reset_{cid}"):
            S[_pdf_draft_key] = []
            S[_pdf_selected_key] = []
            S.pop(f"pdf_cache_{cid}", None)
            S.pop(f"pdf_sig_{cid}", None)
            st.rerun()










    _ensure_registry()
    tc_key = f"test_classes_ev_{cid}"
    if tc_key not in S or not S[tc_key]:
        S[tc_key] = build_tests_from_snapshot(snap)
    test_classes = S[tc_key]
    render_evolution_view(
        bilans_df=be, patient_info=info,
        test_classes=test_classes,
        module_id=cas.get("template_id",""),
        patient_id=S.patient_id,
        cas_id=cid)



# ── ROUTEUR ───────────────────────────────────────────────────────────────────
mode = S.mode
# ── VUE IMPRESSION ────────────────────────────────────────────────────────────
def render_impression():
    _sidebar_context()
    from utils.pdf import generate_tests_pdf
    from core.registry import all_tests as _all_tests_imp
    info = S.patient_info
    bid  = S.get("bilan_id","")

    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")} '
        f'— Impression fiches</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🖨️ Fiches à imprimer")
    st.caption("Basé sur les tests actifs au moment de l'ouverture de cette page.")

    _tests_map_imp = _all_tests_imp()
    _ta = S.get("tests_actifs_snap") or []
    _q_avail = [tid for tid in _ta if tid in _tests_map_imp]

    if not _q_avail:
        st.info("Aucune fiche disponible pour les tests actifs de ce bilan.")
        return

    st.caption("Décochez les fiches à exclure du PDF.")
    _pc = st.columns(min(len(_q_avail), 5))
    _checks = {}
    for _i, _tid in enumerate(_q_avail):
        _cls = _tests_map_imp[_tid]
        _checks[_tid] = _pc[_i % 5].checkbox(
            _cls.tab_label(), value=True, key=f"imp_{_tid}")
    _sel = [k for k, v in _checks.items() if v]

    st.markdown("")
    if _sel:
        with st.spinner("Génération du PDF…"):
            try:
                _pdf = generate_tests_pdf(_sel, info)
                st.download_button(
                    "📥 Télécharger les fiches",
                    data=_pdf,
                    file_name=f"fiches_{info.get('nom','')}_{bid}.pdf",
                    mime="application/pdf",
                    type="primary",
                )
            except Exception as _e:
                st.error(f"Erreur : {_e}")
    else:
        st.info("Sélectionnez au moins une fiche.")

# ── VUE BIBLIOTHÈQUE DES TESTS ────────────────────────────────────────────────
def render_bibliotheque():
    from utils.search import search_items
    _ensure_registry()
    from core.registry import all_tests as _all_tests_reg
    tests_map = _all_tests_reg()  # {test_id: class}

    st.markdown('<div class="page-title">📚 Bibliothèque des tests</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    # Recherche
    s1, s2 = st.columns([3, 2])
    search_q  = s1.text_input("🔍 Rechercher", placeholder="ex: épaule, équilibre, Berg…",
                               key="bib_search")
    ai_q      = s2.text_input("🤖 Décrire", placeholder="ex: patient âgé qui chute…",
                               key="bib_ai")

    # Recherche IA
    if ai_q and S.get("bib_ai_prev") != ai_q:
        S["bib_ai_prev"] = ai_q
        with st.spinner("Recherche IA…"):
            try:
                import anthropic as _ant, json as _aj, re as _re
                _catalog = [{"id": tid,
                             "nom": cls.meta().get("nom",""),
                             "tags": cls.meta().get("tags",[]),
                             "desc": cls.meta().get("description","")}
                            for tid, cls in tests_map.items()]
                _msg = _ant.Anthropic().messages.create(
                    model="claude-haiku-4-5", max_tokens=600,
                    system=('Tu es un assistant physiothérapeute. '
                            'Reponds UNIQUEMENT avec un JSON {"ids":[...]} '
                            'contenant TOUS les IDs de tests pertinents.'),
                    messages=[{"role":"user","content":
                        "Catalogue: " + _aj.dumps(_catalog, ensure_ascii=False) +
                        "\nDescription: " + ai_q}])
                _m = _re.search(r'\{"ids":\s*\[[^\]]*\]\}', _msg.content[0].text, _re.DOTALL)
                S["bib_ai_results"] = _aj.loads(_m.group()).get("ids",[]) if _m else []
            except Exception:
                S["bib_ai_results"] = []

    ai_ids = S.get("bib_ai_results", [])

    # Filtrer la liste
    all_items = list(tests_map.items())  # [(tid, cls), ...]
    if search_q:
        def _key(item):
            m = item[1].meta()
            return f"{m.get('nom','')} {m.get('description','')} {item[0]}", m.get("tags",[])
        filtered = search_items(search_q, all_items, _key)
    elif ai_ids:
        filtered = [(tid, tests_map[tid]) for tid in ai_ids if tid in tests_map]
        if filtered:
            st.markdown("**✨ Suggestions IA :**")
    else:
        filtered = all_items

    if not filtered:
        st.info("Aucun test trouvé.")
        return

    # Affichage — test sélectionné
    sel_key = "bib_selected_test"
    selected_tid = S.get(sel_key)

    col_list, col_detail = st.columns([1, 2])

    with col_list:
        st.markdown(f"**{len(filtered)} test(s)**")
        for tid, cls in filtered:
            m = cls.meta()
            tags = m.get("tags", [])
            is_sel = (tid == selected_tid)
            tag_str = " ".join([f"`{t}`" for t in tags[:3]])
            btn_label = f"{'▶ ' if is_sel else ''}{cls.tab_label()}"
            if st.button(btn_label, key=f"bib_btn_{tid}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                S[sel_key] = tid
                st.rerun()
            if tags:
                st.caption(" · ".join(tags[:4]))

    with col_detail:
        if not selected_tid or selected_tid not in tests_map:
            st.info("👈 Sélectionne un test pour le consulter.")
        else:
            cls = tests_map[selected_tid]
            m = cls.meta()
            st.markdown(f"### {cls.tab_label()}")
            if m.get("description"):
                st.caption(m["description"])
            if m.get("tags"):
                st.markdown(" ".join([f"`{t}`" for t in m["tags"]]))
            st.markdown("---")

            # Affichage read-only — render() avec données vides + disabled inputs via CSS
            st.markdown("""<style>
                [data-testid="stForm"] button { display: none !important; }
                .bib-readonly input, .bib-readonly textarea, .bib-readonly select {
                    pointer-events: none; opacity: 0.7;
                }
            </style>""", unsafe_allow_html=True)

            def _lv_empty(k, default=""):
                return default

            st.markdown('<div class="bib-readonly">', unsafe_allow_html=True)
            try:
                with st.container():
                    cls().render(_lv_empty, f"bib_{selected_tid}")
            except Exception as _e:
                st.warning(f"Aperçu non disponible : {_e}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Impression PDF si disponible
            from utils.pdf import QUESTIONNAIRES, generate_questionnaires_pdf
            _TEST_TO_Q = {
                "had":"had","sf12":"sf12","hvt":"hvt","bolt":"bolt",
                "nijmegen":"nijmegen","mrc_dyspnee":"mrc","comorbidites":"comorb",
                "testing_mi":"muscle","leg_press":"leg_press",
                "odi":"odi","tampa":"tampa","orebro":"orebro",
                "mmrc":"mmrc_bpco","cat":"cat_bpco",
                "quick_dash":"quick_dash","ases":"ases",
            }
            _qk = _TEST_TO_Q.get(selected_tid)
            if _qk and _qk in QUESTIONNAIRES:
                st.markdown("---")
                if st.button("🖨️ Télécharger fiche PDF", type="primary",
                             key=f"bib_pdf_{selected_tid}"):
                    with st.spinner("Génération…"):
                        try:
                            _pdf = generate_questionnaires_pdf([_qk], {})
                            st.download_button("📥 Télécharger",
                                data=_pdf,
                                file_name=f"fiche_{selected_tid}.pdf",
                                mime="application/pdf",
                                key=f"bib_dl_{selected_tid}")
                        except Exception as _e:
                            st.error(f"Erreur : {_e}")


if   mode == "accueil":          render_accueil()
elif mode == "dossier":          render_dossier()
elif mode == "choisir_template": render_choisir_template()
elif mode == "cas":              render_cas()
elif mode == "formulaire":       render_formulaire()
elif mode == "evolution":        render_evolution()
elif mode == "impression":       render_impression()
elif mode == "bibliotheque":     render_bibliotheque()
else:
    S.mode = "accueil"; st.rerun()
