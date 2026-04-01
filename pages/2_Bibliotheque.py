"""pages/2_Bibliotheque.py — Bibliothèque des tests cliniques"""
import streamlit as st

st.set_page_config(page_title="Bibliothèque — 36.9 Bilans",
                   page_icon="📚", layout="wide")

@st.cache_resource
def _load_all():
    import importlib
    # Templates (importent leurs propres tests)
    for m in ["templates.shv","templates.equilibre","templates.bpco",
              "templates.lombalgie","templates.neutre","templates.epaule_douloureuse",
              "templates.cervicalgie","templates.genou","templates.hanche",
              "templates.membre_superieur"]:
        try: importlib.import_module(m)
        except Exception as e: st.warning(f"{m}: {e}")
    # Tests non liés à un template (batch 1)
    for m in [
        "tests.questionnaires.psfs","tests.questionnaires.groc",
        "tests.questionnaires.eq5d","tests.questionnaires.ndi",
        "tests.questionnaires.koos","tests.questionnaires.hoos",
        "tests.questionnaires.lysholm","tests.questionnaires.dash",
        "tests.questionnaires.lefs","tests.questionnaires.womac",
        "tests.questionnaires.spadi","tests.questionnaires.constant_murley",
        "tests.questionnaires.prtee","tests.questionnaires.bctq",
        "tests.questionnaires.roland_morris","tests.questionnaires.start_back",
        "tests.questionnaires.fabq","tests.questionnaires.dn4",
        "tests.questionnaires.faos","tests.questionnaires.kujala",
        "tests.questionnaires.acl_rsi","tests.questionnaires.hagos",
        "tests.questionnaires.ikdc","tests.questionnaires.csi",
        "tests.questionnaires.qbpds","tests.questionnaires.atrs",
        "tests.questionnaires.wosi",
        "tests.questionnaires.visa_a","tests.questionnaires.visa_p",
        "tests.questionnaires.visa_h","tests.questionnaires.visa_g",
        "tests.questionnaires.cait","tests.questionnaires.tegner",
        "tests.questionnaires.dhi","tests.questionnaires.hit6",
        "tests.tests_cliniques.nrs",
        # Tests batch 2
        "tests.questionnaires.borg_rpe","tests.questionnaires.sgrq",
        "tests.questionnaires.lcadl","tests.questionnaires.pcfs",
        "tests.questionnaires.psqi","tests.questionnaires.abc_scale",
        "tests.questionnaires.mini_bestest","tests.questionnaires.fes_i",
        "tests.questionnaires.barthel","tests.questionnaires.ten_mwt",
        "tests.questionnaires.ashworth","tests.questionnaires.iciq_ui",
        "tests.questionnaires.pfdi20","tests.questionnaires.pcs",
        "tests.questionnaires.phq9","tests.questionnaires.gad7",
        "tests.questionnaires.isi","tests.questionnaires.haq",
        "tests.questionnaires.basdai","tests.questionnaires.frailty_scale",
        "tests.questionnaires.frail_scale","tests.questionnaires.gait_speed",
        "tests.questionnaires.k_ses","tests.questionnaires.prwe",
        "tests.questionnaires.bpi",
    ]:
        try: importlib.import_module(m)
        except Exception as e: st.warning(f"{m}: {e}")
    return True

_load_all()

from core.registry import all_tests
from utils.search import search_items
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import get_all_validations, save_validation

tests_map = all_tests()

# ── Sidebar ────────────────────────────────────────────────────────────────────
_validations = get_all_validations()
_VAL_STYLE = {
    "validé":    ("✅", "#e8f5e9", "#388e3c"),
    "en_cours":  ("🔄", "#fff8e1", "#f9a825"),
    "non_testé": ("⬜", "#f5f5f5", "#999999"),
}

with st.sidebar:
    st.markdown("**⚙️ Affichage**")
    layout = st.radio("Mode d'affichage",
        options=["liste","cartes","tuiles","table"],
        format_func=lambda x: {
            "liste":"☰ Liste avec accents",
            "cartes":"⊟ Cartes larges",
            "tuiles":"⊞ Tuiles icône",
            "table":"▤ Table enrichie"
        }[x],
        index=["liste","cartes","tuiles","table"].index(
            st.session_state.get("bib_layout","liste")),
        label_visibility="collapsed")
    st.session_state["bib_layout"] = layout
    st.markdown("---")
    st.markdown("**🧪 Validation**")
    _val_filter = st.selectbox("Statut",
        ["Tous", "✅ Validé", "🔄 En cours", "⬜ Non testé"],
        key="bib_val_filter", label_visibility="collapsed")
    # Compteurs
    _counts = {"validé": 0, "en_cours": 0, "non_testé": 0}
    for _v in _validations.values():
        _s = _v.get("statut","non_testé")
        if _s in _counts: _counts[_s] += 1
    _total = len(list(all_tests().keys()))
    _counts["non_testé"] = _total - _counts["validé"] - _counts["en_cours"]
    st.caption(
        f"✅ {_counts['validé']} · "
        f"🔄 {_counts['en_cours']} · "
        f"⬜ {_counts['non_testé']} / {_total}")

st.markdown("""<style>
.bib-readonly input,.bib-readonly textarea,.bib-readonly select{pointer-events:none!important;opacity:.7}
.tag{font-size:11px;padding:2px 8px;border-radius:20px;background:var(--color-background-secondary);
     border:0.5px solid var(--color-border-tertiary);color:var(--color-text-secondary);
     display:inline-block;margin:1px 2px}
.list-item{display:flex;align-items:center;gap:12px;padding:10px 14px;
           border:0.5px solid var(--color-border-tertiary);border-radius:10px;
           margin-bottom:6px;background:var(--color-background-primary)}
.list-item:hover{border-color:var(--color-border-secondary);background:var(--color-background-secondary)}
.list-accent{width:4px;min-height:40px;border-radius:2px;flex-shrink:0}
.list-title{font-size:13px;font-weight:500;margin-bottom:2px}
.list-desc{font-size:12px;color:var(--color-text-secondary)}
.card-b{border:0.5px solid var(--color-border-tertiary);border-radius:12px;overflow:hidden;
        background:var(--color-background-primary);margin-bottom:8px}
.card-b:hover{border-color:var(--color-border-secondary)}
.card-b-head{padding:12px 16px;display:flex;align-items:center;gap:12px}
.card-b-ico{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;
            justify-content:center;font-size:18px;flex-shrink:0}
.card-b-title{font-size:14px;font-weight:500}
.card-b-desc{font-size:12px;color:var(--color-text-secondary);margin-top:1px}
.card-b-foot{padding:8px 16px;border-top:0.5px solid var(--color-border-tertiary);
             background:var(--color-background-secondary)}
.tile-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.tile{border:0.5px solid var(--color-border-tertiary);border-radius:10px;padding:12px;
      background:var(--color-background-primary);display:flex;flex-direction:column;gap:5px}
.tile:hover{border-color:var(--color-border-secondary);background:var(--color-background-secondary)}
.tile-ico{font-size:22px;line-height:1}
.tile-title{font-size:12px;font-weight:500;line-height:1.3}
.tile-cat{font-size:11px;color:var(--color-text-secondary)}
.rich-table{width:100%;border-collapse:collapse}
.rich-table th{font-size:11px;color:var(--color-text-secondary);font-weight:500;
               padding:6px 12px;border-bottom:0.5px solid var(--color-border-tertiary);text-align:left}
.rich-table td{padding:9px 12px;font-size:13px;vertical-align:middle;
               border-bottom:0.5px solid var(--color-border-tertiary)}
.rich-table tr:hover td{background:var(--color-background-secondary)}
.pill-green{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;background:#EAF3DE;color:#3B6D11}
.pill-none{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;background:var(--color-background-secondary);color:var(--color-text-secondary)}
</style>""", unsafe_allow_html=True)

sel_key = "bib_selected_test"
selected_tid = st.session_state.get(sel_key)

_ACCENT_COLORS = ["#378ADD","#1D9E75","#D85A30","#7F77DD","#EF9F27","#D4537E"]
_ICO_BG = ["#E6F1FB","#E1F5EE","#FAECE7","#EEEDFE","#FAEEDA","#FBEAF0"]
_TEST_TO_Q = {
    "had":"had","sf12":"sf12","hvt":"hvt","bolt":"bolt",
    "nijmegen":"nijmegen","mrc_dyspnee":"mrc","comorbidites":"comorb",
    "testing_mi":"muscle","leg_press":"leg_press",
    "odi":"odi","tampa":"tampa","orebro":"orebro",
    "mmrc":"mmrc_bpco","cat":"cat_bpco",
    "quick_dash":"quick_dash","ases":"ases",
}

# ── Vue détail ─────────────────────────────────────────────────────────────────
if selected_tid and selected_tid in tests_map:
    cls = tests_map[selected_tid]
    m = cls.meta()
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f"## {cls.tab_label()}")
        if m.get("description"): st.caption(m["description"])
        if m.get("tags"): st.markdown(" ".join([f"`{t}`" for t in m["tags"]]))
    with c2:
        if st.button("✖ Fermer", use_container_width=True):
            st.session_state.pop(sel_key, None)
            st.rerun()
    st.markdown("---")
    st.markdown('<div class="bib-readonly">', unsafe_allow_html=True)
    try:
        cls().render(lambda k, default="": default, f"bib_{selected_tid}")
    except Exception as e:
        st.warning(f"Aperçu non disponible : {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    # ── Validation ──────────────────────────────────────────────────────────
    st.markdown("---")
    _vdata  = _validations.get(selected_tid, {})
    _vstat  = _vdata.get("statut", "non_testé")
    _vnotes = _vdata.get("notes", "")
    _vicon, _vbg, _vcol = _VAL_STYLE.get(_vstat, _VAL_STYLE["non_testé"])
    st.markdown(
        f"<span style='display:inline-block;padding:3px 12px;background:{_vbg};"
        f"border-radius:12px;font-size:0.82rem;color:{_vcol};font-weight:600'>"
        f"{_vicon} {_vstat.replace('_',' ').capitalize()}</span>",
        unsafe_allow_html=True)
    with st.expander("🧪 Modifier le statut", expanded=(_vstat == "non_testé")):
        _opts  = ["non_testé", "en_cours", "validé"]
        _idx   = _opts.index(_vstat) if _vstat in _opts else 0
        _new_stat = st.radio("Statut", _opts, index=_idx, horizontal=True,
            format_func=lambda x: {"non_testé":"⬜ Non testé",
                                    "en_cours": "🔄 En cours",
                                    "validé":   "✅ Validé"}[x],
            key=f"val_stat_{selected_tid}")
        _new_notes = st.text_area("Notes / observations", value=_vnotes, height=80,
            key=f"val_notes_{selected_tid}",
            placeholder="Points à vérifier, bugs, comportement attendu…")
        if st.button("💾 Enregistrer", type="primary", key=f"val_save_{selected_tid}"):
            if save_validation(selected_tid, _new_stat, _new_notes):
                st.success("✅ Sauvegardé.")
                st.rerun()
            else:
                st.error("❌ Erreur GSheets.")

    st.markdown("---")
    from utils.pdf import generate_tests_pdf
    _pdf_key = f"bib_pdf_{selected_tid}"
    if st.button("🖨️ Générer fiche PDF", type="primary", key=f"gen_{selected_tid}"):
        with st.spinner("Génération…"):
            try: st.session_state[_pdf_key] = generate_tests_pdf([selected_tid], {})
            except Exception as e: st.error(f"Erreur : {e}")
    if st.session_state.get(_pdf_key):
        st.download_button("📥 Télécharger",
            data=st.session_state[_pdf_key],
            file_name=f"fiche_{selected_tid}.pdf",
            mime="application/pdf", key=f"dl_{selected_tid}")
    st.stop()

# ── Recherche ─────────────────────────────────────────────────────────────────
st.markdown("## 📚 Bibliothèque des tests")
s1, s2 = st.columns([3, 2])
search_q = s1.text_input("🔍 Rechercher", placeholder="ex: épaule, Berg, ODI…", key="bib_search")
ai_q     = s2.text_input("🤖 Décrire le patient", placeholder="ex: patient âgé qui chute…", key="bib_ai")

if ai_q and st.session_state.get("bib_ai_prev") != ai_q:
    st.session_state["bib_ai_prev"] = ai_q
    with st.spinner("Recherche IA…"):
        try:
            import anthropic, json, re
            _catalog = [{"id": tid, "nom": cls.meta().get("nom",""),
                         "tags": cls.meta().get("tags",[]),
                         "desc": cls.meta().get("description","")}
                        for tid, cls in tests_map.items()]
            _msg = anthropic.Anthropic().messages.create(
                model="claude-haiku-4-5", max_tokens=600,
                system='Reponds UNIQUEMENT avec un JSON {"ids":[...]} avec TOUS les IDs pertinents.',
                messages=[{"role":"user","content":
                    "Catalogue: " + json.dumps(_catalog, ensure_ascii=False) +
                    "\nDescription: " + ai_q}])
            _m = re.search(r'\{"ids":\s*\[[^\]]*\]\}', _msg.content[0].text, re.DOTALL)
            st.session_state["bib_ai_results"] = json.loads(_m.group()).get("ids",[]) if _m else []
        except Exception:
            st.session_state["bib_ai_results"] = []

ai_ids = st.session_state.get("bib_ai_results", [])
all_items = list(tests_map.items())

if search_q:
    def _key(item):
        m = item[1].meta()
        return f"{m.get('nom','')} {m.get('description','')} {item[0]}", m.get("tags",[])
    filtered = search_items(search_q, all_items, _key)
elif ai_ids:
    filtered = [(tid, tests_map[tid]) for tid in ai_ids if tid in tests_map]
    if filtered: st.caption(f"✨ {len(filtered)} suggestion(s) IA")
else:
    filtered = all_items

# Filtre validation
_val_map = {"Tous": None, "✅ Validé": "validé",
            "🔄 En cours": "en_cours", "⬜ Non testé": "non_testé"}
_val_sel = _val_map.get(_val_filter)
if _val_sel:
    filtered = [(tid, cls) for tid, cls in filtered
                if _validations.get(tid, {}).get("statut","non_testé") == _val_sel]

st.caption(f"{len(filtered)} test(s)")
st.markdown("")

def _open(tid):
    st.session_state[sel_key] = tid
    st.rerun()

# ── Layout A : Liste avec accents ─────────────────────────────────────────────
if layout == "liste":
    for i, (tid, cls) in enumerate(filtered):
        m = cls.meta()
        tags = m.get("tags", [])[:3]
        desc = m.get("description","")[:90] + ("…" if len(m.get("description",""))>90 else "")
        color = _ACCENT_COLORS[i % len(_ACCENT_COLORS)]
        tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
        _vstat = _validations.get(tid, {}).get("statut","non_testé")
        _vicon = _VAL_STYLE.get(_vstat, _VAL_STYLE["non_testé"])[0]
        st.markdown(f"""<div class="list-item">
  <div class="list-accent" style="background:{color}"></div>
  <div style="flex:1;min-width:0">
    <div class="list-title">{cls.tab_label()}</div>
    <div class="list-desc">{desc}</div>
  </div>
  <div style="flex-shrink:0;margin-right:6px;font-size:1rem" title="{_vstat}">{_vicon}</div>
  <div style="flex-shrink:0">{tag_html}</div>
</div>""", unsafe_allow_html=True)
        if st.button("→", key=f"bib_{tid}", help=m.get("description","")):
            _open(tid)

# ── Layout B : Cartes larges 2 colonnes ───────────────────────────────────────
elif layout == "cartes":
    rows = [filtered[i:i+2] for i in range(0, len(filtered), 2)]
    for row in rows:
        cols = st.columns(2)
        for j, (tid, cls) in enumerate(row):
            m = cls.meta()
            tags = m.get("tags",[])[:3]
            desc = m.get("description","")[:70] + ("…" if len(m.get("description",""))>70 else "")
            ico_bg = _ICO_BG[(list(tests_map.keys()).index(tid)) % len(_ICO_BG)]
            tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
            with cols[j]:
                st.markdown(f"""<div class="card-b">
  <div class="card-b-head">
    <div class="card-b-ico" style="background:{ico_bg}">{cls.tab_label().split()[0]}</div>
    <div><div class="card-b-title">{" ".join(cls.tab_label().split()[1:])}</div>
    <div class="card-b-desc">{desc}</div></div>
  </div>
  <div class="card-b-foot">{tag_html}</div>
</div>""", unsafe_allow_html=True)
                if st.button("Ouvrir", key=f"bib_{tid}", use_container_width=True):
                    _open(tid)

# ── Layout C : Tuiles icône 4 colonnes ────────────────────────────────────────
elif layout == "tuiles":
    rows = [filtered[i:i+4] for i in range(0, len(filtered), 4)]
    for row in rows:
        cols = st.columns(4)
        for j, (tid, cls) in enumerate(row):
            m = cls.meta()
            tags_str = " · ".join(m.get("tags",[])[:2])
            ico = cls.tab_label().split()[0]
            title = " ".join(cls.tab_label().split()[1:])
            with cols[j]:
                st.markdown(f"""<div class="tile">
  <div class="tile-ico">{ico}</div>
  <div class="tile-title">{title}</div>
  <div class="tile-cat">{tags_str}</div>
</div>""", unsafe_allow_html=True)
                if st.button(" ", key=f"bib_{tid}", use_container_width=True,
                             help=m.get("description","")):
                    _open(tid)

# ── Layout D : Table enrichie ─────────────────────────────────────────────────
elif layout == "table":
    from utils.pdf import QUESTIONNAIRES
    st.markdown('<table class="rich-table"><thead><tr>'
        '<th>Test</th><th>Description</th><th>Tags</th><th>Fiche PDF</th>'
        '</tr></thead><tbody>', unsafe_allow_html=True)
    for tid, cls in filtered:
        m = cls.meta()
        tags = "".join(f'<span class="tag">{t}</span>' for t in m.get("tags",[])[:3])
        qk = _TEST_TO_Q.get(tid)
        pdf_badge = ('<span class="pill-green">✓ dispo</span>' if qk and qk in QUESTIONNAIRES
                     else '<span class="pill-none">—</span>')
        desc = m.get("description","")[:60] + ("…" if len(m.get("description",""))>60 else "")
        st.markdown(f"""<tr><td><strong>{cls.tab_label()}</strong></td>
<td style="color:var(--color-text-secondary);font-size:12px">{desc}</td>
<td>{tags}</td><td>{pdf_badge}</td></tr>""", unsafe_allow_html=True)
    st.markdown('</tbody></table>', unsafe_allow_html=True)
    st.markdown("")
    st.caption("Cliquez sur un test pour l'ouvrir :")
    sel_name = st.selectbox("Sélectionner un test",
        options=[tid for tid, _ in filtered],
        format_func=lambda tid: tests_map[tid].tab_label() if tid in tests_map else tid,
        label_visibility="collapsed")
    if st.button("Ouvrir →", type="primary"):
        _open(sel_name)
