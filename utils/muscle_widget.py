"""
muscle_widget.py — Onglet testing musculaire réutilisable (Streamlit)
Usage : collected = render_muscle_tab(lv_fn, key_prefix, show_leg_press=True)
"""
import streamlit as st
from utils.muscle_data import (
    MUSCLE_GROUPS, MRC_SCALE, MRC_VALUES, SIDES,
    get_muscle_key, compute_muscle_score,
    compute_1rm, interpret_leg_press, LEG_PRESS_KEYS,
)


def render_muscle_tab(lv_fn, key_prefix: str, show_leg_press: bool = False,
                      leg_press_only: bool = False,
                      body_weight_key: str = None, bilan_data: dict = None) -> dict:
    """
    Affiche l'onglet testing musculaire.
    lv_fn           : fonction lv(key, default) pour charger les valeurs stockées
    key_prefix      : préfixe unique pour les widgets Streamlit (ex: "shv", "eq", "bp")
    show_leg_press  : afficher le bloc 1RM Leg Press (après le testing)
    leg_press_only  : afficher UNIQUEMENT le bloc 1RM (sans le testing musculaire)
    body_weight_key : clé pour récupérer le poids corporel (pour ratio 1RM)
    Retourne : dict avec toutes les valeurs à sauvegarder
    """
    collected = {}

    if leg_press_only:
        # N'afficher que le bloc 1RM Leg Press
        collected.update(_render_leg_press(lv_fn, key_prefix, body_weight_key, bilan_data))
        return collected

    st.markdown('<div class="section-title">Testing musculaire — Membres inférieurs</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">Testing manuel selon l\'échelle MRC (0–5). '
        'D = côté droit · G = côté gauche</div>',
        unsafe_allow_html=True)

    # En-tête du tableau
    hcol, hd, hg = st.columns([3, 1, 1])
    with hcol: st.markdown("**Groupe musculaire**")
    with hd:   st.markdown("**Droit (0–5)**")
    with hg:   st.markdown("**Gauche (0–5)**")
    st.markdown("---")

    muscle_answers = {}
    for key_sfx, label, desc in MUSCLE_GROUPS:
        col_lbl, col_d, col_g = st.columns([3, 1, 1])
        with col_lbl:
            st.markdown(f"**{label}**")
            st.markdown(f"<small style='color:#888'>{desc}</small>", unsafe_allow_html=True)

        for side, col in [("d", col_d), ("g", col_g)]:
            k = get_muscle_key(key_sfx, side)
            stored = lv_fn(k, "")
            stored_str = str(stored).strip()
            # Options : None + 0..5
            opts = [None] + MRC_VALUES
            fmt  = {None: "—", 0:"0",1:"1",2:"2",3:"3",4:"4",5:"5"}
            default = None if stored_str in ("","None") else int(float(stored_str))
            with col:
                chosen = st.select_slider(
                    label=f"{key_sfx}_{side}",
                    options=opts,
                    value=default,
                    format_func=lambda x: fmt.get(x, str(x)),
                    key=f"{key_prefix}_musc_{key_sfx}_{side}",
                    label_visibility="collapsed",
                )
            if chosen is not None:
                muscle_answers[k] = chosen
                collected[k] = chosen
            else:
                collected[k] = ""

    # Score global
    result = compute_muscle_score(muscle_answers)
    if result["mean"] is not None:
        st.markdown("---")
        st.markdown(
            f'<div class="score-box" style="background:{result["color"]};">'
            f'Moyenne MRC : {result["mean"]}/5 '
            f'<small>({result["count"]} groupes évalués · total {result["total"]}/{result["max"]})</small>'
            f'</div>',
            unsafe_allow_html=True)

    # Notes
    notes = st.text_area("Notes / observations",
                         value=lv_fn("musc_notes", ""),
                         height=70,
                         key=f"{key_prefix}_musc_notes")
    collected["musc_notes"] = notes

    # ── 1RM Leg Press (optionnel) ──────────────────────────────────────────────
    if show_leg_press:
        st.markdown("---")
        collected.update(_render_leg_press(lv_fn, key_prefix, body_weight_key, bilan_data))

    return collected



def _render_leg_press(lv_fn, key_prefix, body_weight_key=None, bilan_data=None):
    """Affiche uniquement le bloc 1RM Leg Press."""
    collected = {}
    st.markdown('<div class="section-title">1RM Leg Press (estimé)</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">Entrez la charge et le nombre de répétitions réalisées. '
        'Le 1RM est estimé via la formule de Brzycki (valide pour 1–10 répétitions) '
        'ou Epley (> 10 rép.).</div>',
        unsafe_allow_html=True)

    lp1, lp2, lp3 = st.columns(3)
    with lp1:
        lp_charge = st.number_input(
            "Charge utilisée (kg)", 0.0, 500.0,
            value=_load_float(lv_fn, "lp_charge_kg"),
            step=2.5, key=f"{key_prefix}_lp_charge",
            help="0 = non réalisé")
    with lp2:
        lp_reps = st.number_input(
            "Répétitions réalisées", 0, 30,
            value=_load_int(lv_fn, "lp_reps"),
            step=1, key=f"{key_prefix}_lp_reps",
            help="0 = non réalisé")
    with lp3:
        bw = None
        if bilan_data and body_weight_key:
            try: bw = float(bilan_data.get(body_weight_key, 0)) or None
            except: bw = None
        if bw:
            st.metric("Poids corporel", f"{bw} kg")

    lp_1rm = None
    lp_interp = ""
    if lp_charge and lp_charge > 0 and lp_reps and lp_reps > 0:
        lp_1rm = compute_1rm(lp_charge, int(lp_reps))
        r_interp = interpret_leg_press(lp_1rm, bw)
        lp_interp = r_interp["interpretation"]
        st.markdown(
            f'<div class="score-box" style="background:{r_interp["color"]};">'
            f'1RM estimé : <b>{lp_1rm} kg</b> — {lp_interp}</div>',
            unsafe_allow_html=True)

    lp_notes = st.text_area("Notes Leg Press",
                            value=lv_fn("lp_notes", ""),
                            height=50,
                            key=f"{key_prefix}_lp_notes")
    collected.update({
        "lp_charge_kg": lp_charge or "",
        "lp_reps": lp_reps or "",
        "lp_1rm_estime": lp_1rm or "",
        "lp_interpretation": lp_interp,
        "lp_notes": lp_notes,
    })
    return collected


def _load_float(lv_fn, key):
    v = lv_fn(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=float(v); return r if r!=0.0 else None
    except: return None

def _load_int(lv_fn, key):
    v = lv_fn(key, None)
    if v is None or str(v).strip() in ("","None"): return None
    try: r=int(float(v)); return r if r!=0 else None
    except: return None
