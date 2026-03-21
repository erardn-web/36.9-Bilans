"""
bpco_data.py — Données cliniques BPCO
Tests : 6MWT, STS 1min, mMRC, CAT, BODE, Spirométrie, Saturation
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  mMRC — Modified Medical Research Council Dyspnoea Scale
# ═══════════════════════════════════════════════════════════════════════════════

MMRC_GRADES = [
    (0, "Grade 0 — Dyspnée seulement lors d'exercice intense"),
    (1, "Grade 1 — Dyspnée en montant une côte ou une légère pente"),
    (2, "Grade 2 — Marche plus lentement que les autres à plat ou s'arrête après ~100 m"),
    (3, "Grade 3 — S'arrête pour souffler après quelques minutes ou ~100 m à plat"),
    (4, "Grade 4 — Trop essoufflé pour quitter la maison ou s'habiller/déshabiller"),
]

# ═══════════════════════════════════════════════════════════════════════════════
#  CAT — COPD Assessment Test (8 items, 0–5)
# ═══════════════════════════════════════════════════════════════════════════════

CAT_ITEMS = [
    ("cat_1", "Je ne tousse jamais", "Je tousse tout le temps"),
    ("cat_2", "Je n'ai pas du tout de glaires dans la poitrine", "J'ai la poitrine pleine de glaires"),
    ("cat_3", "Je n'ai pas du tout la poitrine oppressée", "J'ai très fortement la poitrine oppressée"),
    ("cat_4", "Quand je monte une côte ou une flight of stairs, je ne suis pas essoufflé(e)",
              "Quand je monte une côte ou un escalier, je suis très essoufflé(e)"),
    ("cat_5", "Les activités à la maison ne me sont pas du tout limitées",
              "Les activités à la maison me sont très limitées"),
    ("cat_6", "Je suis confiant(e) de sortir de chez moi malgré ma condition pulmonaire",
              "Je ne suis pas du tout confiant(e) de sortir de chez moi à cause de ma condition pulmonaire"),
    ("cat_7", "Je dors profondément", "Je ne dors pas profondément à cause de ma condition pulmonaire"),
    ("cat_8", "J'ai plein d'énergie", "Je n'ai pas du tout d'énergie"),
]

CAT_KEYS = [c[0] for c in CAT_ITEMS]

def compute_cat(answers: dict) -> dict:
    vals = [int(answers[k]) for k in CAT_KEYS if str(answers.get(k,"")).strip() != ""]
    if not vals:
        return {"score": None, "color": "#888", "interpretation": ""}
    total = sum(vals)
    if total <= 10:
        color, interp = "#388e3c", "Impact faible (0–10)"
    elif total <= 20:
        color, interp = "#f57c00", "Impact modéré (11–20)"
    elif total <= 30:
        color, interp = "#e64a19", "Impact sévère (21–30)"
    else:
        color, interp = "#d32f2f", "Impact très sévère (31–40)"
    return {"score": total, "color": color, "interpretation": interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  BODE Index (0–10) — prédicteur mortalité BPCO
# ═══════════════════════════════════════════════════════════════════════════════

def compute_bode(fev1_pct, mmrc, dist_6mwt, bmi) -> dict:
    """Calcule le BODE index."""
    score = 0
    # VEMS % prédit
    if fev1_pct is not None:
        if fev1_pct >= 65:   score += 0
        elif fev1_pct >= 50: score += 1
        elif fev1_pct >= 36: score += 2
        else:                score += 3
    # mMRC
    if mmrc is not None:
        if mmrc <= 1:   score += 0
        elif mmrc == 2: score += 1
        elif mmrc == 3: score += 2
        else:           score += 3
    # Distance 6MWT
    if dist_6mwt is not None:
        if dist_6mwt >= 350:   score += 0
        elif dist_6mwt >= 250: score += 1
        elif dist_6mwt >= 150: score += 2
        else:                  score += 3
    # IMC
    if bmi is not None:
        score += 0 if bmi > 21 else 1

    if score <= 2:
        color, interp, survival = "#388e3c", "Quartile 1 — Bon pronostic (0–2)", "~80% survie 4 ans"
    elif score <= 4:
        color, interp, survival = "#f57c00", "Quartile 2 — Pronostic modéré (3–4)", "~67%"
    elif score <= 6:
        color, interp, survival = "#e64a19", "Quartile 3 — Pronostic réservé (5–6)", "~57%"
    else:
        color, interp, survival = "#d32f2f", "Quartile 4 — Pronostic sévère (7–10)", "~18%"
    return {"score": score, "color": color, "interpretation": interp, "survival": survival}


# ═══════════════════════════════════════════════════════════════════════════════
#  6MWT — normes de référence simplifiées
# ═══════════════════════════════════════════════════════════════════════════════

def interpret_6mwt(distance: float, age: int = None, sexe: str = None) -> dict:
    """Interprétation simplifiée de la distance au 6MWT."""
    if distance is None:
        return {"color": "#888", "interpretation": ""}
    # Seuils cliniques BPCO (indépendants de l'âge/sexe pour simplifier)
    if distance >= 400:
        color, interp = "#388e3c", "Bonne capacité fonctionnelle (≥ 400 m)"
    elif distance >= 300:
        color, interp = "#f57c00", "Capacité modérée (300–399 m)"
    elif distance >= 150:
        color, interp = "#e64a19", "Capacité limitée (150–299 m)"
    else:
        color, interp = "#d32f2f", "Capacité très limitée (< 150 m)"
    return {"color": color, "interpretation": interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  Google Sheets headers — Bilans_BPCO
# ═══════════════════════════════════════════════════════════════════════════════

def get_bpco_headers():
    h = ["bilan_id","patient_id","date_bilan","type_bilan","praticien","notes_generales"]
    # Spirométrie
    h += ["spiro_vems","spiro_cvf","spiro_ratio","spiro_vems_pct","spiro_cvf_pct",
          "spiro_gold","spiro_notes"]
    # Saturation
    h += ["spo2_repos","spo2_effort","spo2_min_effort"]
    # 6MWT
    h += ["mwt_distance","mwt_spo2_avant","mwt_spo2_apres","mwt_spo2_min",
          "mwt_fc_avant","mwt_fc_apres","mwt_fc_max",
          "mwt_dyspnee_avant","mwt_dyspnee_apres",
          "mwt_fatigue_avant","mwt_fatigue_apres",
          "mwt_aide_technique","mwt_incidents","mwt_interpretation"]
    # STS 1 min
    h += ["sts_1min_reps","sts_1min_interpretation"]
    # mMRC
    h += ["mmrc_grade"]
    # CAT
    h += CAT_KEYS + ["cat_score","cat_interpretation"]
    # BODE
    h += ["bmi","bode_score","bode_interpretation"]
    # IMC
    h += ["poids","taille"]
    return h
