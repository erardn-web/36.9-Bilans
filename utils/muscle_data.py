"""
muscle_data.py — Testing musculaire membres inférieurs (partagé SHV/BPCO/Équilibre)
"""

# ─── MRC Scale ────────────────────────────────────────────────────────────────
MRC_SCALE = [
    (0, "0 — Pas de contraction"),
    (1, "1 — Contraction visible sans mouvement"),
    (2, "2 — Mouvement pesanteur éliminée"),
    (3, "3 — Mouvement contre pesanteur"),
    (4, "4 — Mouvement contre résistance partielle"),
    (5, "5 — Force normale"),
]
MRC_VALUES = [s for s, _ in MRC_SCALE]

# ─── Groupes musculaires ──────────────────────────────────────────────────────
MUSCLE_GROUPS = [
    ("hip_flex",  "Fléchisseurs de hanche",     "Décubitus dorsal — flexion contre résistance"),
    ("hip_ext",   "Extenseurs de hanche",        "Décubitus ventral — extension contre résistance"),
    ("hip_abd",   "Abducteurs de hanche",        "Décubitus latéral — abduction contre résistance"),
    ("hip_add",   "Adducteurs de hanche",        "Décubitus latéral — adduction contre résistance"),
    ("knee_ext",  "Extenseurs genou (Quadriceps)","Assis — extension contre résistance"),
    ("knee_flex", "Fléchisseurs genou (IJ)",     "Décubitus ventral — flexion contre résistance"),
    ("ankle_df",  "Dorsiflexeurs cheville",      "Décubitus dorsal — dorsiflexion contre résistance"),
    ("ankle_pf",  "Plantarflexeurs cheville",    "Debout — montée sur pointe des pieds"),
]

SIDES = ["d", "g"]

def get_muscle_key(key_sfx, side):
    return f"musc_{key_sfx}_{side}"

def get_muscle_keys():
    keys = []
    for key_sfx, _, _ in MUSCLE_GROUPS:
        keys += [get_muscle_key(key_sfx, s) for s in SIDES]
    keys.append("musc_notes")
    return keys

def compute_muscle_score(answers: dict) -> dict:
    vals = []
    for key_sfx, _, _ in MUSCLE_GROUPS:
        for side in SIDES:
            k = get_muscle_key(key_sfx, side)
            v = answers.get(k)
            if v is not None and str(v).strip() not in ("", "None"):
                try: vals.append(int(float(v)))
                except: pass
    if not vals:
        return {"mean": None, "total": None, "count": 0, "max": 0, "color": "#888"}
    total = sum(vals)
    mean  = round(total / len(vals), 1)
    max_  = len(vals) * 5
    if mean >= 4.5:   color = "#388e3c"
    elif mean >= 3.5: color = "#8bc34a"
    elif mean >= 2.5: color = "#f57c00"
    else:             color = "#d32f2f"
    return {"mean": mean, "total": total, "count": len(vals), "max": max_, "color": color}


# ─── 1RM Leg Press ────────────────────────────────────────────────────────────
LEG_PRESS_KEYS = ["lp_charge_kg", "lp_reps", "lp_1rm_estime", "lp_interpretation", "lp_notes"]

def compute_1rm(weight_kg: float, reps: int):
    if not weight_kg or not reps or reps <= 0 or weight_kg <= 0:
        return None
    if reps == 1:
        return round(weight_kg, 1)
    if reps > 10:
        return round(weight_kg * (1 + reps / 30), 1)
    return round(weight_kg / (1.0278 - 0.0278 * reps), 1)

def interpret_leg_press(weight_1rm_kg, body_weight_kg=None) -> dict:
    if weight_1rm_kg is None:
        return {"color": "#888", "interpretation": ""}
    if body_weight_kg and body_weight_kg > 0:
        ratio = weight_1rm_kg / body_weight_kg
        if ratio >= 2.0:   c,i = "#388e3c", f"Très bon ({ratio:.1f}× PC)"
        elif ratio >= 1.5: c,i = "#8bc34a", f"Bon ({ratio:.1f}× PC)"
        elif ratio >= 1.0: c,i = "#f57c00", f"Moyen ({ratio:.1f}× PC)"
        else:              c,i = "#d32f2f", f"Faible ({ratio:.1f}× PC)"
    else:
        if weight_1rm_kg >= 150:   c,i = "#388e3c", "≥ 150 kg"
        elif weight_1rm_kg >= 100: c,i = "#f57c00", "100–149 kg"
        else:                      c,i = "#d32f2f", "< 100 kg"
    return {"color": c, "interpretation": i}
