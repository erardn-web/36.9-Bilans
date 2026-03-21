import streamlit as st
from datetime import date
import pandas as pd

from utils.db import (
    get_all_patients, create_patient,
    get_patient_bilans_equilibre, save_bilan_equilibre, delete_bilan_equilibre,
)
from utils.equilibre_data import (
    TINETTI_EQUILIBRE, TINETTI_MARCHE, TINETTI_EQ_KEYS, TINETTI_MA_KEYS,
    compute_tinetti, TINETTI_EQ_MAX, TINETTI_MA_MAX,
    BERG_ITEMS, BERG_KEYS, compute_berg,
    SPPB_BALANCE_OPTS, SPPB_WALK_OPTS, SPPB_CHAIR_OPTS, compute_sppb,
)

st.set_page_config(page_title="Bilan Équilibre", page_icon="🧘", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.page-title{font-size:1.8rem;font-weight:700;color:#2B57A7;margin-bottom:.2rem;}
.patient-badge{background:#E8EEF9;border-left:4px solid #2B57A7;
    padding:.5rem 1rem;border-radius:6px;font-weight:600;margin-bottom:1rem;}
.section-title{font-size:1.1rem;font-weight:700;color:#C4603A;
    border-bottom:2px solid #C4603A;padding-bottom:.3rem;margin-bottom:.8rem;}
.score-box{background:#2B57A7;color:white;padding:.6rem 1rem;
    border-radius:8px;font-weight:600;margin:.5rem 0;}
.info-box{background:#E8EEF9;border-left:3px solid #2B57A7;
    padding:.5rem .8rem;border-radius:4px;font-size:.9rem;margin:.3rem 0;}
</style>
""", unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "eq_mode": "accueil", "eq_patient_id": None, "eq_patient_info": None,
    "eq_bilan_id": None, "eq_bilan_data": {}, "eq_unsaved": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Helpers ──────────────────────────────────────────────────────────────────
def lv(key, default=None):
    v = st.session_state.eq_bilan_data.get(key)
    return default if (v is None or str(v).strip() in ("","None")) else v

def lv_int(key, default=0):
    try: return int(float(lv(key, default)))
    except: return default

def lv_float(key, default=0.0):
    try: return float(lv(key, default))
    except: return default

def lv_float_or_none(key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try:
        r = float(v); return r if r != 0.0 else None
    except: return None

def lv_int_or_none(key):
    v = lv(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try:
        r = int(float(v)); return r if r != 0 else None
    except: return None

# ═══════════════════════════════════════════════════════════════════════════════
#  ACCUEIL
# ═══════════════════════════════════════════════════════════════════════════════
def render_accueil():
    st.markdown('<div class="page-title">🧘 Bilan Équilibre — Gériatrie</div>',
                unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🔍 Rechercher un patient")
        patients_df = get_all_patients()
        if patients_df.empty:
            st.info("Aucun patient enregistré.")
        else:
            search = st.text_input("Nom ou prénom…", key="eq_search")
            filtered = patients_df
            if search:
                mask = (patients_df["nom"].str.contains(search.upper(), na=False) |
                        patients_df["prenom"].str.contains(search.capitalize(), na=False))
                filtered = patients_df[mask]
            if filtered.empty:
                st.warning("Aucun résultat.")
            else:
                for _, row in filtered.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(
                            f"**{row['nom']} {row['prenom']}** | "
                            f"{row.get('date_naissance','—')} — `{row['patient_id']}`")
                    with c2:
                        if st.button("Sélectionner", key=f"eqsel_{row['patient_id']}"):
                            st.session_state.eq_patient_id   = row["patient_id"]
                            st.session_state.eq_patient_info = row.to_dict()
                            st.session_state.eq_mode         = "bilan"
                            st.rerun()
    with col_b:
        st.markdown("#### ➕ Nouveau patient")
        with st.form("eq_new_pat", clear_on_submit=True):
            nom    = st.text_input("Nom *")
            prenom = st.text_input("Prénom *")
            ddn    = st.date_input("Date de naissance *",
                                   min_value=date(1900,1,1), max_value=date.today())
            sexe   = st.selectbox("Sexe", ["Féminin","Masculin","Autre"])
            sub    = st.form_submit_button("Créer", type="primary")
        if sub:
            if not nom or not prenom:
                st.error("Nom et prénom obligatoires.")
            else:
                pid = create_patient(nom, prenom, ddn, sexe, "")
                df2 = get_all_patients()
                row = df2[df2["patient_id"]==pid].iloc[0]
                st.session_state.eq_patient_id   = pid
                st.session_state.eq_patient_info = row.to_dict()
                st.session_state.eq_mode         = "bilan"
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  SÉLECTION BILAN
# ═══════════════════════════════════════════════════════════════════════════════
def render_bilan_selection():
    info      = st.session_state.eq_patient_info
    bilans_df = get_patient_bilans_equilibre(st.session_state.eq_patient_id)

    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— {info.get("date_naissance","—")} — ID : {info["patient_id"]}</div>',
        unsafe_allow_html=True)

    sel_ids = st.session_state.get("eq_selected_ids", None)
    if sel_ids is None or not bilans_df.empty:
        sel_ids = list(bilans_df["bilan_id"]) if not bilans_df.empty else []
        st.session_state["eq_selected_ids"] = sel_ids

    def get_sel(df):
        sel = st.session_state.get("eq_selected_ids", [])
        f = df[df["bilan_id"].isin(sel)] if sel else df
        return f if not f.empty else df

    col_back, col_evol, col_pdf, _ = st.columns([1, 1, 1.2, 3])
    with col_back:
        if st.button("⬅️ Changer de patient"):
            for k in ["eq_patient_id","eq_patient_info","eq_bilan_id"]:
                st.session_state[k] = None
            st.session_state.eq_bilan_data = {}
            st.session_state.pop("eq_selected_ids", None)
            st.session_state.eq_mode = "accueil"
            st.rerun()
    with col_evol:
        if not bilans_df.empty:
            if st.button("📈 Évolution", type="primary"):
                st.session_state.eq_mode = "evolution"
                st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            from utils.equilibre_pdf import generate_pdf_equilibre
            sel_df = get_sel(bilans_df)
            with st.spinner("PDF…"):
                pdf = generate_pdf_equilibre(sel_df, info)
            st.download_button(
                f"📄 Exporter PDF ({len(sel_df)})",
                data=pdf,
                file_name=f"equilibre_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf")

    st.markdown("---")
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### 📋 Bilans existants")
        if bilans_df.empty:
            st.info("Aucun bilan pour ce patient.")
        else:
            st.markdown("<small style='color:#888'>Cochez les bilans à inclure dans l'évolution</small>",
                        unsafe_allow_html=True)
            new_sel = []
            for _, row in bilans_df.iterrows():
                bid = row["bilan_id"]
                c_ck, c_info, c_open, c_del = st.columns([0.5, 3.5, 0.8, 0.8])
                with c_ck:
                    if st.checkbox("", value=bid in sel_ids, key=f"eqck_{bid}",
                                   label_visibility="collapsed"):
                        new_sel.append(bid)
                with c_info:
                    st.markdown(
                        f"**{row.get('date_bilan','—')}** — {row.get('type_bilan','—')}"
                        f"  \n<small>`{bid}`</small>", unsafe_allow_html=True)
                with c_open:
                    if st.button("✏️", key=f"eqopen_{bid}", help="Ouvrir"):
                        st.session_state.eq_bilan_id   = bid
                        st.session_state.eq_bilan_data = row.to_dict()
                        st.session_state.eq_mode       = "formulaire"
                        st.session_state.eq_unsaved    = False
                        st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"eqdel_{bid}", help="Supprimer"):
                        st.session_state[f"eq_confirm_del_{bid}"] = True
                if st.session_state.get(f"eq_confirm_del_{bid}", False):
                    st.warning(f"⚠️ Supprimer définitivement ce bilan ?")
                    ca, cb, _ = st.columns([1,1,3])
                    with ca:
                        if st.button("✅ Confirmer", key=f"eqdelok_{bid}", type="primary"):
                            delete_bilan_equilibre(bid)
                            st.session_state.pop(f"eq_confirm_del_{bid}", None)
                            st.session_state["eq_selected_ids"] = [i for i in sel_ids if i != bid]
                            st.rerun()
                    with cb:
                        if st.button("✖ Annuler", key=f"eqdelcancel_{bid}"):
                            st.session_state.pop(f"eq_confirm_del_{bid}", None)
                            st.rerun()
            st.session_state["eq_selected_ids"] = new_sel

    with col_right:
        st.markdown("#### ➕ Nouveau bilan")
        with st.form("eq_new_bilan"):
            bilan_date = st.date_input("Date", value=date.today())
            bilan_type = st.selectbox("Type", ["Bilan initial","Bilan intermédiaire","Bilan final"])
            praticien  = st.text_input("Praticien")
            go = st.form_submit_button("Créer", type="primary")
        if go:
            st.session_state.eq_bilan_id   = None
            st.session_state.eq_bilan_data = {
                "patient_id": st.session_state.eq_patient_id,
                "date_bilan": str(bilan_date),
                "type_bilan": bilan_type,
                "praticien": praticien,
            }
            st.session_state.eq_mode    = "formulaire"
            st.session_state.eq_unsaved = True
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  FORMULAIRE BILAN
# ═══════════════════════════════════════════════════════════════════════════════
def render_formulaire():
    info = st.session_state.eq_patient_info
    bd   = st.session_state.eq_bilan_data
    st.markdown(
        f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} '
        f'— {bd.get("type_bilan","—")} du {bd.get("date_bilan","—")}</div>',
        unsafe_allow_html=True)

    col_back, col_save, _ = st.columns([1,1,4])
    with col_back:
        if st.button("⬅️ Retour"):
            if not st.session_state.get("eq_just_saved", False):
                st.session_state["eq_confirm_back"] = True
            else:
                st.session_state.pop("eq_just_saved", None)
                st.session_state.eq_mode = "bilan"
                st.rerun()
    with col_save:
        save_top = st.button("💾 Sauvegarder", type="primary")

    if st.session_state.get("eq_confirm_back", False):
        st.warning("⚠️ **Modifications non sauvegardées.** Quitter sans sauvegarder ?")
        ca, cb, _ = st.columns([1.5, 1.5, 4])
        with ca:
            if st.button("✅ Quitter", type="primary", key="eq_back_ok"):
                st.session_state["eq_confirm_back"] = False
                st.session_state.eq_mode = "bilan"
                st.rerun()
        with cb:
            if st.button("✖ Continuer", key="eq_back_cancel"):
                st.session_state["eq_confirm_back"] = False
                st.rerun()

    st.markdown("---")
    collected = {}

    tab_gen, tab_tinetti, tab_sts, tab_unip, tab_tug, tab_berg, tab_sppb = st.tabs([
        "📝 Général", "🧍 Tinetti", "🪑 STS 1 min",
        "🦵 Unipodal", "⏱️ TUG", "⚖️ Berg", "📊 SPPB",
    ])

    # ── GÉNÉRAL ───────────────────────────────────────────────────────────────
    with tab_gen:
        st.markdown('<div class="section-title">Informations générales</div>',
                    unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            bilan_date = st.date_input("Date du bilan", value=pd.to_datetime(lv("date_bilan", str(date.today()))))
            bilan_type = st.selectbox("Type", ["Bilan initial","Bilan intermédiaire","Bilan final"],
                index=["Bilan initial","Bilan intermédiaire","Bilan final"].index(
                    lv("type_bilan","Bilan initial")) if lv("type_bilan") else 0)
        with g2:
            praticien = st.text_input("Praticien", value=lv("praticien",""))
            notes = st.text_area("Notes générales", value=lv("notes_generales",""), height=80)
        collected.update({"date_bilan": str(bilan_date), "type_bilan": bilan_type,
                          "praticien": praticien, "notes_generales": notes})

    # ── TINETTI ───────────────────────────────────────────────────────────────
    with tab_tinetti:
        st.markdown('<div class="section-title">Tinetti — POMA</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Évaluation de l\'équilibre et de la marche. '
                    'Seuil de risque de chute : < 24/28</div>', unsafe_allow_html=True)

        tin_answers = {}
        st.markdown("**Partie A — Équilibre (0–16)**")
        for key, label, options in TINETTI_EQUILIBRE:
            stored = lv(key, "")
            opts_ext = ["— Non évalué —"] + [f"{s} — {d}" for s,d in options]
            stored_idx = 0
            if stored != "":
                try:
                    s_int = int(float(stored))
                    stored_idx = next((i+1 for i,(s,_) in enumerate(options) if s==s_int), 0)
                except: pass
            chosen = st.radio(label, opts_ext, index=stored_idx, key=f"tin_{key}", horizontal=False)
            if chosen != "— Non évalué —":
                score = int(chosen.split(" — ")[0])
                tin_answers[key] = score
                collected[key]   = score
            else:
                collected[key] = ""

        st.markdown("---")
        st.markdown("**Partie B — Marche (0–12)**")
        for key, label, options in TINETTI_MARCHE:
            stored = lv(key, "")
            opts_ext = ["— Non évalué —"] + [f"{s} — {d}" for s,d in options]
            stored_idx = 0
            if stored != "":
                try:
                    s_int = int(float(stored))
                    stored_idx = next((i+1 for i,(s,_) in enumerate(options) if s==s_int), 0)
                except: pass
            chosen = st.radio(label, opts_ext, index=stored_idx, key=f"tin_{key}", horizontal=False)
            if chosen != "— Non évalué —":
                score = int(chosen.split(" — ")[0])
                tin_answers[key] = score
                collected[key]   = score
            else:
                collected[key] = ""

        result = compute_tinetti(tin_answers)
        if result["total"] is not None:
            st.markdown("---")
            eq_s = f"{result['eq']}/{TINETTI_EQ_MAX}" if result['eq'] is not None else "—"
            ma_s = f"{result['ma']}/{TINETTI_MA_MAX}" if result['ma'] is not None else "—"
            st.markdown(
                f'<div class="score-box" style="background:{result["color"]};">'
                f'Tinetti : {result["total"]}/28 — {result["interpretation"]}'
                f'  <small>(Équilibre : {eq_s} · Marche : {ma_s})</small></div>',
                unsafe_allow_html=True)
        collected.update({
            "tinetti_eq_score": result["eq"] if result["eq"] is not None else "",
            "tinetti_ma_score": result["ma"] if result["ma"] is not None else "",
            "tinetti_total": result["total"] if result["total"] is not None else "",
            "tinetti_interpretation": result["interpretation"],
        })

    # ── STS 1 MIN ─────────────────────────────────────────────────────────────
    with tab_sts:
        st.markdown('<div class="section-title">STS — Sit to Stand 1 minute</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">Compter le nombre de levers complets en 1 minute '
                    'depuis une chaise standard sans appui-bras.</div>', unsafe_allow_html=True)
        sts_reps = st.number_input("Nombre de répétitions / minute",
                                   min_value=0, max_value=60, step=1,
                                   value=lv_int_or_none("sts_1min_reps"),
                                   help="0 = non réalisé")
        sts_interp = ""
        if sts_reps and sts_reps > 0:
            # Normes approximatives par tranche d'âge (à affiner selon population)
            if sts_reps >= 14: sts_color, sts_interp = "#388e3c", "Bonne capacité fonctionnelle (≥ 14)"
            elif sts_reps >= 10: sts_color, sts_interp = "#f57c00", "Capacité modérée (10–13)"
            else: sts_color, sts_interp = "#d32f2f", "Capacité limitée (< 10)"
            st.markdown(f'<div class="score-box" style="background:{sts_color};">'
                        f'{sts_reps} rép/min — {sts_interp}</div>', unsafe_allow_html=True)
        collected.update({"sts_1min_reps": sts_reps or "", "sts_1min_interpretation": sts_interp})

    # ── UNIPODAL ──────────────────────────────────────────────────────────────
    with tab_unip:
        st.markdown('<div class="section-title">Équilibre unipodal (secondes)</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">Temps de maintien sur un pied (max 30 sec). '
                    'Seuil : < 5 sec = risque de chute élevé.</div>', unsafe_allow_html=True)
        u1, u2 = st.columns(2)
        with u1:
            st.markdown("**Yeux ouverts**")
            u_do = st.number_input("Côté droit (sec)", 0.0, 30.0,
                                   lv_float_or_none("unipodal_d_ouvert"), 0.5, key="ueq_do",
                                   help="0 = non mesuré")
            u_go = st.number_input("Côté gauche (sec)", 0.0, 30.0,
                                   lv_float_or_none("unipodal_g_ouvert"), 0.5, key="ueq_go",
                                   help="0 = non mesuré")
        with u2:
            st.markdown("**Yeux fermés**")
            u_df = st.number_input("Côté droit (sec)", 0.0, 30.0,
                                   lv_float_or_none("unipodal_d_ferme"), 0.5, key="ueq_df",
                                   help="0 = non mesuré")
            u_gf = st.number_input("Côté gauche (sec)", 0.0, 30.0,
                                   lv_float_or_none("unipodal_g_ferme"), 0.5, key="ueq_gf",
                                   help="0 = non mesuré")
        for val, label in [(u_do,"D ouvert"),(u_go,"G ouvert"),(u_df,"D fermé"),(u_gf,"G fermé")]:
            if val is not None and val > 0:
                color = "#388e3c" if val >= 10 else "#f57c00" if val >= 5 else "#d32f2f"
                st.markdown(f'<small style="color:{color}">● {label} : {val}s</small>',
                            unsafe_allow_html=True)
        collected.update({"unipodal_d_ouvert": u_do or "", "unipodal_g_ouvert": u_go or "",
                          "unipodal_d_ferme": u_df or "", "unipodal_g_ferme": u_gf or ""})

    # ── TUG ───────────────────────────────────────────────────────────────────
    with tab_tug:
        st.markdown('<div class="section-title">TUG — Timed Up and Go</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">Lever, marcher 3 m, demi-tour, revenir, s\'asseoir. '
                    'Normal < 12 sec chez l\'adulte âgé. < 20 sec = indépendant.</div>',
                    unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            tug_temps = st.number_input("Temps (secondes)", 0.0, 120.0,
                                        lv_float_or_none("tug_temps"), 0.1, key="tug_t",
                                        help="0 = non mesuré")
        with t2:
            tug_aide = st.selectbox("Aide technique",
                                    ["— Non renseigné —","Aucune","Canne","Déambulateur","Autre"],
                                    index=["— Non renseigné —","Aucune","Canne","Déambulateur","Autre"].index(
                                        lv("tug_aide","— Non renseigné —"))
                                    if lv("tug_aide","") in ["Aucune","Canne","Déambulateur","Autre","— Non renseigné —"] else 0)
        tug_interp = ""
        if tug_temps and tug_temps > 0:
            if tug_temps < 10:   tc, tug_interp = "#388e3c", "Mobilité normale (< 10 sec)"
            elif tug_temps < 12: tc, tug_interp = "#8bc34a", "Bon score (10–11 sec)"
            elif tug_temps < 20: tc, tug_interp = "#f57c00", "Risque modéré (12–19 sec)"
            else:                tc, tug_interp = "#d32f2f", "Risque élevé de chute (≥ 20 sec)"
            st.markdown(f'<div class="score-box" style="background:{tc};">'
                        f'TUG : {tug_temps} sec — {tug_interp}</div>', unsafe_allow_html=True)
        collected.update({
            "tug_temps": tug_temps or "",
            "tug_aide": "" if tug_aide == "— Non renseigné —" else tug_aide,
            "tug_interpretation": tug_interp,
        })

    # ── BERG ──────────────────────────────────────────────────────────────────
    with tab_berg:
        st.markdown('<div class="section-title">Berg Balance Scale (0–56)</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="info-box">14 items cotés 0–4. '
                    'Seuils : ≤ 20 = risque élevé · 21–40 = risque modéré · ≥ 41 = faible</div>',
                    unsafe_allow_html=True)
        berg_answers = {}
        for key, label, options in BERG_ITEMS:
            stored = lv(key, "")
            opts_ext = ["— Non évalué —"] + [f"{s} — {d}" for s,d in options]
            stored_idx = 0
            if stored != "":
                try:
                    s_int = int(float(stored))
                    stored_idx = next((i+1 for i,(s,_) in enumerate(options) if s==s_int), 0)
                except: pass
            chosen = st.radio(label, opts_ext, index=stored_idx, key=f"berg_{key}", horizontal=False)
            if chosen != "— Non évalué —":
                score = int(chosen.split(" — ")[0])
                berg_answers[key] = score
                collected[key]    = score
            else:
                collected[key] = ""
        berg_r = compute_berg(berg_answers)
        if berg_r["score"] is not None:
            st.markdown("---")
            st.markdown(
                f'<div class="score-box" style="background:{berg_r["color"]};">'
                f'Berg : {berg_r["score"]}/56 — {berg_r["interpretation"]}</div>',
                unsafe_allow_html=True)
        collected.update({
            "berg_score": berg_r["score"] if berg_r["score"] is not None else "",
            "berg_interpretation": berg_r["interpretation"],
        })

    # ── SPPB ──────────────────────────────────────────────────────────────────
    with tab_sppb:
        st.markdown('<div class="section-title">SPPB — Short Physical Performance Battery (0–12)</div>',
                    unsafe_allow_html=True)

        def _sppb_radio(label, opts, key):
            stored = lv(key, "")
            ext = ["— Non évalué —"] + [f"{s} — {d}" for s,d in opts]
            idx = 0
            if stored != "":
                try:
                    sv = int(float(stored))
                    idx = next((i+1 for i,(s,_) in enumerate(opts) if s==sv), 0)
                except: pass
            chosen = st.radio(label, ext, index=idx, key=f"sppb_{key}", horizontal=False)
            if chosen == "— Non évalué —":
                collected[key] = ""; return None
            else:
                score = int(chosen.split(" — ")[0])
                collected[key] = score; return score

        st.markdown("**1. Équilibre statique**")
        bal = _sppb_radio("Score équilibre", SPPB_BALANCE_OPTS, "sppb_balance")
        st.markdown("---")
        st.markdown("**2. Vitesse de marche (4 mètres)**")
        walk_t = st.number_input("Temps de marche (sec)", 0.0, 60.0,
                                  lv_float_or_none("sppb_walk_time"), 0.1, key="sppb_walk_t",
                                  help="0 = non mesuré")
        walk_s = _sppb_radio("Score vitesse de marche", SPPB_WALK_OPTS, "sppb_walk_score")
        collected["sppb_walk_time"] = walk_t or ""
        st.markdown("---")
        st.markdown("**3. Lever de chaise (5 répétitions)**")
        chair_t = st.number_input("Temps pour 5 levers (sec)", 0.0, 60.0,
                                   lv_float_or_none("sppb_chair_time"), 0.1, key="sppb_chair_t",
                                   help="0 = non mesuré")
        chair_s = _sppb_radio("Score lever de chaise", SPPB_CHAIR_OPTS, "sppb_chair_score")
        collected["sppb_chair_time"] = chair_t or ""

        sppb_r = compute_sppb(bal, walk_s, chair_s)
        if sppb_r["score"] is not None:
            st.markdown("---")
            st.markdown(
                f'<div class="score-box" style="background:{sppb_r["color"]};">'
                f'SPPB : {sppb_r["score"]}/12 — {sppb_r["interpretation"]}</div>',
                unsafe_allow_html=True)
        collected.update({
            "sppb_score": sppb_r["score"] if sppb_r["score"] is not None else "",
            "sppb_interpretation": sppb_r["interpretation"],
        })

    # ── SAUVEGARDE ────────────────────────────────────────────────────────────
    if save_top or st.button("💾 Sauvegarder le bilan", type="primary", key="eq_save_bot"):
        final = {**st.session_state.eq_bilan_data, **collected,
                 "patient_id": st.session_state.eq_patient_id}
        if st.session_state.eq_bilan_id:
            final["bilan_id"] = st.session_state.eq_bilan_id
        with st.spinner("Enregistrement…"):
            new_id = save_bilan_equilibre(final)
        st.session_state.eq_bilan_id   = new_id
        final["bilan_id"]              = new_id
        st.session_state.eq_bilan_data = final
        st.session_state.eq_just_saved = True
        st.session_state.eq_unsaved    = False
        st.success(f"✅ Bilan sauvegardé ! (ID : {new_id})")
        st.balloons()

# ═══════════════════════════════════════════════════════════════════════════════
#  ÉVOLUTION
# ═══════════════════════════════════════════════════════════════════════════════
def render_evolution():
    info      = st.session_state.eq_patient_info
    all_df    = get_patient_bilans_equilibre(st.session_state.eq_patient_id)
    sel       = st.session_state.get("eq_selected_ids", None)
    bilans_df = all_df[all_df["bilan_id"].isin(sel)] if sel else all_df
    if bilans_df.empty: bilans_df = all_df

    st.markdown(f'<div class="patient-badge">👤 {info["nom"]} {info["prenom"]} — Évolution Équilibre</div>',
                unsafe_allow_html=True)
    n_sel, n_tot = len(bilans_df), len(all_df)
    if n_sel < n_tot:
        st.info(f"ℹ️ Affichage de {n_sel}/{n_tot} bilans sélectionnés.")

    col_back, col_pdf, _ = st.columns([1, 1.5, 4])
    with col_back:
        if st.button("⬅️ Retour"):
            st.session_state.eq_mode = "bilan"
            st.rerun()
    with col_pdf:
        if not bilans_df.empty:
            from utils.equilibre_pdf import generate_pdf_equilibre
            with st.spinner("PDF…"):
                pdf = generate_pdf_equilibre(bilans_df, info)
            st.download_button(
                f"📄 Exporter PDF ({n_sel})",
                data=pdf,
                file_name=f"evolution_equilibre_{info['nom']}_{info['prenom']}_{date.today()}.pdf",
                mime="application/pdf", type="primary")
    st.markdown("---")

    if bilans_df.empty:
        st.info("Aucun bilan disponible."); return

    bilans_df = bilans_df.copy()
    bilans_df["date_bilan"] = pd.to_datetime(bilans_df["date_bilan"], errors="coerce")
    bilans_df = bilans_df.sort_values("date_bilan").reset_index(drop=True)
    labels = [f"{r['date_bilan'].strftime('%d/%m/%y')} – {r.get('type_bilan','')}"
              for _, r in bilans_df.iterrows()]

    def safe_n(v):
        try: r=float(v); return r if r!=0 else None
        except: return None

    import plotly.graph_objects as go
    tab_scores, tab_detail = st.tabs(["📊 Scores", "📋 Détail"])

    with tab_scores:
        # Graphique scores principaux
        scores_data = {
            "Tinetti /28": [safe_n(r.get("tinetti_total")) for _, r in bilans_df.iterrows()],
            "Berg /56": [safe_n(r.get("berg_score")) for _, r in bilans_df.iterrows()],
            "SPPB /12": [safe_n(r.get("sppb_score")) for _, r in bilans_df.iterrows()],
            "TUG (sec)": [safe_n(r.get("tug_temps")) for _, r in bilans_df.iterrows()],
            "STS 1min": [safe_n(r.get("sts_1min_reps")) for _, r in bilans_df.iterrows()],
        }
        colors = ["#2B57A7","#C4603A","#388e3c","#f57c00","#7b1fa2"]
        fig = go.Figure()
        for (name, vals), color in zip(scores_data.items(), colors):
            xp = [labels[i] for i,v in enumerate(vals) if v is not None]
            yp = [v for v in vals if v is not None]
            if xp:
                fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines+markers+text",
                    name=name, line=dict(color=color, width=2.5),
                    marker=dict(size=9), text=[str(int(v)) for v in yp],
                    textposition="top center"))
        fig.update_layout(height=400, legend=dict(orientation="h", y=-0.2),
                          xaxis_title="Bilan", yaxis_title="Score",
                          plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

        # Tableau synthèse
        synth = {"Bilan": labels}
        for name, vals in scores_data.items():
            synth[name] = [str(int(v)) if v is not None else "—" for v in vals]
        synth["TUG aide"] = [r.get("tug_aide","—") or "—" for _, r in bilans_df.iterrows()]
        st.dataframe(pd.DataFrame(synth), use_container_width=True, hide_index=True)

    with tab_detail:
        for i, (_, row) in enumerate(bilans_df.iterrows()):
            with st.expander(f"Bilan {i+1} — {labels[i]}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Tinetti", f"{row.get('tinetti_total','—')}/28")
                    st.metric("TUG", f"{row.get('tug_temps','—')} sec")
                with c2:
                    st.metric("Berg", f"{row.get('berg_score','—')}/56")
                    st.metric("STS 1min", f"{row.get('sts_1min_reps','—')} rép")
                with c3:
                    st.metric("SPPB", f"{row.get('sppb_score','—')}/12")
                if row.get("notes_generales"):
                    st.markdown(f"*{row['notes_generales']}*")

# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
mode = st.session_state.eq_mode
if mode == "accueil":       render_accueil()
elif mode == "bilan":       render_bilan_selection()
elif mode == "formulaire":  render_formulaire()
elif mode == "evolution":   render_evolution()
