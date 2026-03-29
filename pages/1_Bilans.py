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
    info = S.patient_info
    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")} '
        f'— {info.get("date_naissance","—")} — ID : {info.get("patient_id","")}</div>',
        unsafe_allow_html=True)
    st.markdown("")

    col_back, col_new, col_edit, _ = st.columns([1,1,1,3])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            _go("accueil")
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
    info = S.patient_info
    st.markdown(
        f'<div class="patient-badge">👤 {info.get("nom","")} {info.get("prenom","")}'
        f' — Nouveau cas</div>', unsafe_allow_html=True)
    if st.button("⬅️ Retour"): _go("dossier")

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

    # Barre d'actions (copie v1)
    col_back, col_print, _ = st.columns([1,1.5,4])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            _go("accueil")

    # ── Questionnaires vierges ───────────────────────────────────────────────
    if S.get("show_print_modal"):
        with st.container():
            st.markdown("""
            <div style="background:#e8f0f8; border:2px solid #1a3c5e; border-radius:10px;
                        padding:1.2rem 1.5rem; margin-bottom:1rem;">
                <span style="font-size:1.1rem; font-weight:700; color:#1a3c5e;">
                🖨️ Sélectionner les questionnaires à imprimer
                </span>
            </div>""", unsafe_allow_html=True)

            # Questionnaires disponibles selon le template du cas
            _tmpl_id = "shv"
            _snap_q = {}
            try:
                _raw_snap = S.cas_info.get("template_snapshot","{}") or "{}"
                _snap_q = json.loads(_raw_snap)
                _tmpl_id = (_snap_q.get("template_id","") or
                            S.cas_info.get("template_id","") or "shv")
            except:
                _tmpl_id = S.cas_info.get("template_id","") or "shv"

            # Définir les questionnaires disponibles par template
            _Q_SHV       = ["had","sf12","hvt","bolt","nijmegen","mrc","comorb","muscle","leg_press"]
            _Q_EQUILIBRE = ["muscle","leg_press"]
            _Q_BPCO      = ["mmrc_bpco","cat_bpco","muscle","leg_press"]
            _Q_LOMBALGIE = ["odi","tampa","orebro","muscle","leg_press"]
            _Q_EPAULE    = ["quick_dash","ases","muscle","leg_press"]
            _Q_NEUTRE    = ["muscle","leg_press"]
            _Q_MAP = {
                "shv":               _Q_SHV,
                "equilibre":         _Q_EQUILIBRE,
                "bpco":              _Q_BPCO,
                "lombalgie":         _Q_LOMBALGIE,
                "epaule_douloureuse":_Q_EPAULE,
                "neutre":            _Q_NEUTRE,
            }
            # Fallback vide si template non mappé (pas de liste SHV par erreur)
            _avail = _Q_MAP.get(_tmpl_id, [])

            _Q_LABELS = {
                "had":"😟 HAD","sf12":"📊 SF-12","hvt":"🌬️ Test HV","bolt":"⏱️ BOLT",
                "nijmegen":"📋 Nijmegen","mrc":"🚶 MRC","comorb":"🏥 Comorb.",
                "muscle":"💪 Testing","leg_press":"🦵 Leg Press",
                "odi":"📋 ODI","tampa":"😰 Tampa","orebro":"🔮 Örebro",
                "cat_bpco":"💨 CAT","mmrc_bpco":"😮‍💨 mMRC","eva_lomb":"📊 EVA",
            }
            pc = st.columns(min(len(_avail), 5))
            checks = {
                k: pc[i%5].checkbox(_Q_LABELS.get(k,k), value=True, key=f"pc_{k}")
                for i,k in enumerate(_avail)
            }
            selected_q = [k for k,v in checks.items() if v]
            ga, gb, _ = st.columns([1.5,1,4])
            with ga:
                if selected_q:
                    with st.spinner("Génération…"):
                        try:
                            q_pdf = generate_questionnaires_pdf(selected_q, S.patient_info)
                            st.download_button(
                                label="📥 Télécharger PDF vierge",
                                data=q_pdf,
                                file_name=f"questionnaires_{S.patient_info.get('nom','')}_{date.today()}.pdf",
                                mime="application/pdf",
                                type="primary",
                                key="dl_q",
                            )
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                else:
                    st.warning("Sélectionnez au moins un questionnaire.")
            with gb:
                if st.button("✖ Fermer", key="close_print"):
                    S["show_print_modal"] = False; st.rerun()
        st.markdown("---")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # ── Gauche : bilans existants ─────────────────────────────────────────────
    with col_left:
        h1, h2 = st.columns([2, 1])
        with h1:
            st.markdown("#### 📋 Bilans existants")
        with h2:
            if st.button("📈 Évolution", type="primary", use_container_width=True):
                sel_key = f"sel_bilans_{S.cas_id}"
                _go("evolution", cas_id=S.cas_id, cas_info=cas,
                    selected_bilans=S.get(sel_key,[]))
        bilans_df = get_cas_bilans_meta(S.cas_id)
        if bilans_df.empty:
            st.info("Aucun bilan pour ce cas.")
        else:
            sel_key     = f"sel_bilans_{S.cas_id}"
            if sel_key not in S:
                S[sel_key] = list(bilans_df["bilan_id"])
            # Nettoyer les IDs obsolètes
            valid_ids   = list(bilans_df["bilan_id"])
            S[sel_key]  = [i for i in S[sel_key] if i in valid_ids]

            st.markdown(
                "<small style='color:#888'>Cochez les bilans à inclure dans l'évolution et le PDF</small>",
                unsafe_allow_html=True)

            new_sel = []
            for _, bilan in bilans_df.iterrows():
                bid  = bilan["bilan_id"]
                d    = bilan["date_bilan"]
                dstr = d.strftime("%d/%m/%Y") if pd.notna(d) else "—"

                c_chk, c_info, c_open, c_del = st.columns([0.5,3.5,0.8,0.8])
                with c_chk:
                    checked = st.checkbox("", value=bid in S[sel_key],
                                          key=f"sel_{bid}", label_visibility="collapsed")
                    if checked: new_sel.append(bid)
                with c_info:
                    st.markdown(
                        f"**{dstr}**  \n"
                        f"<small>{bilan.get('praticien','')}</small>",
                        unsafe_allow_html=True)
                with c_open:
                    if st.button("✏️", key=f"op_{bid}", help="Ouvrir ce bilan"):
                        S.pop("_bilan_unsaved", None)
                        # Vider le cache de la ligne bilan pour forcer rechargement
                        S.pop(f"bilan_row_{bid}", None)
                        _go("formulaire", bilan_id=bid,
                            bilan_data=get_bilan_donnees(bid))
                with c_del:
                    if st.button("🗑️", key=f"dl_{bid}", help="Supprimer"):
                        S[f"confirm_del_{bid}"] = True

                if S.get(f"confirm_del_{bid}"):
                    st.warning(
                        f"⚠️ Supprimer définitivement le bilan du **{dstr}** ? "
                        "Cette action est irréversible.")
                    ca, cb, _ = st.columns([1,1,3])
                    with ca:
                        if st.button("✅ Confirmer", key=f"dok_{bid}", type="primary"):
                            with st.spinner("Suppression…"):
                                delete_bilan(bid, S.therapeute)
                            S.pop(f"confirm_del_{bid}", None)
                            S[sel_key] = [i for i in S[sel_key] if i!=bid]
                            st.rerun()
                    with cb:
                        if st.button("✖ Annuler", key=f"dno_{bid}"):
                            S.pop(f"confirm_del_{bid}", None); st.rerun()

            S[sel_key] = new_sel
            n_sel = len(new_sel); n_tot = len(bilans_df)
            if n_sel < n_tot:
                st.markdown(
                    f"<small style='color:#f57c00'>⚡ {n_sel}/{n_tot} bilans "
                    f"sélectionnés pour l'évolution</small>",
                    unsafe_allow_html=True)

    # ── Droite : créer bilan ──────────────────────────────────────────────────
    with col_right:
        st.markdown(f"#### ➕ Nouveau bilan {snap.get('nom','')}")
        with st.form("f_new_bilan"):
            bilan_date = st.date_input("Date du bilan", value=date.today())
            praticien  = st.text_input("Praticien", value=S.therapeute or "")
            ok = st.form_submit_button("➕ Créer", type="primary")

    with col_print:
        if st.button("🖨️ Questionnaires vierges"):
            S["show_print_modal"] = not S.get("show_print_modal", False)
            st.rerun()

    if ok:
        with st.spinner("Création du bilan…"):
            bid = create_bilan(S.cas_id, praticien,
                               bilan_date, S.cabinet_id)
        S.pop("_bilan_unsaved", None)
        _go("formulaire", bilan_id=bid, bilan_data={})

# ── FORMULAIRE ────────────────────────────────────────────────────────────────
def render_formulaire():
    import json as _j
    info = S.patient_info
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

    col_back, col_save, col_cas, _ = st.columns([1,1,1.5,4])
    with col_back:
        if st.button("⬅️ Retour"):
            if S.get("_bilan_unsaved"):
                S["_confirm_back"] = True
                st.rerun()
            else:
                _back_to_cas()
    with col_save:
        save_btn = st.button("💾 Sauvegarder", type="primary")
    with col_cas:
        if st.button("⬅️ Changer de patient"):
            if S.get("_bilan_unsaved"):
                S["_confirm_back_accueil"] = True
                st.rerun()
            else:
                _go("accueil")

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

    collected = render_bilan_form(
        bilan_id=bid, bilan_data=S.bilan_data,
        test_classes=test_classes, key_prefix=f"frm_{bid}",
        patient_info=S.patient_info)

    if save_btn:
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

    col_back, col_chg, col_pdf, _ = st.columns([1,1.5,2,3])
    with col_back:
        if st.button("⬅️ Retour"): _back_to_cas()
    with col_chg:
        if st.button("⬅️ Changer de patient"): _go("accueil")

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
    # Pré-charger la synthèse IA en session AVANT la génération PDF
    _ai_key = f"analyse_text_{cid}"
    if _ai_key not in S:
        S[_ai_key] = load_analyse_cas(cid)

    with col_pdf:
        _tid  = snap.get("template_id","") or cas.get("template_id","") or "shv"
        _tnom = snap.get("nom","Bilan")
        try:
            # Priorité : widget text_area (valeur courante) > session > GSheets
            analyse_txt = S.get(f"analyse_text_{cid}") or load_analyse_cas(cid)
            pdf_data = generate_pdf(be, info,
                analyse_text=analyse_txt,
                template_id=_tid, template_nom=_tnom)
        except Exception as e:
            pdf_data = None
            st.error(f"Erreur PDF : {e}")
        if pdf_data:
            st.download_button(
                label=f"📄 Exporter PDF ({n_sel} bilan{'s' if n_sel>1 else ''})",
                data=pdf_data,
                file_name=f"evolution_{_tnom}_{info.get('nom','')}_{date.today()}.pdf",
                mime="application/pdf",
                type="primary",
            )

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
if   mode == "accueil":          render_accueil()
elif mode == "dossier":          render_dossier()
elif mode == "choisir_template": render_choisir_template()
elif mode == "cas":              render_cas()
elif mode == "formulaire":       render_formulaire()
elif mode == "evolution":        render_evolution()
else:
    S.mode = "accueil"; st.rerun()
