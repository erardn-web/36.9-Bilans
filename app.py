"""
app.py — Point d'entrée 36.9 Bilans v2
"""
import sys
import os
import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

st.set_page_config(
    page_title="36.9 Bilans",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Charger tous les tests et templates ───────────────────────────────────────
from core.bilan_template import BilanTemplate
from core.registry       import register_template, all_templates

@st.cache_resource
def _load_all_templates():
    """Chargé une seule fois par session — importe tous les templates."""
    import traceback
    for tmpl_name in ["templates.shv","templates.equilibre","templates.bpco","templates.lombalgie","templates.neutre","templates.epaule_douloureuse"]:
        try:
            __import__(tmpl_name)
        except Exception as e:
            st.error(f"❌ {tmpl_name} : {e}")
            st.code(traceback.format_exc())
    return True

_load_all_templates()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.module-card {
    border: 1.5px solid #e0e0e0; border-radius: 12px;
    padding: 1.2rem 1.5rem; text-align: center; background: white;
}
.module-icone { font-size: 2.5rem; margin-bottom: .4rem; }
.module-nom   { font-size: 1rem; font-weight: 600; color: #2B57A7; }
.module-desc  { font-size: .8rem; color: #888; margin-top: .3rem; }
</style>
""", unsafe_allow_html=True)

# ── Accueil ───────────────────────────────────────────────────────────────────
try:
    st.image("assets/logo_369.png", width=160)
except Exception:
    pass

st.markdown("## 36.9 Bilans")
st.markdown("**Plateforme de bilans physiothérapeutiques**")
st.markdown("---")

templates = all_templates()
if templates:
    st.markdown("### Modules disponibles")
    cols = st.columns(min(len(templates), 4))
    for i, (tid, tmpl) in enumerate(templates.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="module-card">
                <div class="module-icone">{tmpl.icone}</div>
                <div class="module-nom">{tmpl.nom}</div>
                <div class="module-desc">{len(tmpl.tests)} tests</div>
            </div>""", unsafe_allow_html=True)
else:
    st.warning("Aucun template enregistré.")

st.markdown("---")
st.caption("Sélectionnez **Bilans** dans la barre latérale pour commencer.")

with st.sidebar:
    st.markdown("### 👤 Thérapeute")
    therapeute = st.text_input("Votre nom",
        value=st.session_state.get("therapeute", ""),
        placeholder="N. Rossier", key="therapeute_input")
    if therapeute:
        st.session_state["therapeute"] = therapeute
    st.markdown("---")
    st.caption("36.9 Bilans v2")
