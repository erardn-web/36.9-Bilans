"""
Définitions des tests cliniques supplémentaires pour le bilan SHV.
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  QUESTIONNAIRE DE NIJMEGEN
# ═══════════════════════════════════════════════════════════════════════════════

NIJMEGEN_ITEMS = [
    "Douleurs dans la poitrine",
    "Sensation de tension",
    "Vision trouble",
    "Étourdissements",
    "Confusion ou perte de contact avec l'environnement",
    "Mains et/ou pieds froids",
    "Fourmillements dans les mains et/ou les pieds",
    "Bouche sèche",
    "Fourmillements autour de la bouche",
    "Rigidité dans les mains et/ou les pieds",
    "Palpitations",
    "Anxiété",
    "Respiration rapide",
    "Respiration difficile",
    "Sensation d'étouffement",
    "Ballonnements abdominaux",
]

NIJMEGEN_OPTIONS = [
    (0, "Jamais"),
    (1, "Rarement"),
    (2, "Parfois"),
    (3, "Souvent"),
    (4, "Très souvent"),
]

NIJMEGEN_KEYS = [f"nij_{i+1}" for i in range(16)]


def compute_nijmegen(answers: dict) -> dict:
    """answers = {"nij_1": 2, "nij_2": 0, ...}"""
    total = sum(int(answers.get(k, 0) or 0) for k in NIJMEGEN_KEYS)
    if total >= 23:
        interp = "Positif — SHV probable (≥ 23)"
        color  = "#d32f2f"
    elif total >= 15:
        interp = "Borderline (15–22) — à surveiller"
        color  = "#f57c00"
    else:
        interp = "Négatif — SHV peu probable (< 15)"
        color  = "#388e3c"
    return {"score": total, "interpretation": interp, "color": color}


# ═══════════════════════════════════════════════════════════════════════════════
#  GAZOMÉTRIE
# ═══════════════════════════════════════════════════════════════════════════════

GAZO_FIELDS = [
    ("gazo_type",   "Type de prélèvement",    ["Artériel", "Veineux", "Capillaire"], "select"),
    ("gazo_ph",     "pH",                     "7.35 – 7.45",   "number"),
    ("gazo_paco2",  "PaCO₂ (mmHg)",           "35 – 45 mmHg",  "number"),
    ("gazo_pao2",   "PaO₂ (mmHg)",            "75 – 100 mmHg", "number"),
    ("gazo_hco3",   "HCO₃⁻ (mmol/L)",         "22 – 26 mmol/L","number"),
    ("gazo_sato2",  "SatO₂ (%)",              "≥ 95 %",        "number"),
    ("gazo_fio2",   "FiO₂ (%)",               "21 % (air amb.)","number"),
    ("gazo_notes",  "Notes / contexte",       "",              "text"),
]

def interpret_gazo(key, val):
    """Retourne (normal, message) selon les valeurs."""
    try:
        v = float(val)
    except (TypeError, ValueError):
        return None, ""
    ranges = {
        "gazo_ph":    (7.35, 7.45,  "Acidose"    , "Alcalose"),
        "gazo_paco2": (35,   45,    "Hypocapnie" , "Hypercapnie"),
        "gazo_pao2":  (75,   100,   "Hypoxémie"  , None),
        "gazo_hco3":  (22,   26,    "Bas"        , "Élevé"),
        "gazo_sato2": (95,   100,   "Désaturation", None),
    }
    if key not in ranges:
        return None, ""
    lo, hi, low_label, high_label = ranges[key]
    if v < lo:
        return False, f"⬇ {low_label} ({v})"
    if high_label and v > hi:
        return False, f"⬆ {high_label} ({v})"
    return True, f"✓ Normal ({v})"


# ═══════════════════════════════════════════════════════════════════════════════
#  CAPNOGRAPHIE
# ═══════════════════════════════════════════════════════════════════════════════

ETCO2_PATTERNS = [
    "Normal",
    "Hypocapnie (ETCO₂ < 35 mmHg)",
    "Hypocapnie sévère (ETCO₂ < 30 mmHg)",
    "Hypercapnie (ETCO₂ > 45 mmHg)",
    "Pattern irrégulier",
    "Non réalisé",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  PATTERN RESPIRATOIRE
# ═══════════════════════════════════════════════════════════════════════════════

PATTERN_MODES = [
    "Diaphragmatique (normal)",
    "Thoracique supérieur",
    "Mixte",
    "Paradoxal",
]

PATTERN_AMPLITUDES = [
    "Normale",
    "Superficielle",
    "Profonde",
    "Irrégulière",
]

PATTERN_RYTHMES = [
    "Régulier",
    "Irrégulier",
    "Avec apnées",
    "Avec soupirs fréquents",
    "Avec blocages",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  SNIF / PImax / PEmax
# ═══════════════════════════════════════════════════════════════════════════════

SNIF_PIMAX_PEMAX_VALEURS_REF = {
    "pimax": {
        "homme": {"18-30": -124, "31-50": -116, "51-70": -103, ">70": -85},
        "femme": {"18-30": -87,  "31-50": -79,  "51-70": -70,  ">70": -65},
    },
    "pemax": {
        "homme": {"18-30": 220,  "31-50": 196,  "51-70": 171,  ">70": 136},
        "femme": {"18-30": 138,  "31-50": 128,  "51-70": 118,  ">70": 100},
    },
}

def interpret_mip_mep(val, predicted):
    """Interprétation en % de la valeur prédite."""
    try:
        pct = abs(float(val)) / abs(float(predicted)) * 100
        if pct >= 80:
            return pct, "Normal (≥ 80%)", "#388e3c"
        elif pct >= 60:
            return pct, "Légèrement diminué (60–79%)", "#f57c00"
        else:
            return pct, "Diminué (< 60%)", "#d32f2f"
    except (TypeError, ValueError, ZeroDivisionError):
        return None, "—", "#888"


# ═══════════════════════════════════════════════════════════════════════════════
#  ÉCHELLE MRC DYSPNÉE
# ═══════════════════════════════════════════════════════════════════════════════

MRC_GRADES = [
    (0, "Grade 0 — Pas de dyspnée sauf en cas d'exercice intense"),
    (1, "Grade 1 — Dyspnée lors d'une montée rapide ou d'une côte légère"),
    (2, "Grade 2 — Marche plus lentement que les personnes du même âge à plat, "
        "ou s'arrête à son propre rythme"),
    (3, "Grade 3 — S'arrête après 100 m ou quelques minutes à plat"),
    (4, "Grade 4 — Trop essoufflé(e) pour quitter la maison, ou essoufflé(e) "
        "en s'habillant/déshabillant"),
]


# ═══════════════════════════════════════════════════════════════════════════════
#  COMORBIDITÉS
# ═══════════════════════════════════════════════════════════════════════════════

COMORB_CATEGORIES = {
    "🫁 Respiratoires": [
        "Asthme", "BPCO", "Emphysème", "Bronchectasies",
        "Rhinite / sinusite chronique", "Apnées du sommeil (SAOS)",
        "Fibrose pulmonaire",
    ],
    "❤️ Cardio-vasculaires": [
        "Insuffisance cardiaque", "Hypertension artérielle",
        "Arythmie / tachycardie", "Cardiopathie ischémique",
        "Embolie pulmonaire (antécédent)",
    ],
    "🧠 Neurologiques / Psychiatriques": [
        "Trouble anxieux généralisé", "Trouble panique",
        "Dépression", "Stress post-traumatique",
        "Épilepsie", "Sclérose en plaques",
    ],
    "🦴 Musculo-squelettiques": [
        "Scoliose / cyphose", "Douleurs chroniques",
        "Fibromyalgie", "Déformation thoracique",
    ],
    "⚗️ Métaboliques / Endocrines": [
        "Diabète", "Dysthyroïdie", "Anémie",
        "Reflux gastro-œsophagien (RGO)", "Grossesse",
    ],
    "💊 Traitements en cours": [
        "Bronchodilatateurs", "Corticoïdes inhalés", "Anxiolytiques / benzodiazépines",
        "Antidépresseurs", "Bêtabloquants", "Diurétiques",
    ],
}
