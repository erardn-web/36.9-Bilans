import streamlit as st

st.set_page_config(
    page_title="PhysioApp",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1a3c5e;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #5a7a99;
        margin-bottom: 2rem;
    }
    .module-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px solid #e0ecf8;
        text-align: center;
        transition: border-color 0.2s;
        height: 160px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .module-card:hover { border-color: #1a3c5e; }
    .module-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .module-name { font-size: 1.1rem; font-weight: 600; color: #1a3c5e; }
    .module-sub  { font-size: 0.85rem; color: #888; margin-top: 0.2rem; }
    .coming-soon { opacity: 0.45; }
    .divider { border-top: 1px solid #e0ecf8; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🏥 PhysioApp</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Outil de bilans physiothérapeutiques – Sélectionnez un module</div>',
            unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─── Module cards ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">🫁</div>
        <div class="module-name">Bilan SHV</div>
        <div class="module-sub">Syndrome d'hyperventilation</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➡️ Accéder au bilan SHV", use_container_width=True, type="primary"):
        st.switch_page("pages/1_SHV_Bilan.py")

with col2:
    st.markdown("""
    <div class="module-card coming-soon">
        <div class="module-icon">🦴</div>
        <div class="module-name">Bilan Musculo-squelettique</div>
        <div class="module-sub">Bientôt disponible</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔒 Bientôt disponible", use_container_width=True, disabled=True, key="btn2")

with col3:
    st.markdown("""
    <div class="module-card coming-soon">
        <div class="module-icon">❤️</div>
        <div class="module-name">Bilan Cardio-respiratoire</div>
        <div class="module-sub">Bientôt disponible</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔒 Bientôt disponible", use_container_width=True, disabled=True, key="btn3")

with col4:
    st.markdown("""
    <div class="module-card coming-soon">
        <div class="module-icon">🧠</div>
        <div class="module-name">Bilan Neurologique</div>
        <div class="module-sub">Bientôt disponible</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔒 Bientôt disponible", use_container_width=True, disabled=True, key="btn4")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(
    "<small style='color:#aaa;'>PhysioApp — données stockées sur Google Sheets · "
    "Développement en cours · v0.1</small>",
    unsafe_allow_html=True,
)
