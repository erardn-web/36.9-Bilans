"""pages/2_Bibliotheque.py — Bibliothèque des tests cliniques"""
import streamlit as st

st.set_page_config(page_title="Bibliothèque — 36.9 Bilans",
                   page_icon="📚", layout="wide")

@st.cache_resource
def _load_all():
    import importlib
    for m in ["templates.shv","templates.equilibre","templates.bpco",
              "templates.lombalgie","templates.neutre","templates.epaule_douloureuse"]:
        try: importlib.import_module(m)
        except Exception as e: st.warning(f"{m}: {e}")
    return True

_load_all()

from core.registry import all_tests
from utils.search import search_items

tests_map = all_tests()

st.markdown("""<style>
.bib-readonly input,.bib-readonly textarea,.bib-readonly select{pointer-events:none!important;opacity:.7}
.test-card{border:0.5px solid var(--color-border-tertiary);border-radius:12px;padding:14px 16px;
           background:var(--color-background-primary);min-height:90px}
.test-card-title{font-size:14px;font-weight:500;margin-bottom:4px}
.test-card-desc{font-size:12px;color:var(--color-text-secondary);line-height:1.4;margin-bottom:8px}
.test-tag{font-size:11px;padding:1px 8px;border-radius:20px;background:var(--color-background-secondary);
          border:0.5px solid var(--color-border-tertiary);color:var(--color-text-secondary);
          display:inline-block;margin:1px 2px}
</style>""", unsafe_allow_html=True)

sel_key = "bib_selected_test"
selected_tid = st.session_state.get(sel_key)

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
        _pdf_key = f"bib_pdf_{selected_tid}"
        if st.button("🖨️ Générer fiche PDF", type="primary"):
            with st.spinner("Génération…"):
                try: st.session_state[_pdf_key] = generate_questionnaires_pdf([_qk], {})
                except Exception as e: st.error(f"Erreur : {e}")
        if st.session_state.get(_pdf_key):
            st.download_button("📥 Télécharger", data=st.session_state[_pdf_key],
                file_name=f"fiche_{selected_tid}.pdf", mime="application/pdf",
                key=f"dl_{selected_tid}")
    st.stop()

# ── Vue grille ─────────────────────────────────────────────────────────────────
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

st.caption(f"{len(filtered)} test(s)")
st.markdown("")

cols_per_row = 4
for row_items in [filtered[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]:
    cols = st.columns(cols_per_row)
    for j, (tid, cls) in enumerate(row_items):
        m = cls.meta()
        tags = m.get("tags", [])[:3]
        desc = m.get("description", "")
        desc_short = desc[:75] + "…" if len(desc) > 75 else desc
        with cols[j]:
            st.markdown(f"""<div class="test-card">
  <div class="test-card-title">{cls.tab_label()}</div>
  <div class="test-card-desc">{desc_short}</div>
  {''.join(f'<span class="test-tag">{t}</span>' for t in tags)}
</div>""", unsafe_allow_html=True)
            if st.button("Ouvrir →", key=f"bib_{tid}", use_container_width=True):
                st.session_state[sel_key] = tid
                st.rerun()
