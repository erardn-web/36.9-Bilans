import streamlit as st
import os

st.set_page_config(
    page_title="36.9 Bilans",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ligne graphique 36.9 ──────────────────────────────────────────────────
st.markdown("""
<style>
    /* Police et fond */
    [data-testid="stAppViewContainer"] { background: #F7F7F7; }
    [data-testid="stHeader"] { background: transparent; }

    /* Header barre */
    .header-bar {
        display: flex; align-items: center; justify-content: space-between;
        background: #2B57A7;
        border-radius: 14px;
        padding: 0.6rem 1.8rem;
        margin-bottom: 2rem;
    }
    .header-bar-title {
        color: white; font-size: 1.1rem; font-weight: 600; letter-spacing: 0.04em;
    }
    .header-bar-sub { color: rgba(255,255,255,0.75); font-size: 0.85rem; }

    /* Accent terracotta */
    .accent { color: #C4603A; font-weight: 700; }

    /* Cards modules */
    .module-card {
        background: white;
        border-radius: 14px;
        padding: 1.8rem 1.2rem;
        border-top: 5px solid #2B57A7;
        text-align: center;
        height: 170px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        box-shadow: 0 2px 8px rgba(43,87,167,0.08);
        transition: box-shadow 0.2s, border-color 0.2s;
    }
    .module-card:hover {
        box-shadow: 0 6px 20px rgba(43,87,167,0.15);
        border-top-color: #C4603A;
    }
    .module-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .module-name { font-size: 1.05rem; font-weight: 700; color: #2B57A7; }
    .module-sub  { font-size: 0.8rem; color: #888; margin-top: 0.2rem; }
    .coming-soon { opacity: 0.4; border-top-color: #ccc !important; }

    /* Séparateur */
    .divider { border: none; border-top: 1px solid #E0E0E0; margin: 1.8rem 0; }

    /* Bouton primaire */
    .stButton > button[kind="primary"] {
        background: #2B57A7 !important;
        border-color: #2B57A7 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #C4603A !important;
        border-color: #C4603A !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header avec logo ─────────────────────────────────────────────────────────
LOGO = os.path.join(os.path.dirname(__file__), "assets", "logo_369.png")

col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists(LOGO):
        st.image(LOGO, width=160)
with col_title:
    st.markdown("""
        <div style="padding-top:0.4rem;">
            <div style="font-size:2rem;font-weight:700;color:#2B57A7;line-height:1.1;">
                36.9 <span style="color:#C4603A;">Bilans</span>
            </div>
            <div style="font-size:1rem;color:#666;margin-top:0.2rem;">
                Outil de bilans physiothérapeutiques
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

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
    if st.button("➡️ Accéder", use_container_width=True, key="btn1", type="primary"):
        st.switch_page("pages/1_SHV_Bilan.py")

with col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">🦴</div>
        <div class="module-name">Bilan Lombalgie</div>
        <div class="module-sub">Lombalgie chronique & aiguë</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➡️ Accéder", use_container_width=True, key="btn2", type="primary"):
        st.switch_page("pages/2_Lombalgie_Bilan.py")

with col3:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">🧘</div>
        <div class="module-name">Bilan Équilibre</div>
        <div class="module-sub">Gériatrie — Tinetti, Berg, SPPB…</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➡️ Accéder", use_container_width=True, key="btn3", type="primary"):
        st.switch_page("pages/3_Equilibre_Bilan.py")

with col4:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">🌬️</div>
        <div class="module-name">Bilan BPCO</div>
        <div class="module-sub">6MWT, CAT, BODE, spirométrie…</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➡️ Accéder", use_container_width=True, key="btn4", type="primary"):
        st.switch_page("pages/4_BPCO_Bilan.py")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── Pied de page ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#aaa; font-size:0.8rem; padding:1rem 0;">
    36.9 Bilans — Cabinet de physiothérapie
</div>
""", unsafe_allow_html=True)
