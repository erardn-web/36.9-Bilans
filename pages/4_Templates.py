"""pages/4_Templates.py — Gestion des templates cabinet"""
import streamlit as st
import json, re
from datetime import datetime

st.set_page_config(page_title="Templates — 36.9 Bilans", page_icon="📋", layout="wide")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Charger tous les tests ────────────────────────────────────────────────────
@st.cache_resource
def _load_all_tests():
    import importlib
    modules = [
        # Templates (chargent leurs tests)
        "templates.shv","templates.equilibre","templates.bpco","templates.lombalgie",
        "templates.neutre","templates.epaule_douloureuse","templates.cervicalgie",
        "templates.genou","templates.hanche","templates.membre_superieur",
        # Tests individuels batch 1
        "tests.questionnaires.psfs","tests.questionnaires.groc","tests.questionnaires.eq5d",
        "tests.questionnaires.ndi","tests.questionnaires.koos","tests.questionnaires.hoos",
        "tests.questionnaires.lysholm","tests.questionnaires.dash","tests.questionnaires.lefs",
        "tests.questionnaires.womac","tests.questionnaires.spadi","tests.questionnaires.constant_murley",
        "tests.questionnaires.prtee","tests.questionnaires.bctq","tests.questionnaires.roland_morris",
        "tests.questionnaires.start_back","tests.questionnaires.fabq","tests.questionnaires.dn4",
        "tests.questionnaires.faos","tests.questionnaires.kujala","tests.questionnaires.acl_rsi",
        "tests.questionnaires.hagos","tests.questionnaires.ikdc","tests.questionnaires.csi",
        "tests.questionnaires.qbpds","tests.questionnaires.atrs","tests.questionnaires.wosi",
        "tests.questionnaires.visa_a","tests.questionnaires.visa_p",
        "tests.questionnaires.visa_h","tests.questionnaires.visa_g",
        "tests.questionnaires.cait","tests.questionnaires.tegner",
        "tests.questionnaires.dhi","tests.questionnaires.hit6",
        "tests.tests_cliniques.nrs",
        # Batch 2
        "tests.questionnaires.borg_rpe","tests.questionnaires.sgrq","tests.questionnaires.lcadl",
        "tests.questionnaires.pcfs","tests.questionnaires.psqi","tests.questionnaires.abc_scale",
        "tests.questionnaires.mini_bestest","tests.questionnaires.fes_i",
        "tests.questionnaires.barthel","tests.questionnaires.ten_mwt","tests.questionnaires.ashworth",
        "tests.questionnaires.iciq_ui","tests.questionnaires.pfdi20",
        "tests.questionnaires.pcs","tests.questionnaires.phq9","tests.questionnaires.gad7",
        "tests.questionnaires.isi","tests.questionnaires.haq","tests.questionnaires.basdai",
        "tests.questionnaires.frailty_scale","tests.questionnaires.frail_scale",
        "tests.questionnaires.gait_speed","tests.questionnaires.k_ses",
        "tests.questionnaires.prwe","tests.questionnaires.bpi",
    ]
    for m in modules:
        try: importlib.import_module(m)
        except Exception as e: pass
    return True

_load_all_tests()

from core.registry import all_tests
from utils.db import get_all_cabinet_templates, save_cabinet_template, set_cabinet_template_actif

S = st.session_state

# ── Helpers ───────────────────────────────────────────────────────────────────
def _make_id(nom: str) -> str:
    """Génère un template_id unique à partir du nom."""
    base = re.sub(r'[^a-z0-9]', '_', nom.lower().strip())
    base = re.sub(r'_+', '_', base).strip('_')
    return f"cab_{base}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

ICONES = ["🏥","🦴","💪","🦵","🦶","🤚","🧠","❤️","🫁","🧘","🏃","⚽","🎾","🏊",
          "👴","🤰","🦽","🔬","📋","⚡","💧","🌀","😟","😴"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""<style>
.tmpl-card {
    border: 1px solid var(--color-border-tertiary);
    border-radius: 10px; padding: 14px 18px;
    background: var(--color-background-primary);
    margin-bottom: 10px;
}
.tmpl-card:hover { border-color: var(--color-border-secondary); }
.tmpl-inactive { opacity: 0.5; }
.tmpl-badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
}
.tmpl-active   { background: #e8f5e9; color: #388e3c; }
.tmpl-disabled { background: #f5f5f5; color: #999; }
</style>""", unsafe_allow_html=True)

# ── Titre ─────────────────────────────────────────────────────────────────────
st.markdown("## 📋 Templates du cabinet")
st.caption("Créez des templates personnalisés avec les tests de votre choix. Ils apparaîtront dans la liste lors de la création d'un nouveau cas.")
st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**📋 Templates**")
    _templates_all = get_all_cabinet_templates()
    _n_actif = sum(1 for t in _templates_all if t.get("actif","Oui") == "Oui")
    st.metric("Templates actifs", _n_actif)
    st.metric("Total", len(_templates_all))
    st.markdown("---")
    _show_inactive = st.checkbox("Afficher les inactifs", value=False)

# ── État : mode (liste / créer / éditer) ─────────────────────────────────────
if "tmpl_mode" not in S:
    S["tmpl_mode"] = "liste"
if "tmpl_edit_id" not in S:
    S["tmpl_edit_id"] = None

# ── Vue LISTE ─────────────────────────────────────────────────────────────────
if S["tmpl_mode"] == "liste":

    if st.button("➕ Créer un template", type="primary"):
        S["tmpl_mode"] = "creer"
        S["tmpl_edit_id"] = None
        st.rerun()

    templates = get_all_cabinet_templates()
    if _show_inactive:
        shown = templates
    else:
        shown = [t for t in templates if t.get("actif","Oui") == "Oui"]

    if not shown:
        st.info("Aucun template cabinet pour l'instant. Créez votre premier template !")
    else:
        st.markdown(f"**{len(shown)} template(s)**")
        for tmpl in shown:
            tid   = tmpl.get("template_id","")
            nom   = tmpl.get("nom","—")
            icone = tmpl.get("icone","📋")
            desc  = tmpl.get("description","")
            actif = tmpl.get("actif","Oui") == "Oui"
            try:
                test_ids = json.loads(tmpl.get("tests_json","[]") or "[]")
            except Exception:
                test_ids = []
            created = tmpl.get("created_at","")[:10]
            badge_cls = "tmpl-active" if actif else "tmpl-disabled"
            badge_txt = "Actif" if actif else "Inactif"
            card_cls  = "tmpl-card" if actif else "tmpl-card tmpl-inactive"

            with st.container():
                st.markdown(f'<div class="{card_cls}">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([6, 1.5, 1.5])
                with c1:
                    st.markdown(f"### {icone} {nom}")
                    if desc:
                        st.caption(desc)
                    st.markdown(
                        f'<span class="tmpl-badge {badge_cls}">{badge_txt}</span> '
                        f'<span style="font-size:12px;color:#aaa"> · {len(test_ids)} tests · créé le {created}</span>',
                        unsafe_allow_html=True)
                    # Aperçu des tests
                    tests_map = all_tests()
                    test_labels = []
                    for t in test_ids:
                        cls = tests_map.get(t)
                        test_labels.append(cls.tab_label() if cls else f"⚠️ {t}")
                    if test_labels:
                        st.caption(" · ".join(test_labels))
                with c2:
                    if st.button("✏️ Modifier", key=f"edit_{tid}", use_container_width=True):
                        S["tmpl_mode"] = "editer"
                        S["tmpl_edit_id"] = tid
                        st.rerun()
                with c3:
                    if actif:
                        if st.button("⏸ Désactiver", key=f"deact_{tid}", use_container_width=True):
                            set_cabinet_template_actif(tid, False)
                            st.rerun()
                    else:
                        if st.button("▶ Activer", key=f"act_{tid}", use_container_width=True):
                            set_cabinet_template_actif(tid, True)
                            st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")


# ── Vue CRÉER / ÉDITER ────────────────────────────────────────────────────────
elif S["tmpl_mode"] in ("creer", "editer"):

    is_edit = S["tmpl_mode"] == "editer"
    edit_id = S.get("tmpl_edit_id")

    # Charger les données existantes si édition
    existing = {}
    if is_edit and edit_id:
        for t in get_all_cabinet_templates():
            if t.get("template_id") == edit_id:
                existing = t
                break

    st.markdown(f"### {'✏️ Modifier' if is_edit else '➕ Créer'} un template")
    if st.button("⬅️ Retour"):
        S["tmpl_mode"] = "liste"
        st.rerun()
    st.markdown("---")

    # ── Formulaire ────────────────────────────────────────────────────────────
    c1, c2 = st.columns([4, 1])
    nom = c1.text_input("Nom du template *",
        value=existing.get("nom",""),
        placeholder="ex: Bilan épaule sportif, Lombalgie post-op...",
        key="tmpl_nom")

    icone_stored = existing.get("icone","🏥")
    icone_idx = ICONES.index(icone_stored) if icone_stored in ICONES else 0
    icone = c2.selectbox("Icône", ICONES, index=icone_idx, key="tmpl_icone")

    desc = st.text_input("Description",
        value=existing.get("description",""),
        placeholder="ex: Pour les patients en rééducation post-chirurgie épaule",
        key="tmpl_desc")

    st.markdown("---")
    st.markdown("#### 🧪 Sélection des tests")
    st.caption("Choisissez les tests dans l'ordre souhaité. Vous pouvez réordonner après sélection.")

    tests_map = all_tests()

    # Grouper par catégorie
    by_cat = {}
    for tid, cls in sorted(tests_map.items(), key=lambda x: x[1].tab_label()):
        cat = cls.meta().get("categorie", "autre")
        by_cat.setdefault(cat, []).append((tid, cls))

    CAT_LABELS = {
        "test_clinique":  "🔬 Tests cliniques",
        "questionnaire":  "📋 Questionnaires",
        "autre":          "📁 Autres",
    }

    # Sélection actuelle
    try:
        stored_ids = json.loads(existing.get("tests_json","[]") or "[]")
    except Exception:
        stored_ids = []

    selected_ids = list(S.get("tmpl_selected", stored_ids))
    if "tmpl_selected" not in S:
        S["tmpl_selected"] = stored_ids

    selected_set = set(selected_ids)

    # Afficher tests sélectionnés avec réordonnancement
    if selected_ids:
        st.markdown("**Tests sélectionnés (ordre du bilan) :**")
        for i, tid in enumerate(selected_ids):
            cls = tests_map.get(tid)
            label = cls.tab_label() if cls else f"⚠️ {tid}"
            col_n, col_l, col_up, col_dn, col_rm = st.columns([0.4, 4, 0.5, 0.5, 0.5])
            col_n.markdown(f"<div style='padding-top:6px;color:#2B57A7;font-weight:700'>{i+1}</div>",
                           unsafe_allow_html=True)
            col_l.markdown(f"<div style='padding-top:6px'>{label}</div>", unsafe_allow_html=True)
            if i > 0:
                if col_up.button("▲", key=f"up_{tid}_{i}", use_container_width=True):
                    selected_ids[i-1], selected_ids[i] = selected_ids[i], selected_ids[i-1]
                    S["tmpl_selected"] = selected_ids
                    st.rerun()
            if i < len(selected_ids)-1:
                if col_dn.button("▼", key=f"dn_{tid}_{i}", use_container_width=True):
                    selected_ids[i], selected_ids[i+1] = selected_ids[i+1], selected_ids[i]
                    S["tmpl_selected"] = selected_ids
                    st.rerun()
            if col_rm.button("✕", key=f"rm_{tid}_{i}", use_container_width=True):
                selected_ids.remove(tid)
                S["tmpl_selected"] = selected_ids
                st.rerun()
        st.markdown("---")

    # Ajouter des tests depuis les catégories
    st.markdown("**Ajouter des tests :**")
    for cat, items in sorted(by_cat.items()):
        available = [(tid, cls) for tid, cls in items if tid not in selected_set]
        if not available:
            continue
        with st.expander(f"{CAT_LABELS.get(cat, cat)} — {len(available)} disponibles"):
            cols = st.columns(3)
            for j, (tid, cls) in enumerate(available):
                m = cls.meta()
                tags = " · ".join(m.get("tags", [])[:3])
                if cols[j % 3].button(
                        f"{cls.tab_label()}",
                        key=f"add_{tid}",
                        use_container_width=True,
                        help=tags):
                    selected_ids.append(tid)
                    S["tmpl_selected"] = selected_ids
                    st.rerun()

    st.markdown("---")

    # ── Boutons sauvegarde ────────────────────────────────────────────────────
    col_save, col_cancel, _ = st.columns([2, 1.5, 4])

    can_save = bool(nom.strip()) and len(selected_ids) > 0

    if col_save.button("💾 Enregistrer le template", type="primary",
                       use_container_width=True, disabled=not can_save):
        if not can_save:
            st.error("Nom et au moins un test requis.")
        else:
            tid_save = edit_id if is_edit else _make_id(nom)
            ok = save_cabinet_template(
                template_id=tid_save,
                nom=nom.strip(),
                icone=icone,
                description=desc.strip(),
                tests_json=json.dumps(selected_ids),
                actif=True,
            )
            if ok:
                st.success(f"✅ Template « {nom} » enregistré !")
                # Réinitialiser
                S.pop("tmpl_selected", None)
                S["tmpl_mode"] = "liste"
                # Forcer rechargement des templates dans 1_Bilans
                S.pop("_cabinet_templates_loaded", None)
                st.rerun()
            else:
                st.error("❌ Erreur lors de la sauvegarde.")

    if col_cancel.button("Annuler", use_container_width=True):
        S.pop("tmpl_selected", None)
        S["tmpl_mode"] = "liste"
        st.rerun()

    if not can_save and nom.strip():
        st.caption("⚠️ Sélectionnez au moins un test.")
    elif not can_save:
        st.caption("⚠️ Renseignez un nom et sélectionnez au moins un test.")
