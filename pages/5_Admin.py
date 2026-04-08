"""pages/5_Admin.py — Administration 36.9 Bilans
Deux niveaux d'accès :
  - Admin Cabinet  : gestion thérapeutes + templates
  - Super Admin    : validation tests + PDFs fixes + audit log
"""
import streamlit as st
import json, os, re
from datetime import datetime

st.set_page_config(page_title="Admin — 36.9 Bilans", page_icon="🔐", layout="wide")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Authentification ──────────────────────────────────────────────────────────
PWD_CABINET   = str(st.secrets.get("admin_cabinet_password", "cabinet369"))
PWD_SUPER     = str(st.secrets.get("admin_super_password",  "super369"))

def _check_auth():
    S = st.session_state
    if S.get("admin_level") in ("cabinet","super"):
        return S["admin_level"]
    return None

def _login_form():
    st.markdown("## 🔐 Administration 36.9 Bilans")
    st.markdown("Entrez votre mot de passe pour accéder à l'espace d'administration.")
    pwd = st.text_input("Mot de passe", type="password", key="admin_pwd_input")
    if st.button("Connexion", type="primary"):
        if pwd == PWD_SUPER:
            st.session_state["admin_level"] = "super"
            st.rerun()
        elif pwd == PWD_CABINET:
            st.session_state["admin_level"] = "cabinet"
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect.")
    st.stop()

level = _check_auth()
if not level:
    _login_form()

# ── Header ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([5, 1])
with col_h1:
    badge = "🔴 Super Admin" if level == "super" else "🟡 Admin Cabinet"
    st.markdown(f"## 🔐 Administration &nbsp; <span style='font-size:0.8rem;padding:3px 10px;background:{'#fce4ec' if level=='super' else '#fff8e1'};border-radius:10px;color:{'#c62828' if level=='super' else '#f57f17'}'>{badge}</span>", unsafe_allow_html=True)
with col_h2:
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.pop("admin_level", None)
        st.rerun()

st.markdown("---")

# ── Onglets selon niveau ──────────────────────────────────────────────────────
if level == "super":
    tabs = st.tabs(["📋 Templates", "👥 Thérapeutes", "🧪 Validation tests", "📄 PDFs fixes", "💬 Feedback", "📋 Audit Log", "📊 Statistiques"])
    tab_tmpl, tab_thera, tab_valid, tab_pdf, tab_fb, tab_audit, tab_stats = tabs
else:
    tabs = st.tabs(["📋 Templates", "👥 Thérapeutes", "📊 Statistiques"])
    tab_tmpl, tab_thera, tab_stats = tabs
    tab_valid = tab_pdf = tab_fb = tab_audit = None


# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET TEMPLATES CABINET
# ═══════════════════════════════════════════════════════════════════════════════
with tab_tmpl:
    @st.cache_resource
    def _load_all_tests_admin():
        import importlib, pathlib
        root = pathlib.Path(__file__).parent.parent
        # Templates
        for tmpl in ["templates.shv","templates.equilibre","templates.bpco","templates.lombalgie",
                     "templates.neutre","templates.epaule_douloureuse","templates.cervicalgie",
                     "templates.genou","templates.hanche","templates.membre_superieur"]:
            try: importlib.import_module(tmpl)
            except: pass
        # Auto-découverte récursive de tous les tests
        tests_dir = root / "tests"
        if tests_dir.exists():
            for py_file in sorted(tests_dir.rglob("*.py")):
                if py_file.name.startswith("_"): continue
                rel = py_file.relative_to(root).with_suffix("")
                module_name = str(rel).replace("/", ".").replace("\\", ".")
                try: importlib.import_module(module_name)
                except: pass
        return True

    _load_all_tests_admin()
    from core.registry import all_tests as _all_tests
    from utils.db import get_all_cabinet_templates, save_cabinet_template, set_cabinet_template_actif

    def _make_tmpl_id(nom):
        base = re.sub(r'[^a-z0-9]', '_', nom.lower().strip())
        base = re.sub(r'_+', '_', base).strip('_')
        return f"cab_{base}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    ICONES = ["🏥","🦴","💪","🦵","🦶","🤚","🧠","❤️","🫁","🧘","🏃","⚽","🎾","🏊",
              "👴","🤰","🦽","🔬","📋","⚡","💧","🌀","😟","😴"]

    S = st.session_state
    if "tmpl_mode" not in S: S["tmpl_mode"] = "liste"
    if "tmpl_edit_id" not in S: S["tmpl_edit_id"] = None

    # ── Vue liste ──────────────────────────────────────────────────────────────
    if S["tmpl_mode"] == "liste":
        c1h, c2h = st.columns([4,1])
        c1h.markdown("### 📋 Templates du cabinet")
        if c2h.button("➕ Créer", type="primary", use_container_width=True):
            S["tmpl_mode"] = "creer"; S["tmpl_edit_id"] = None
            S.pop("tmpl_selected", None); st.rerun()

        templates = get_all_cabinet_templates()
        show_inact = st.checkbox("Afficher les inactifs", value=False, key="tmpl_show_inact")
        shown = templates if show_inact else [t for t in templates if t.get("actif","Oui")=="Oui"]

        if not shown:
            st.info("Aucun template cabinet. Créez votre premier !")
        else:
            tests_map = _all_tests()
            for tmpl in shown:
                tid   = tmpl.get("template_id","")
                nom   = tmpl.get("nom","—")
                icone = tmpl.get("icone","📋")
                desc  = tmpl.get("description","")
                actif = tmpl.get("actif","Oui") == "Oui"
                try:    test_ids = json.loads(tmpl.get("tests_json","[]") or "[]")
                except: test_ids = []
                created = tmpl.get("created_at","")[:10]

                with st.container():
                    ca, cb, cc = st.columns([6,1.5,1.5])
                    with ca:
                        badge_col = "#e8f5e9" if actif else "#f5f5f5"
                        badge_txt = "Actif" if actif else "Inactif"
                        st.markdown(f"### {icone} {nom}")
                        if desc: st.caption(desc)
                        labels = [tests_map[t].tab_label() if t in tests_map else f"⚠️{t}" for t in test_ids]
                        st.caption(f"**{len(test_ids)} tests** : " + " · ".join(labels[:8]) + ("…" if len(labels)>8 else ""))
                        st.markdown(f'<span style="background:{badge_col};padding:2px 8px;border-radius:10px;font-size:11px">{badge_txt}</span> <span style="color:#aaa;font-size:11px">· créé le {created}</span>', unsafe_allow_html=True)
                    with cb:
                        if st.button("✏️ Modifier", key=f"te_{tid}", use_container_width=True):
                            S["tmpl_mode"] = "editer"; S["tmpl_edit_id"] = tid
                            S.pop("tmpl_selected", None); st.rerun()
                    with cc:
                        if actif:
                            if st.button("⏸ Désactiver", key=f"td_{tid}", use_container_width=True):
                                set_cabinet_template_actif(tid, False); st.rerun()
                        else:
                            if st.button("▶ Activer", key=f"ta_{tid}", use_container_width=True):
                                set_cabinet_template_actif(tid, True); st.rerun()
                    st.markdown("---")

    # ── Vue créer/éditer ───────────────────────────────────────────────────────
    elif S["tmpl_mode"] in ("creer","editer"):
        is_edit = S["tmpl_mode"] == "editer"
        edit_id = S.get("tmpl_edit_id")
        existing = {}
        if is_edit and edit_id:
            for t in get_all_cabinet_templates():
                if t.get("template_id") == edit_id: existing = t; break

        st.markdown(f"### {'✏️ Modifier' if is_edit else '➕ Créer'} un template")
        if st.button("⬅️ Retour"): S["tmpl_mode"]="liste"; st.rerun()
        st.markdown("---")

        cn, ci = st.columns([4,1])
        nom   = cn.text_input("Nom *", value=existing.get("nom",""), key="tn")
        icone_stored = existing.get("icone","🏥")
        icone = ci.selectbox("Icône", ICONES, index=ICONES.index(icone_stored) if icone_stored in ICONES else 0, key="ti")
        desc  = st.text_input("Description", value=existing.get("description",""), key="td")

        st.markdown("---")
        st.markdown("#### 🧪 Tests sélectionnés")

        tests_map = _all_tests()
        try:    stored_ids = json.loads(existing.get("tests_json","[]") or "[]")
        except: stored_ids = []
        if "tmpl_selected" not in S: S["tmpl_selected"] = stored_ids
        selected_ids = list(S["tmpl_selected"])
        selected_set = set(selected_ids)

        if selected_ids:
            for i, tid in enumerate(selected_ids):
                cls = tests_map.get(tid)
                label = cls.tab_label() if cls else f"⚠️ {tid}"
                sn, sl, su, sd, sr = st.columns([0.4,4,0.5,0.5,0.5])
                sn.markdown(f"<div style='padding-top:6px;color:#2B57A7;font-weight:700'>{i+1}</div>", unsafe_allow_html=True)
                sl.markdown(f"<div style='padding-top:6px'>{label}</div>", unsafe_allow_html=True)
                if i>0 and su.button("▲", key=f"up_{tid}_{i}", use_container_width=True):
                    selected_ids[i-1],selected_ids[i]=selected_ids[i],selected_ids[i-1]
                    S["tmpl_selected"]=selected_ids; st.rerun()
                if i<len(selected_ids)-1 and sd.button("▼", key=f"dn_{tid}_{i}", use_container_width=True):
                    selected_ids[i],selected_ids[i+1]=selected_ids[i+1],selected_ids[i]
                    S["tmpl_selected"]=selected_ids; st.rerun()
                if sr.button("✕", key=f"rm_{tid}_{i}", use_container_width=True):
                    selected_ids.remove(tid); S["tmpl_selected"]=selected_ids; st.rerun()
            st.markdown("---")

        st.markdown("**Ajouter des tests :**")

        # ── Recherche ────────────────────────────────────────────────────────
        rs1, rs2 = st.columns([3, 3])
        tmpl_search_q  = rs1.text_input("🔍 Recherche rapide",
            placeholder="ex: épaule, genou, KOOS…",
            key="tmpl_search_q")
        tmpl_search_ai = rs2.text_input("🤖 Décrire le patient",
            placeholder="ex: patient post-op LCA sportif…",
            key="tmpl_search_ai",
            help="Décrivez le tableau clinique en langage naturel — l'IA sélectionne "
                 "les tests les plus pertinents parmi les 96 disponibles.")

        # Reset si champ IA vidé
        if not tmpl_search_ai:
            S.pop("tmpl_ai_ids", None)
            S.pop("tmpl_ai_prev", None)

        # Recherche IA — identique à 2_Bilans.py (pattern éprouvé)
        if tmpl_search_ai and S.get("tmpl_ai_prev") != tmpl_search_ai:
            S["tmpl_ai_prev"] = tmpl_search_ai
            with st.spinner("Recherche IA…"):
                try:
                    import anthropic as _ant, json as _jj, re as _re
                    _catalog = [{"id": tid, "nom": cls.meta().get("nom",""),
                                 "tags": cls.meta().get("tags",[]),
                                 "desc": cls.meta().get("description","")}
                                for tid, cls in tests_map.items()
                                if tid not in selected_set]
                    _msg = _ant.Anthropic().messages.create(
                        model="claude-haiku-4-5", max_tokens=600,
                        system=('Tu es un assistant physiothérapeute. '
                                'Reponds UNIQUEMENT avec un JSON {"ids":[...]} '
                                'contenant TOUS les IDs de tests pertinents.'),
                        messages=[{"role":"user","content":
                            "Catalogue: " + _jj.dumps(_catalog, ensure_ascii=False)
                            + "\nDescription: " + tmpl_search_ai}])
                    _raw = _msg.content[0].text
                    # Parser robuste : strip markdown puis JSON, fallback regex
                    _clean = _re.sub(r'```\w*\n?', '', _raw).strip()
                    try:
                        S["tmpl_ai_ids"] = _jj.loads(_clean).get("ids", [])
                    except Exception:
                        _m = _re.search(r'"ids"\s*:\s*\[([^\]]*)\]', _raw, _re.DOTALL)
                        if _m:
                            try: S["tmpl_ai_ids"] = _jj.loads(f'[{_m.group(1)}]')
                            except: S["tmpl_ai_ids"] = []
                        else:
                            S["tmpl_ai_ids"] = []
                    if S["tmpl_ai_ids"]:
                        st.caption(f"✨ {len(S['tmpl_ai_ids'])} suggestion(s) IA")
                except Exception:
                    S["tmpl_ai_ids"] = []

        # Construire la liste filtrée des tests disponibles
        ai_ids = S.get("tmpl_ai_ids", [])
        all_available = [(tid, cls) for tid, cls in
                         sorted(tests_map.items(), key=lambda x: x[1].tab_label())
                         if tid not in selected_set]

        if tmpl_search_ai and ai_ids:
            # IA : montrer uniquement les suggestions, pas les autres
            filtered_avail = [(tid, cls) for tid, cls in all_available if tid in ai_ids]
        elif tmpl_search_q.strip():
            import unicodedata as _ud
            def _norm(s):
                return _ud.normalize("NFD", s.lower()).encode("ascii","ignore").decode()
            q = _norm(tmpl_search_q.strip())
            filtered_avail = [(tid, cls) for tid, cls in all_available
                              if q in _norm(cls.tab_label())
                              or q in _norm(cls.meta().get("nom",""))
                              or any(q in _norm(t) for t in cls.meta().get("tags",[]))
                              or q in _norm(cls.meta().get("description",""))]
        else:
            filtered_avail = all_available

        # Afficher tous les tests dans un seul expander (plus de catégories)
        if not filtered_avail:
            st.info("Aucun test ne correspond à la recherche.")
        else:
            label_count = f"{len(filtered_avail)} test(s)"
            if tmpl_search_q.strip() or tmpl_search_ai.strip():
                st.caption(label_count + " trouvé(s)")
                if tmpl_search_ai and ai_ids:
                    st.caption(f"✨ {len(filtered_avail)} test(s) suggérés par l'IA")
                cols = st.columns(3)
                for j, (tid, cls) in enumerate(filtered_avail):
                    if cols[j%3].button(cls.tab_label(), key=f"add_{tid}",
                                        use_container_width=True,
                                        help=" · ".join(cls.meta().get("tags",[])[:3])):
                        selected_ids.append(tid)
                        S["tmpl_selected"] = selected_ids
                        S.pop("tmpl_ai_ids", None)
                        S.pop("tmpl_ai_prev", None)
                        st.rerun()
            else:
                with st.expander(f"📋 Tous les tests — {len(filtered_avail)} disponibles",
                                 expanded=False):
                    cols = st.columns(3)
                    for j, (tid, cls) in enumerate(filtered_avail):
                        if cols[j%3].button(cls.tab_label(), key=f"add_{tid}",
                                            use_container_width=True,
                                            help=" · ".join(cls.meta().get("tags",[])[:3])):
                            selected_ids.append(tid)
                            S["tmpl_selected"] = selected_ids; st.rerun()

        st.markdown("---")
        can_save = bool(nom.strip()) and len(selected_ids)>0
        cs, cc2, _ = st.columns([2,1.5,4])
        if cs.button("💾 Enregistrer", type="primary", use_container_width=True, disabled=not can_save):
            tid_save = edit_id if is_edit else _make_tmpl_id(nom)
            ok = save_cabinet_template(tid_save, nom.strip(), icone, desc.strip(),
                                       json.dumps(selected_ids), True)
            if ok:
                st.success(f"✅ Template « {nom} » enregistré !")
                S.pop("tmpl_selected",None); S["tmpl_mode"]="liste"; st.rerun()
            else:
                st.error("❌ Erreur sauvegarde.")
        if cc2.button("Annuler", use_container_width=True):
            S.pop("tmpl_selected",None); S["tmpl_mode"]="liste"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET THÉRAPEUTES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_thera:
    st.markdown("### 👥 Gestion des thérapeutes")
    st.info("🚧 Fonctionnalité disponible après migration PostgreSQL. En attendant, les thérapeutes sont gérés directement dans Google Sheets.")
    st.markdown("**Thérapeutes actifs** — consultez la feuille `Patients` > colonne `praticien` pour voir les noms utilisés.")
    from utils.db import get_all_patients
    try:
        df = get_all_patients()
        if "praticien" in df.columns:
            theras = df["praticien"].dropna().unique()
            theras = [t for t in theras if str(t).strip()]
            if theras:
                for t in sorted(theras):
                    n = len(df[df["praticien"]==t])
                    st.markdown(f"- **{t}** — {n} patient(s)")
            else:
                st.caption("Aucun praticien enregistré.")
    except Exception as e:
        st.warning(f"Impossible de charger les données : {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET STATISTIQUES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_stats:
    st.markdown("### 📊 Statistiques du cabinet")
    from utils.db import get_all_patients, get_audit_log_all
    import pandas as pd

    try:
        df_patients = get_all_patients()
        n_patients = len(df_patients)
    except: n_patients = 0

    try:
        df_audit = get_audit_log_all(limit=500)
        n_bilans = len(df_audit[df_audit["action"]=="creation_bilan"]) if not df_audit.empty and "action" in df_audit.columns else 0
        n_cas    = len(df_audit[df_audit["action"]=="creation_cas"]) if not df_audit.empty and "action" in df_audit.columns else 0
    except: n_bilans=0; n_cas=0; df_audit=pd.DataFrame()

    c1,c2,c3 = st.columns(3)
    c1.metric("Patients", n_patients)
    c2.metric("Cas créés", n_cas)
    c3.metric("Bilans créés", n_bilans)

    if not df_audit.empty and "action" in df_audit.columns:
        st.markdown("---")
        st.markdown("**Activité récente (30 dernières actions)**")
        st.dataframe(df_audit.head(30)[["timestamp","therapeute","action","cas_id"]],
                     use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET VALIDATION TESTS (super admin uniquement)
# ═══════════════════════════════════════════════════════════════════════════════
if tab_valid:
    with tab_valid:
        st.markdown("### 🧪 Validation des tests")
        st.caption("Suivi des 4 critères de qualité pour chaque test de la bibliothèque.")
        from core.registry import all_tests as _at
        from utils.db import get_all_validations, save_validation

        _load_all_tests_admin()
        tests_map = _at()
        validations = get_all_validations()

        FIXED_PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets","fiches")
        CRITERES = [
            ("contenu",          "✅ Contenu"),
            ("pdf_vierge",       "📄 PDF vierge"),
            ("valeurs_imprimees","🖨️ Valeurs"),
            ("graphique",        "📊 Graphique"),
        ]
        VAL_STYLE = {"validé":("✅","#e8f5e9","#388e3c"),"en_cours":("🔄","#fff8e1","#f9a825"),"non_testé":("⬜","#f5f5f5","#999")}

        # Filtres
        fa, fb = st.columns(2)
        filt_stat = fa.selectbox("Filtre statut",["Tous","✅ Validé","🔄 En cours","⬜ Non testé"],key="admin_val_filt")
        filt_pdf  = fb.checkbox("Avec PDF fixe uniquement", key="admin_val_pdf")
        stat_map  = {"Tous":None,"✅ Validé":"validé","🔄 En cours":"en_cours","⬜ Non testé":"non_testé"}
        filt_s    = stat_map[filt_stat]

        all_items = list(tests_map.items())
        if filt_s:
            all_items = [(t,c) for t,c in all_items if validations.get(t,{}).get("statut","non_testé")==filt_s]
        if filt_pdf:
            all_items = [(t,c) for t,c in all_items if c.meta().get("has_fixed_pdf") or os.path.exists(os.path.join(FIXED_PDF_DIR,f"{t}.pdf"))]

        # Compteurs
        total = len(tests_map)
        n_val = sum(1 for v in validations.values() if v.get("statut")=="validé")
        n_enc = sum(1 for v in validations.values() if v.get("statut")=="en_cours")
        m1,m2,m3 = st.columns(3)
        m1.metric("✅ Validés",f"{n_val}/{total}")
        m2.metric("🔄 En cours",n_enc)
        m3.metric("⬜ Non testés",total-n_val-n_enc)
        st.markdown(f"<div style='background:#eee;border-radius:4px;height:8px;margin:8px 0'><div style='background:#388e3c;width:{int(n_val/max(total,1)*100)}%;height:8px;border-radius:4px'></div></div>", unsafe_allow_html=True)
        st.markdown("---")

        st.caption(f"{len(all_items)} test(s) affichés")

        for tid, cls in all_items:
            m = cls.meta()
            vdata    = validations.get(tid, {})
            vstat    = vdata.get("statut","non_testé")
            vcrit    = vdata.get("criteres",{})
            vnotes   = vdata.get("notes","")
            vicon,vbg,vcol = VAL_STYLE.get(vstat,VAL_STYLE["non_testé"])
            has_fixed = m.get("has_fixed_pdf") or os.path.exists(os.path.join(FIXED_PDF_DIR,f"{tid}.pdf"))

            with st.expander(f"{vicon} {cls.tab_label()}  —  {vstat.replace('_',' ')}", expanded=False):
                cc1,cc2 = st.columns(2)
                crit_vals = {}
                for key, label in CRITERES:
                    is_auto = key=="pdf_vierge" and has_fixed
                    val = has_fixed if is_auto else vcrit.get(key, False)
                    checked = (cc1 if CRITERES.index((key,label))%2==0 else cc2).checkbox(
                        label, value=val, disabled=is_auto,
                        key=f"vadm_{tid}_{key}",
                        help="Auto : PDF fixe présent" if is_auto else "")
                    crit_vals[key] = val if is_auto else checked

                n_ok = sum(crit_vals.values())
                auto_stat = "validé" if n_ok==4 else "en_cours" if n_ok>0 else "non_testé"
                prog_col = "#388e3c" if n_ok==4 else "#f57c00" if n_ok>0 else "#ddd"
                st.markdown(f"<div style='background:#eee;border-radius:4px;height:5px;margin:6px 0'><div style='background:{prog_col};width:{n_ok*25}%;height:5px;border-radius:4px'></div></div><span style='font-size:11px;color:#666'>{n_ok}/4 critères</span>", unsafe_allow_html=True)

                new_notes = st.text_area("Notes", value=vnotes, height=60, key=f"vadm_notes_{tid}",
                    placeholder="Bugs, comportement attendu…")
                if st.button("💾 Enregistrer", key=f"vadm_save_{tid}", type="primary"):
                    if save_validation(tid, auto_stat, crit_vals, new_notes):
                        st.success(f"✅ {auto_stat}")
                        get_all_validations.clear(); st.rerun()
                    else:
                        st.error("❌ Erreur GSheets.")


# ── Bouton regénération _bilans_fields.py ────────────────────────────────────
if tab_valid:
    with tab_valid:
        st.markdown("---")
        st.markdown("### 🔧 Maintenance")
        if st.button("♻️ Regénérer `_bilans_fields.py`",
                     help="À faire après ajout de nouveaux tests"):
            try:
                from core.registry import all_tests as _at_regen
                import pathlib as _pl
                _tests  = _at_regen()
                _fields = []
                _seen   = set()
                for _tid, _cls in _tests.items():
                    for _f in _cls.fields():
                        if _f not in _seen:
                            _fields.append(_f)
                            _seen.add(_f)
                _lines = [
                    "# Auto-generated — champs plats de tous les tests",
                    f"ALL_TEST_FIELDS = {repr(_fields)}",
                ]
                _content = "\n".join(_lines) + "\n"
                _path = _pl.Path(__file__).parent.parent / "utils" / "_bilans_fields.py"
                _path.write_text(_content, encoding="utf-8")
                st.success(f"✅ Regénéré — {len(_fields)} colonnes, {len(_tests)} tests")
                st.code(_content[:200] + "...", language="python")
            except Exception as _e:
                st.error(f"❌ Erreur : {_e}")

# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET PDFs FIXES (super admin uniquement)
# ═══════════════════════════════════════════════════════════════════════════════
if tab_pdf:
    with tab_pdf:
        st.markdown("### 📄 PDFs fixes — fiches questionnaires")
        st.info("Générez les fiches vierges depuis l'app, validez-les, puis uploadez-les dans `assets/fiches/{test_id}.pdf`.")

        FIXED_PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets","fiches")
        _load_all_tests_admin()
        tests_map = _at()

        os.makedirs(FIXED_PDF_DIR, exist_ok=True)
        existing_pdfs = {f.replace(".pdf","") for f in os.listdir(FIXED_PDF_DIR) if f.endswith(".pdf")}

        from utils.pdf import generate_tests_pdf

        col_a, col_b = st.columns(2)
        col_a.metric("Tests avec PDF fixe", len(existing_pdfs))
        col_b.metric("Tests sans PDF fixe", len(tests_map)-len(existing_pdfs))

        st.markdown("---")

        # ── Régénérer TOUTES les fiches → ZIP ─────────────────────────────────
        st.markdown("**🔄 Regénérer toutes les fiches (nouveau logo ou mise à jour)**")
        st.caption("Génère toutes les fiches en une fois et les emballe dans un ZIP. "
                   "Extrayez le ZIP et commitez le contenu dans `assets/fiches/` du repo.")

        regen_scope = st.radio("Périmètre",
            ["Tous les tests","Seulement ceux avec PDF fixe existant"],
            horizontal=True, key="regen_scope")

        if st.button("⚙️ Générer le ZIP de toutes les fiches", type="primary", key="regen_all"):
            if regen_scope == "Seulement ceux avec PDF fixe existant":
                to_gen = [tid for tid in tests_map if tid in existing_pdfs]
            else:
                to_gen = list(tests_map.keys())

            import zipfile, io
            zip_buf = io.BytesIO()
            errors  = []
            bar = st.progress(0, text="Génération en cours…")

            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, tid in enumerate(to_gen):
                    bar.progress((i+1)/len(to_gen), text=f"{i+1}/{len(to_gen)} — {tid}")
                    try:
                        pdf_bytes = generate_tests_pdf([tid], {})
                        zf.writestr(f"{tid}.pdf", pdf_bytes)
                    except Exception as e:
                        errors.append(f"{tid}: {e}")

            bar.empty()
            zip_buf.seek(0)
            st.session_state["admin_zip_bytes"] = zip_buf.read()

            if errors:
                err_msg = "⚠️ " + str(len(errors)) + " erreur(s) : " + " | ".join(errors[:5])
            else:
                st.success(f"✅ {len(to_gen)} fiches générées.")

        if st.session_state.get("admin_zip_bytes"):
            st.download_button(
                f"📥 Télécharger le ZIP",
                data=st.session_state["admin_zip_bytes"],
                file_name=f"fiches_36_9_bilans_{datetime.now().strftime('%Y%m%d')}.zip",
                mime="application/zip",
                key="dl_zip_all")
            st.caption("→ Extraire le ZIP · Copier les `.pdf` dans `assets/fiches/` · Commiter")

        st.markdown("---")

        # ── Générer une fiche individuelle ─────────────────────────────────────
        st.markdown("**Générer une fiche individuelle :**")
        sel_test = st.selectbox("Test", list(tests_map.keys()),
            format_func=lambda t: tests_map[t].tab_label() if t in tests_map else t,
            key="pdf_sel_test")

        if st.button("⚙️ Générer cette fiche", use_container_width=True, key="gen_one"):
            with st.spinner("Génération…"):
                try:
                    pdf_bytes = generate_tests_pdf([sel_test], {})
                    st.session_state["admin_pdf_bytes"] = pdf_bytes
                    st.session_state["admin_pdf_tid"]   = sel_test
                except Exception as e:
                    st.error(f"Erreur : {e}")

        if st.session_state.get("admin_pdf_bytes") and st.session_state.get("admin_pdf_tid") == sel_test:
            st.download_button("📥 Télécharger la fiche",
                data=st.session_state["admin_pdf_bytes"],
                file_name=f"fiche_{sel_test}.pdf",
                mime="application/pdf", key="admin_dl_pdf")
            st.caption("Après validation → placer dans `assets/fiches/` du repo et commiter.")

        st.markdown("---")

        # ── État des PDFs fixes ────────────────────────────────────────────────
        st.markdown("**État des PDFs fixes :**")
        import pandas as pd
        rows = []
        for tid, cls in sorted(tests_map.items(), key=lambda x: x[1].tab_label()):
            has_f = tid in existing_pdfs
            rows.append({
                "Test":     cls.tab_label(),
                "ID":       tid,
                "PDF fixe": "✅ Oui" if has_f else "—",
                "meta()":   "✅" if cls.meta().get("has_fixed_pdf") else "—",
            })
        df_pdf = pd.DataFrame(rows)
        st.dataframe(df_pdf, use_container_width=True, hide_index=True)
        n_meta_ok = sum(1 for r in rows if r["meta()"]=="✅")
        n_file_ok = sum(1 for r in rows if r["PDF fixe"]=="✅ Oui")
        if n_meta_ok != n_file_ok:
            st.warning(f"⚠️ {n_file_ok} fichiers dans `assets/fiches/` mais {n_meta_ok} tests avec `has_fixed_pdf:True` dans meta(). Pensez à synchroniser.")


# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET FEEDBACK (super admin uniquement)
# ═══════════════════════════════════════════════════════════════════════════════
if tab_fb:
    with tab_fb:
        st.markdown("### 💬 Gestion des feedbacks communauté")
        from utils.db import (get_sheet, admin_update_feedback, admin_delete_feedback)
        from datetime import date as _date
        import pandas as _pd

        STATUTS_COULEUR = {
            "En vote":"#F59E0B","Accepté":"#10B981","En développement":"#3B82F6",
            "Livré":"#6366F1","Refusé":"#EF4444","En traitement":"#F97316",
        }
        TOUS_STATUTS = list(STATUTS_COULEUR.keys())
        TYPES_ICO = {"Bug":"🐛","Suggestion":"💡","Amélioration":"⚡","Bibliothèque":"📚"}

        def _load_fb():
            try:
                df = get_sheet("Feedback")
                if df.empty: return _pd.DataFrame()
                df["votes_pour"]   = _pd.to_numeric(df.get("votes_pour",0),   errors="coerce").fillna(0).astype(int)
                df["votes_contre"] = _pd.to_numeric(df.get("votes_contre",0), errors="coerce").fillna(0).astype(int)
                if "reponse_admin" not in df.columns: df["reponse_admin"] = ""
                return df
            except Exception as e:
                st.error(f"Erreur chargement : {e}"); return _pd.DataFrame()

        df_fb = _load_fb()

        if df_fb.empty:
            st.info("Aucun feedback enregistré.")
        else:
            # Compteurs
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Total",       len(df_fb))
            m2.metric("🐛 Bugs",     len(df_fb[df_fb["type"]=="Bug"]))
            m3.metric("💡 En vote",  len(df_fb[df_fb["statut"]=="En vote"]))
            m4.metric("✅ Livrés",   len(df_fb[df_fb["statut"]=="Livré"]))
            st.markdown("---")

            # Filtres
            fa, fb2 = st.columns(2)
            f_type   = fa.selectbox("Type",   ["Tous","Bug","Suggestion","Amélioration","Bibliothèque"], key="fb_ftype")
            f_statut = fb2.selectbox("Statut", ["Tous"]+TOUS_STATUTS, key="fb_fstat")

            df_view = df_fb.copy().sort_values("date_creation", ascending=False)
            if f_type   != "Tous": df_view = df_view[df_view["type"]   == f_type]
            if f_statut != "Tous": df_view = df_view[df_view["statut"] == f_statut]

            st.caption(f"{len(df_view)} feedback(s)")

            for _, row in df_view.iterrows():
                fid     = row["id"]
                couleur = STATUTS_COULEUR.get(row["statut"],"#9CA3AF")
                ico     = TYPES_ICO.get(row["type"],"❓")
                with st.expander(
                    f'{ico} #{fid} — {row["titre"]}  ·  '
                    f'[{row["statut"]}]  ·  {row["auteur"]}',
                    expanded=False):

                    st.markdown(
                        f'**Auteur :** {row["auteur"]} · **Type :** {ico} {row["type"]} · **Soumis le :** {row["date_creation"]}')
                    st.markdown(f'**Description :** {row["description"]}')
                    if str(row.get("deadline_vote","")).strip():
                        st.caption("Vote jusqu'au " + str(row["deadline_vote"]) + " · ✅ " + str(int(row["votes_pour"])) + " / ❌ " + str(int(row["votes_contre"])))
                    if str(row.get("reponse_admin","")).strip():
                        st.info(f'💬 Réponse actuelle : {row["reponse_admin"]}')
                    st.markdown("---")

                    ca, cb = st.columns(2)
                    nouveau_statut = ca.selectbox("Statut", TOUS_STATUTS,
                        index=TOUS_STATUTS.index(row["statut"]) if row["statut"] in TOUS_STATUTS else 0,
                        key=f"fb_stat_{fid}")
                    forcer_cloture = False
                    if row["statut"] == "En vote":
                        forcer_cloture = ca.checkbox("⏱️ Clôturer le vote maintenant", key=f"fb_cl_{fid}")
                    reponse = cb.text_area("Réponse (visible par tous)", value=row.get("reponse_admin",""),
                        height=100, key=f"fb_rep_{fid}")

                    cs2, cd2 = st.columns([3,1])
                    if cs2.button("💾 Enregistrer", key=f"fb_save_{fid}", type="primary", use_container_width=True):
                        deadline_override = str(_date.today()) if forcer_cloture else None
                        if admin_update_feedback(fid, nouveau_statut, reponse.strip(), deadline_override):
                            st.success("✅ Mis à jour."); st.rerun()
                        else:
                            st.error("❌ Erreur mise à jour.")
                    if cd2.button("🗑️ Supprimer", key=f"fb_del_{fid}", use_container_width=True):
                        if admin_delete_feedback(fid):
                            st.success("🗑️ Supprimé."); st.rerun()
                        else:
                            st.error("❌ Erreur suppression.")


# ═══════════════════════════════════════════════════════════════════════════════
# ONGLET AUDIT LOG (super admin uniquement)
# ═══════════════════════════════════════════════════════════════════════════════
if tab_audit:
    with tab_audit:
        st.markdown("### 📋 Audit Log")
        from utils.db import get_audit_log_all
        import pandas as pd

        n_rows = st.slider("Nombre de lignes", 50, 500, 100, 50, key="audit_rows")
        try:
            df = get_audit_log_all(limit=n_rows)
            if df.empty:
                st.info("Aucune entrée dans l'audit log.")
            else:
                # Filtres
                if "action" in df.columns:
                    actions = ["Toutes"] + sorted(df["action"].dropna().unique().tolist())
                    filt_action = st.selectbox("Action", actions, key="audit_action_filt")
                    if filt_action != "Toutes":
                        df = df[df["action"]==filt_action]
                st.caption(f"{len(df)} entrées")
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erreur chargement audit log : {e}")

        if st.button("🔄 Actualiser", key="audit_refresh"):
            get_audit_log_all.clear() if hasattr(get_audit_log_all,"clear") else None
            st.rerun()
    # Auto-découverte de tous les tests dans tests/
