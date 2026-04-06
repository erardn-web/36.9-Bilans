"""pages/3_Bibliotheque.py — Bibliothèque des tests cliniques"""
import streamlit as st
import os

st.set_page_config(page_title="Bibliothèque — 36.9 Bilans",
                   page_icon="📚", layout="wide")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Chargement de tous les tests ──────────────────────────────────────────────
@st.cache_resource
def _load_all():
    import importlib
    modules = [
        "templates.shv","templates.equilibre","templates.bpco","templates.lombalgie",
        "templates.neutre","templates.epaule_douloureuse","templates.cervicalgie",
        "templates.genou","templates.hanche","templates.membre_superieur",
        "tests.psfs","tests.groc","tests.eq5d",
        "tests.ndi","tests.koos","tests.hoos",
        "tests.lysholm","tests.dash","tests.lefs",
        "tests.womac","tests.spadi","tests.constant_murley",
        "tests.prtee","tests.bctq","tests.roland_morris",
        "tests.start_back","tests.fabq","tests.dn4",
        "tests.faos","tests.kujala","tests.acl_rsi",
        "tests.hagos","tests.ikdc","tests.csi",
        "tests.qbpds","tests.atrs","tests.wosi",
        "tests.visa_a","tests.visa_p","tests.visa_h",
        "tests.visa_g","tests.cait","tests.tegner",
        "tests.dhi","tests.hit6","tests.nrs",
        "tests.borg_rpe","tests.sgrq","tests.lcadl",
        "tests.pcfs","tests.psqi","tests.abc_scale",
        "tests.mini_bestest","tests.fes_i","tests.barthel",
        "tests.ten_mwt","tests.ashworth","tests.iciq_ui",
        "tests.pfdi20","tests.pcs","tests.phq9",
        "tests.gad7","tests.isi","tests.haq",
        "tests.basdai","tests.frailty_scale","tests.frail_scale",
        "tests.gait_speed","tests.k_ses","tests.prwe",
        "tests.bpi",
    ]
    for m in modules:
        try: importlib.import_module(m)
        except Exception: pass
    return True

_load_all()

from core.registry import all_tests
from utils.search  import search_items
from utils.db      import get_all_validations

tests_map    = all_tests()
_validations = get_all_validations()

FIXED_PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fiches")

def _has_fixed_pdf(tid, m=None):
    if m and m.get("has_fixed_pdf"): return True
    return os.path.exists(os.path.join(FIXED_PDF_DIR, f"{tid}.pdf"))

# ── Styles ────────────────────────────────────────────────────────────────────
_ACCENT = ["#378ADD","#1D9E75","#D85A30","#7F77DD","#EF9F27","#D4537E"]
_VAL_STYLE = {
    "validé":    ("✅", "#e8f5e9", "#388e3c"),
    "en_cours":  ("🔄", "#fff8e1", "#f9a825"),
    "non_testé": ("⬜", "#f5f5f5", "#999999"),
}

st.markdown("""<style>
.bib-readonly input,.bib-readonly textarea,.bib-readonly select{pointer-events:none!important;opacity:.7}
.tag{font-size:11px;padding:2px 8px;border-radius:20px;
     background:var(--color-background-secondary);
     border:0.5px solid var(--color-border-tertiary);
     color:var(--color-text-secondary);display:inline-block;margin:1px 2px}
.list-item{display:flex;align-items:center;gap:12px;padding:10px 14px;
           border:0.5px solid var(--color-border-tertiary);border-radius:10px;
           margin-bottom:6px;background:var(--color-background-primary)}
.list-item:hover{border-color:var(--color-border-secondary);
                 background:var(--color-background-secondary)}
.list-accent{width:4px;min-height:40px;border-radius:2px;flex-shrink:0}
.list-title{font-size:13px;font-weight:500;margin-bottom:2px}
.list-desc{font-size:12px;color:var(--color-text-secondary)}
.pill-pdf{display:inline-block;padding:1px 7px;background:#e3f2fd;
          border-radius:10px;font-size:10px;color:#1565c0;font-weight:600;margin-left:4px}
.crit-bar-wrap{background:#eee;border-radius:4px;height:6px;margin:6px 0 2px}
.crit-bar{height:6px;border-radius:4px}
</style>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**🧪 Validation**")
    _val_filter = st.selectbox("Statut",
        ["Tous","✅ Validé","🔄 En cours","⬜ Non testé"],
        key="bib_val_filter", label_visibility="collapsed")

    _counts = {"validé":0,"en_cours":0,"non_testé":0}
    for _v in _validations.values():
        _s = _v.get("statut","non_testé")
        if _s in _counts: _counts[_s] += 1
    _total = len(tests_map)
    _counts["non_testé"] = _total - _counts["validé"] - _counts["en_cours"]
    st.caption(f"✅ {_counts['validé']} · 🔄 {_counts['en_cours']} · ⬜ {_counts['non_testé']} / {_total}")

    st.markdown("---")
    # Compteurs critères
    _n_pdf = sum(1 for tid in tests_map if _has_fixed_pdf(tid, tests_map[tid].meta()))
    st.caption(f"📄 {_n_pdf} fiches PDF fixes")

# ── Vue détail ────────────────────────────────────────────────────────────────
sel_key      = "bib_selected_test"
selected_tid = st.session_state.get(sel_key)

if selected_tid and selected_tid in tests_map:
    cls = tests_map[selected_tid]
    m   = cls.meta()

    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f"## {cls.tab_label()}")
        if m.get("description"): st.caption(m["description"])
        tags_md = " ".join(f'<span class="tag">{t}</span>' for t in m.get("tags", []))
        if _has_fixed_pdf(selected_tid, m):
            tags_md += '<span class="pill-pdf">📄 Fiche PDF disponible</span>'
        if tags_md: st.markdown(tags_md, unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Statut validation (lecture seule) ───────────────────────────────────────
    st.markdown("---")
    _vdata  = _validations.get(selected_tid, {})
    _vstat  = _vdata.get("statut", "non_testé")
    _vcrit  = _vdata.get("criteres", {})
    _vi, _vbg, _vc = _VAL_STYLE.get(_vstat, _VAL_STYLE["non_testé"])
    _n_ok   = sum(_vcrit.values()) if _vcrit else 0
    _bar_col = "#388e3c" if _n_ok==4 else "#f57c00" if _n_ok>0 else "#ddd"

    st.markdown(
        f"<span style='display:inline-block;padding:3px 12px;background:{_vbg};"
        f"border-radius:12px;font-size:0.82rem;color:{_vc};font-weight:600'>"
        f"{_vi} {_vstat.replace('_',' ').capitalize()}</span>"
        f"&nbsp;<span style='font-size:11px;color:#aaa'>{_n_ok}/4 critères validés</span>",
        unsafe_allow_html=True)

    # ── Téléchargement fiche ──────────────────────────────────────────────────
    st.markdown("---")
    _fixed_path = os.path.join(FIXED_PDF_DIR, f"{selected_tid}.pdf")
    if os.path.exists(_fixed_path):
        with open(_fixed_path, "rb") as _f:
            st.download_button("📥 Télécharger la fiche PDF",
                data=_f.read(), file_name=f"fiche_{selected_tid}.pdf",
                mime="application/pdf", key=f"dl_fixed_{selected_tid}")
    else:
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

# ── Recherche + Filtres ───────────────────────────────────────────────────────
st.markdown("## 📚 Bibliothèque des tests")
s1, s2 = st.columns([3, 2])
search_q = s1.text_input("🔍 Rechercher", placeholder="ex: épaule, NDI, qualité de vie…", key="bib_search")
ai_q     = s2.text_input("🤖 Décrire le patient", placeholder="ex: patient âgé qui chute…", key="bib_ai")

if ai_q and st.session_state.get("bib_ai_prev") != ai_q:
    st.session_state["bib_ai_prev"] = ai_q
    with st.spinner("Recherche IA…"):
        try:
            import anthropic, json, re
            _catalog = [{"id":tid,"nom":cls.meta().get("nom",""),
                         "tags":cls.meta().get("tags",[]),
                         "desc":cls.meta().get("description","")}
                        for tid,cls in tests_map.items()]
            _msg = anthropic.Anthropic().messages.create(
                model="claude-haiku-4-5", max_tokens=600,
                system='Reponds UNIQUEMENT avec un JSON {"ids":[...]} avec les IDs pertinents.',
                messages=[{"role":"user","content":
                    "Catalogue: "+json.dumps(_catalog,ensure_ascii=False)+"\nDescription: "+ai_q}])
            _rx = re.search(r'\{"ids":\s*\[[^\]]*\]\}', _msg.content[0].text, re.DOTALL)
            st.session_state["bib_ai_results"] = json.loads(_rx.group()).get("ids",[]) if _rx else []
        except Exception:
            st.session_state["bib_ai_results"] = []

ai_ids    = st.session_state.get("bib_ai_results", [])
all_items = list(tests_map.items())

if search_q:
    def _key(item):
        mm = item[1].meta()
        return f"{mm.get('nom','')} {mm.get('description','')} {item[0]}", mm.get("tags",[])
    filtered = search_items(search_q, all_items, _key)
elif ai_ids:
    filtered = [(tid, tests_map[tid]) for tid in ai_ids if tid in tests_map]
    if filtered: st.caption(f"✨ {len(filtered)} suggestion(s) IA")
else:
    filtered = all_items

# Filtre validation
_val_map = {"Tous":None,"✅ Validé":"validé","🔄 En cours":"en_cours","⬜ Non testé":"non_testé"}
_val_sel = _val_map.get(_val_filter)
if _val_sel:
    filtered = [(tid,cls) for tid,cls in filtered
                if _validations.get(tid,{}).get("statut","non_testé")==_val_sel]

st.caption(f"{len(filtered)} test(s)")
st.markdown("")

def _open(tid):
    st.session_state[sel_key] = tid
    st.rerun()

# ── Vue : Liste avec accents (unique) ─────────────────────────────────────────
for i, (tid, cls) in enumerate(filtered):
    m     = cls.meta()
    tags  = m.get("tags", [])[:3]
    desc  = m.get("description","")[:90] + ("…" if len(m.get("description",""))>90 else "")
    color = _ACCENT[i % len(_ACCENT)]
    tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    _vstat   = _validations.get(tid, {}).get("statut","non_testé")
    _vcrit   = _validations.get(tid, {}).get("criteres", {})
    _vicon   = _VAL_STYLE.get(_vstat, _VAL_STYLE["non_testé"])[0]

    # Badge PDF
    _pdf_badge = ('<span class="pill-pdf">📄 PDF</span>'
                  if _has_fixed_pdf(tid, m) else "")

    # Mini barre critères (4 petits carrés)
    _crit_keys = ["contenu","pdf_vierge","valeurs_imprimees","graphique"]
    # pdf_vierge auto si fichier présent
    _crit_vals = {
        "contenu":           _vcrit.get("contenu", False),
        "pdf_vierge":        _has_fixed_pdf(tid, m) or _vcrit.get("pdf_vierge", False),
        "valeurs_imprimees": _vcrit.get("valeurs_imprimees", False),
        "graphique":         _vcrit.get("graphique", False),
    }
    _squares = "".join(
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:2px;'
        f'background:{"#388e3c" if _crit_vals[k] else "#ddd"};margin:0 1px" '
        f'title="{k}"></span>'
        for k in _crit_keys)

    st.markdown(f"""<div class="list-item">
  <div class="list-accent" style="background:{color}"></div>
  <div style="flex:1;min-width:0">
    <div class="list-title">{cls.tab_label()}{_pdf_badge}</div>
    <div class="list-desc">{desc}</div>
    <div style="margin-top:3px">{_squares}</div>
  </div>
  <div style="flex-shrink:0;margin-right:6px;font-size:1rem" title="{_vstat}">{_vicon}</div>
  <div style="flex-shrink:0">{tag_html}</div>
</div>""", unsafe_allow_html=True)

    if st.button("→", key=f"bib_{tid}", help=m.get("description","")):
        _open(tid)
