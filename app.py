"""
app.py — Tableau de bord 36.9 Bilans v2
"""
import sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
from datetime import date

st.set_page_config(
    page_title="36.9 Bilans",
    page_icon="\U0001f3e5",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Charger templates codés au démarrage
@st.cache_resource
def _load_all_templates():
    for m in ["templates.shv","templates.equilibre","templates.bpco",
              "templates.lombalgie","templates.neutre","templates.epaule_douloureuse",
              "templates.cervicalgie","templates.genou","templates.hanche",
              "templates.membre_superieur"]:
        try: __import__(m)
        except Exception: pass
    return True

_load_all_templates()

st.markdown("""<style>
.dash-metric{border:1px solid var(--color-border-tertiary);border-radius:10px;
    padding:16px 20px;background:var(--color-background-primary);text-align:center}
.dash-metric-val{font-size:2rem;font-weight:700;color:#2B57A7;line-height:1.1}
.dash-metric-lbl{font-size:0.8rem;color:var(--color-text-secondary);margin-top:2px}
.nav-card{border:1px solid var(--color-border-tertiary);border-radius:10px;padding:18px;
    background:var(--color-background-primary);text-align:center}
.nav-card-ico{font-size:1.8rem}.nav-card-lbl{font-size:0.9rem;font-weight:600;margin-top:6px}
.vote-card{border-left:4px solid #F59E0B;padding:10px 14px;border-radius:4px;
    background:var(--color-background-secondary);margin-bottom:8px}
.vote-title{font-size:0.9rem;font-weight:600}
.vote-meta{font-size:0.78rem;color:var(--color-text-secondary);margin-top:2px}
.prog-wrap{background:#eee;border-radius:6px;height:10px;margin:6px 0}
.prog-bar{height:10px;border-radius:6px}
.activity-row{padding:8px 0;border-bottom:0.5px solid var(--color-border-tertiary);font-size:0.85rem}
</style>""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    try: st.image("assets/logo_369.png", width=130)
    except Exception: st.markdown("### \U0001f3e5 36.9 Bilans")
    st.markdown("---")
    st.markdown("### \U0001f464 Thérapeute")
    therapeute = st.text_input("Votre nom",
        value=st.session_state.get("therapeute",""),
        placeholder="N. Rossier", key="therapeute_input")
    if therapeute:
        st.session_state["therapeute"] = therapeute
    st.markdown("---")
    st.caption("36.9 Bilans v2")

# Header
try: st.image("assets/logo_369.png", width=110)
except Exception: pass
st.markdown("## \U0001f3e5 36.9 Bilans")
st.caption(f"Tableau de bord · {date.today().strftime('%d/%m/%Y')}")
st.markdown("---")

# Stats
@st.cache_data(ttl=300, show_spinner=False)
def _load_stats():
    try:
        from utils.db import get_all_patients, get_audit_log_all
        import pandas as pd
        df_p = get_all_patients()
        n_patients = len(df_p)
        df_audit = get_audit_log_all(limit=500)
        if not df_audit.empty and "action" in df_audit.columns:
            n_cas    = len(df_audit[df_audit["action"]=="creation_cas"])
            n_bilans = len(df_audit[df_audit["action"]=="creation_bilan"])
            ACTIONS_UTILES = ["creation_bilan","creation_cas","save_bilan",
                              "modification_bilan","creation_patient","cloture_cas","reouverture_cas"]
            recent = df_audit[
                df_audit["action"].isin(ACTIONS_UTILES) &
                df_audit["therapeute"].fillna("").str.strip().ne("")
            ].head(8)
        else:
            n_cas = n_bilans = 0; recent = pd.DataFrame()
        return {"n_patients":n_patients,"n_cas":n_cas,"n_bilans":n_bilans,"recent":recent}
    except Exception:
        import pandas as pd
        return {"n_patients":0,"n_cas":0,"n_bilans":0,"recent":pd.DataFrame()}

@st.cache_data(ttl=300, show_spinner=False)
def _load_votes():
    try:
        from utils.db import get_sheet
        import pandas as pd
        df = get_sheet("Feedback")
        if df.empty: return []
        df = df[df["statut"]=="En vote"].copy()
        if df.empty: return []
        df["votes_pour"]   = pd.to_numeric(df.get("votes_pour",0),   errors="coerce").fillna(0).astype(int)
        df["votes_contre"] = pd.to_numeric(df.get("votes_contre",0), errors="coerce").fillna(0).astype(int)
        from datetime import datetime
        def _j(dl):
            try: return max(0,(datetime.strptime(str(dl)[:10],"%Y-%m-%d").date()-date.today()).days)
            except: return None
        df["jours"] = df.get("deadline_vote","").apply(_j)
        return df.sort_values("votes_pour",ascending=False).to_dict("records")
    except Exception: return []

stats = _load_stats()
votes = _load_votes()
is_super   = st.session_state.get("admin_level") == "super"
is_cabinet = st.session_state.get("admin_level") == "cabinet"

# 1. Métriques
st.markdown("### \U0001f4ca Activité du cabinet")
m1,m2,m3 = st.columns(3)
for col,val,lbl in [(m1,stats["n_patients"],"Patients"),(m2,stats["n_cas"],"Cas créés"),
                    (m3,stats["n_bilans"],"Bilans")]:
    col.markdown(f'<div class="dash-metric"><div class="dash-metric-val">{val}</div>'                 f'<div class="dash-metric-lbl">{lbl}</div></div>',unsafe_allow_html=True)
st.markdown("")

# 2. Validation (super admin) — chargé séparément pour ne pas bloquer le dashboard
if is_super:
    try:
        from utils.db import get_all_validations
        from core.registry import all_tests as _at
        _vals = get_all_validations()
        _n_t  = len(_at())
        _n_v  = sum(1 for v in _vals.values() if v.get("statut")=="validé")
        _n_e  = sum(1 for v in _vals.values() if v.get("statut")=="en_cours")
        _pct  = int(_n_v/_n_t*100) if _n_t else 0
        _col  = "#388e3c" if _pct==100 else "#f57c00" if _pct>=50 else "#d32f2f"
        st.markdown("### 🧪 Préparation au lancement")
        st.markdown(
            f'<div class="prog-wrap"><div class="prog-bar" style="background:{_col};width:{_pct}%"></div></div>'
            f'<span style="font-size:0.85rem;color:#666">✅ {_n_v} validés · 🔄 {_n_e} en cours · ⬜ {_n_t-_n_v-_n_e} non testés · <strong style="color:{_col}">{_pct}% prêt</strong></span>',
            unsafe_allow_html=True)
        st.markdown("---")
    except Exception:
        pass

# 3. Votes ouverts
TYPES_ICO = {"Bug":"\U0001f41b","Suggestion":"\U0001f4a1","Amélioration":"\u26a1","Bibliothèque":"\U0001f4da"}
if votes:
    st.markdown("### \U0001f4ac Votes ouverts — participez !")
    cols_v = st.columns(min(len(votes),3))
    for i,v in enumerate(votes[:6]):
        ico = TYPES_ICO.get(v.get("type",""),"\u2753")
        j   = v.get("jours")
        j_txt = f"J-{j}" if j is not None else ""
        j_col = "#d32f2f" if j is not None and j<=2 else "#f57c00" if j is not None and j<=5 else "#388e3c"
        with cols_v[i%3]:
            st.markdown(
                f'<div class="vote-card"><div class="vote-title">{ico} {v.get("titre","")}</div>'                f'<div class="vote-meta">✅ {v["votes_pour"]} / ❌ {v["votes_contre"]}'                f'&nbsp;&nbsp;<span style="color:{j_col};font-weight:600">{j_txt}</span></div>'                f'<div class="vote-meta">par {v.get("auteur","—")}</div></div>',
                unsafe_allow_html=True)
    st.caption("Voter dans la page Feedback")
    st.markdown("---")

# 4. Activité récente
if stats["recent"] is not None and not stats["recent"].empty:
    st.markdown("### \U0001f550 Activité récente")
    ACTIONS = {
        "creation_bilan":    ("📋", "Nouveau bilan"),
        "creation_cas":      ("📁", "Nouveau cas"),
        "save_bilan":        ("💾", "Bilan modifié"),
        "modification_bilan":("✏️", "Bilan modifié"),
        "creation_patient":  ("👤", "Nouveau patient"),
        "cloture_cas":       ("✅", "Cas clôturé"),
        "reouverture_cas":   ("🔄", "Cas réouvert"),
    }
    for _,row in stats["recent"].iterrows():
        action_key = str(row.get("action","")).strip()
        ico, lbl = ACTIONS.get(action_key, ("⚙️", action_key.replace("_"," ").capitalize()))
        thera = str(row.get("therapeute","")).strip() or "—"
        ts    = str(row.get("timestamp",""))[:16]
        st.markdown(
            f'<div class="activity-row">'            f'<span style="font-size:1.1rem">{ico}</span> '            f'<strong>{lbl}</strong> '            f'<span style="color:var(--color-text-secondary)"> · {thera} · {ts}</span>'            f'</div>',
            unsafe_allow_html=True)
    st.markdown("")
    st.markdown("---")


if st.button("\U0001f504 Actualiser", key="refresh"):
    _load_stats.clear(); _load_votes.clear(); st.rerun()
