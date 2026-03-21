"""
shv_data.py — Données SHV
Fusion : had.py · sf12.py · shv_tests.py · clinical_data.py
"""



# ════════════════════════════════════════════════════════════
# had.py
# ════════════════════════════════════════════════════════════
HAD_QUESTIONS = [
    # (clé, sous-échelle, texte, options [(score, label), ...])
    (
        "a1", "A",
        "Je me sens tendu(e) ou énervé(e) :",
        [(3, "La plupart du temps"), (2, "Souvent"),
         (1, "De temps en temps"), (0, "Jamais")],
    ),
    (
        "d1", "D",
        "Je prends toujours autant de plaisir aux mêmes choses qu'autrefois :",
        [(0, "Oui, tout autant"), (1, "Pas autant"),
         (2, "Un peu seulement"), (3, "Presque plus")],
    ),
    (
        "a2", "A",
        "J'éprouve des sensations de peur comme si quelque chose d'horrible allait m'arriver :",
        [(3, "Oui, très nettement"), (2, "Oui, mais ce n'est pas trop grave"),
         (1, "Un peu, mais ça ne m'inquiète pas"), (0, "Pas du tout")],
    ),
    (
        "d2", "D",
        "Je ris facilement et vois le bon côté des choses :",
        [(0, "Autant que par le passé"), (1, "Plus autant qu'avant"),
         (2, "Vraiment moins qu'avant"), (3, "Plus du tout")],
    ),
    (
        "a3", "A",
        "Les idées se bousculent dans ma tête :",
        [(3, "La plupart du temps"), (2, "Assez souvent"),
         (1, "De temps en temps"), (0, "Très occasionnellement")],
    ),
    (
        "d3", "D",
        "Je me sens de bonne humeur :",
        [(3, "Jamais"), (2, "Rarement"),
         (1, "Assez souvent"), (0, "La plupart du temps")],
    ),
    (
        "a4", "A",
        "Je peux rester tranquillement assis(e) à ne rien faire et me sentir décontracté(e) :",
        [(0, "Oui, quoi qu'il arrive"), (1, "Oui, en général"),
         (2, "Rarement"), (3, "Jamais")],
    ),
    (
        "d4", "D",
        "J'ai l'impression de fonctionner au ralenti :",
        [(3, "Presque toujours"), (2, "Très souvent"),
         (1, "Parfois"), (0, "Jamais")],
    ),
    (
        "a5", "A",
        "J'éprouve des sensations de peur et j'ai l'estomac noué :",
        [(0, "Jamais"), (1, "Parfois"),
         (2, "Assez souvent"), (3, "Très souvent")],
    ),
    (
        "d5", "D",
        "Je ne m'intéresse plus à mon apparence :",
        [(3, "Plus du tout"), (2, "Je n'y accorde pas autant d'attention que je devrais"),
         (1, "Il se peut que je n'y fasse pas autant attention"), (0, "J'y prête autant d'attention que par le passé")],
    ),
    (
        "a6", "A",
        "Je me sens agité(e) comme si j'avais continuellement besoin de bouger :",
        [(3, "Vraiment très souvent"), (2, "Assez souvent"),
         (1, "Pas tellement"), (0, "Pas du tout")],
    ),
    (
        "d6", "D",
        "Je me réjouis à l'avance à l'idée de faire certaines choses :",
        [(0, "Autant qu'avant"), (1, "Un peu moins qu'avant"),
         (2, "Bien moins qu'avant"), (3, "Presque jamais")],
    ),
    (
        "a7", "A",
        "J'éprouve des sensations soudaines de panique :",
        [(3, "Vraiment très souvent"), (2, "Assez souvent"),
         (1, "Pas tellement"), (0, "Jamais du tout")],
    ),
    (
        "d7", "D",
        "Je peux prendre plaisir à un bon livre ou à une bonne émission de radio ou de télévision :",
        [(0, "Souvent"), (1, "Parfois"),
         (2, "Rarement"), (3, "Très rarement")],
    ),
]


def compute_had_scores(answers: dict) -> dict:
    """
    answers = {"a1": 2, "d1": 0, ...}
    Retourne {"score_anxiete": int, "score_depression": int,
              "interp_anxiete": str, "interp_depression": str}
    """
    score_a = sum(answers.get(f"a{i}", 0) for i in range(1, 8))
    score_d = sum(answers.get(f"d{i}", 0) for i in range(1, 8))

    def interp(s):
        if s <= 7:
            return "Normal (0–7)"
        elif s <= 10:
            return "Douteux (8–10)"
        else:
            return "Pathologique (11–21)"

    return {
        "score_anxiete": score_a,
        "score_depression": score_d,
        "interp_anxiete": interp(score_a),
        "interp_depression": interp(score_d),
    }

# ════════════════════════════════════════════════════════════
# sf12.py
# ════════════════════════════════════════════════════════════
# ─── Items ───────────────────────────────────────────────────────────────────

SF12_QUESTIONS = [
    {
        "key": "q1",
        "dim": "GH",
        "texte": "En général, diriez-vous que votre santé est :",
        "options": [
            (1, "Excellente"),
            (2, "Très bonne"),
            (3, "Bonne"),
            (4, "Passable"),
            (5, "Mauvaise"),
        ],
    },
    {
        "key": "q2a",
        "dim": "PF",
        "texte": "Activités modérées (déplacer une table, passer l'aspirateur, faire du vélo) — "
                 "Votre état de santé vous limite-t-il dans cette activité ?",
        "options": [
            (1, "Oui, très limité(e)"),
            (2, "Oui, un peu limité(e)"),
            (3, "Non, pas du tout limité(e)"),
        ],
    },
    {
        "key": "q2b",
        "dim": "PF",
        "texte": "Monter plusieurs étages par un escalier — "
                 "Votre état de santé vous limite-t-il dans cette activité ?",
        "options": [
            (1, "Oui, très limité(e)"),
            (2, "Oui, un peu limité(e)"),
            (3, "Non, pas du tout limité(e)"),
        ],
    },
    {
        "key": "q3a",
        "dim": "RP",
        "intro": "Au cours des 4 dernières semaines, avez-vous eu des problèmes dans votre "
                 "travail ou vos activités habituelles en raison de votre état de santé PHYSIQUE ?",
        "texte": "Avez-vous accompli moins de choses que vous le souhaitiez ?",
        "options": [(1, "Oui"), (2, "Non")],
    },
    {
        "key": "q3b",
        "dim": "RP",
        "texte": "Avez-vous été limité(e) dans certaines activités ?",
        "options": [(1, "Oui"), (2, "Non")],
    },
    {
        "key": "q4a",
        "dim": "RE",
        "intro": "Au cours des 4 dernières semaines, avez-vous eu des problèmes dans votre "
                 "travail ou vos activités habituelles en raison de problèmes ÉMOTIONNELS ?",
        "texte": "Avez-vous accompli moins de choses que vous le souhaitiez ?",
        "options": [(1, "Oui"), (2, "Non")],
    },
    {
        "key": "q4b",
        "dim": "RE",
        "texte": "Avez-vous fait ce travail ou ces activités avec moins de soin que d'habitude ?",
        "options": [(1, "Oui"), (2, "Non")],
    },
    {
        "key": "q5",
        "dim": "BP",
        "texte": "Au cours des 4 dernières semaines, dans quelle mesure la douleur a-t-elle "
                 "gêné votre travail habituel (y compris les travaux à l'extérieur et à domicile) ?",
        "options": [
            (1, "Pas du tout"),
            (2, "Un petit peu"),
            (3, "Modérément"),
            (4, "Beaucoup"),
            (5, "Énormément"),
        ],
    },
    {
        "key": "q6a",
        "dim": "MH",
        "intro": "Ces questions portent sur ce que vous avez ressenti au cours des 4 dernières "
                 "semaines. Pour chaque question, quelle a été la fréquence de ces situations ?",
        "texte": "Vous êtes-vous senti(e) calme et détendu(e) ?",
        "options": [
            (1, "Tout le temps"),
            (2, "La plupart du temps"),
            (3, "Souvent"),
            (4, "Quelquefois"),
            (5, "Rarement"),
            (6, "Jamais"),
        ],
    },
    {
        "key": "q6b",
        "dim": "VT",
        "texte": "Avez-vous eu beaucoup d'énergie ?",
        "options": [
            (1, "Tout le temps"),
            (2, "La plupart du temps"),
            (3, "Souvent"),
            (4, "Quelquefois"),
            (5, "Rarement"),
            (6, "Jamais"),
        ],
    },
    {
        "key": "q6c",
        "dim": "MH",
        "texte": "Vous êtes-vous senti(e) abattu(e) et triste ?",
        "options": [
            (1, "Tout le temps"),
            (2, "La plupart du temps"),
            (3, "Souvent"),
            (4, "Quelquefois"),
            (5, "Rarement"),
            (6, "Jamais"),
        ],
    },
    {
        "key": "q7",
        "dim": "SF",
        "texte": "Au cours des 4 dernières semaines, dans quelle mesure votre état de santé "
                 "physique ou vos problèmes émotionnels ont-ils gêné vos activités sociales "
                 "(visites chez des amis, des parents…) ?",
        "options": [
            (1, "Tout le temps"),
            (2, "La plupart du temps"),
            (3, "Quelquefois"),
            (4, "Rarement"),
            (5, "Jamais"),
        ],
    },
]

SF12_KEYS = [q["key"] for q in SF12_QUESTIONS]

SF12_DIMENSIONS = {
    "pf":  "Fonctionnement physique",
    "rp":  "Limitations physiques",
    "bp":  "Douleur physique",
    "gh":  "Santé générale",
    "vt":  "Vitalité",
    "sf":  "Vie sociale",
    "re":  "Limitations émotionnelles",
    "mh":  "Santé psychique",
    "pcs": "Score composite physique (PCS-12)",
    "mcs": "Score composite mental (MCS-12)",
}


# ─── Recodage ─────────────────────────────────────────────────────────────────

def _recode_sf12(key, val):
    """
    Transforme la réponse brute (1-6) en score 0-100 selon la grille SF-12.
    """
    if val is None or val == "":
        return None
    v = int(val)
    maps = {
        # GH : 1→100, 2→75, 3→50, 4→25, 5→0
        "q1":  {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
        # PF : 1→0, 2→50, 3→100
        "q2a": {1: 0, 2: 50, 3: 100},
        "q2b": {1: 0, 2: 50, 3: 100},
        # RP : 1(oui)→0, 2(non)→100
        "q3a": {1: 0, 2: 100},
        "q3b": {1: 0, 2: 100},
        # RE : 1(oui)→0, 2(non)→100
        "q4a": {1: 0, 2: 100},
        "q4b": {1: 0, 2: 100},
        # BP : 1→100, 2→75, 3→50, 4→25, 5→0
        "q5":  {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
        # MH calme : 1→100..6→0
        "q6a": {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0},
        # VT énergie : 1→100..6→0
        "q6b": {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0},
        # MH abattu (inversé) : 1→0..6→100
        "q6c": {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100},
        # SF : 1→0..5→100
        "q7":  {1: 0, 2: 25, 3: 50, 4: 75, 5: 100},
    }
    return maps.get(key, {}).get(v)


def _mean(vals):
    v = [x for x in vals if x is not None]
    return round(sum(v) / len(v)) if v else None


# ─── Scoring SF-12 ────────────────────────────────────────────────────────────

def compute_sf12_scores(answers: dict) -> dict:
    """
    answers = {"q1": 3, "q2a": 2, ...}
    Retourne un dict avec les 8 dimensions + PCS-12 + MCS-12 (0-100).

    Les scores PCS-12 / MCS-12 sont estimés par régression linéaire
    selon les coefficients de Ware et al. (1996) — normes US 1998.
    """
    r = {k: _recode_sf12(k, v) for k, v in answers.items()}

    pf  = _mean([r.get("q2a"), r.get("q2b")])
    rp  = _mean([r.get("q3a"), r.get("q3b")])
    bp  = r.get("q5")
    gh  = r.get("q1")
    vt  = r.get("q6b")
    sf  = r.get("q7")
    re  = _mean([r.get("q4a"), r.get("q4b")])
    mh  = _mean([r.get("q6a"), r.get("q6c")])

    # ── PCS / MCS par régression (coefficients Ware 1996, normes US) ──────────
    # Chaque dimension recodée en z-score (mean=50, SD=10) avant régression
    # Coefficients PCS et MCS issus de l'article original
    def z(score, mean, sd):
        return (score - mean) / sd if score is not None else 0

    # Moyennes et SD population de référence (Ware 1996)
    ref = {
        "pf": (81.18, 29.10), "rp": (80.52, 34.50),
        "bp": (75.49, 23.56), "gh": (72.21, 20.16),
        "vt": (61.05, 20.86), "sf": (83.59, 22.37),
        "re": (86.41, 30.09), "mh": (74.74, 18.05),
    }
    scores_dim = {"pf": pf, "rp": rp, "bp": bp, "gh": gh,
                  "vt": vt, "sf": sf, "re": re, "mh": mh}
    zs = {k: z(v, ref[k][0], ref[k][1]) for k, v in scores_dim.items()
          if v is not None}

    # Coefficients de régression PCS-12
    pcs_coef = {"pf": 0.42402, "rp": 0.35119, "bp": 0.31754, "gh": 0.24954,
                "vt": 0.02877, "sf": -0.00753, "re": -0.19206, "mh": -0.22069}
    # Coefficients de régression MCS-12
    mcs_coef = {"pf": -0.22999, "rp": -0.12329, "bp": -0.09731, "gh": -0.01571,
                "vt": 0.23534, "sf": 0.26876,  "re": 0.43407,  "mh": 0.48581}

    pcs_raw = sum(zs.get(k, 0) * v for k, v in pcs_coef.items())
    mcs_raw = sum(zs.get(k, 0) * v for k, v in mcs_coef.items())

    # Mise à l'échelle (mean=50, SD=10)
    pcs = round(pcs_raw * 10 + 50, 1) if zs else None
    mcs = round(mcs_raw * 10 + 50, 1) if zs else None

    return {
        "pf": pf, "rp": rp, "bp": bp, "gh": gh,
        "vt": vt, "sf": sf, "re": re, "mh": mh,
        "pcs": pcs, "mcs": mcs,
    }


def interpret_pcs_mcs(score) -> str:
    if score is None:
        return "—"
    if score >= 55:
        return "Au-dessus de la moyenne"
    if score >= 45:
        return "Dans la moyenne (45–55)"
    if score >= 35:
        return "En-dessous de la moyenne"
    return "Très en-dessous de la moyenne (< 35)"

# ════════════════════════════════════════════════════════════
# shv_tests.py
# ════════════════════════════════════════════════════════════
# ─── BOLT ────────────────────────────────────────────────────────────────────

BOLT_DESCRIPTION = """
**Protocole :**
1. Le patient respire normalement pendant 1 à 2 minutes (ne pas modifier la respiration).
2. Après une **expiration normale** (pas forcée), le patient bloque sa respiration.
3. Chronométrer jusqu'aux **premières envies nettes de respirer** (léger inconfort, premier mouvement involontaire du diaphragme).
4. Relâcher et noter le temps en secondes.

> ⚠️ Il ne s'agit pas de résister le plus longtemps possible, mais de noter la **première envie** de respirer.
"""

def interpret_bolt(seconds: int) -> dict:
    if seconds is None:
        return {}
    if seconds < 10:
        return {"cat": "Très altéré", "color": "#d32f2f",
                "desc": "Dysfonction respiratoire sévère, tolérance au CO₂ très basse."}
    elif seconds < 20:
        return {"cat": "Altéré", "color": "#f57c00",
                "desc": "Contrôle respiratoire altéré, possible SHV significatif."}
    elif seconds < 40:
        return {"cat": "Moyen", "color": "#fbc02d",
                "desc": "Tolérance au CO₂ correcte mais améliorable."}
    else:
        return {"cat": "Bon", "color": "#388e3c",
                "desc": "Bonne tolérance au CO₂, contrôle respiratoire satisfaisant."}


# ─── Test d'hyperventilation volontaire (THV) ────────────────────────────────

HVT_DESCRIPTION = """
**Protocole :**
1. Expliquer au patient qu'il va volontairement respirer plus profondément et plus vite pendant **3 minutes**.
2. Lui demander de noter les symptômes qui apparaissent pendant le test.
3. Après le test, noter le **temps de retour à la normale** (disparition des symptômes).
4. Le test est **positif** si les symptômes reproduits correspondent aux plaintes habituelles du patient.

> ⚠️ Contre-indications : épilepsie, grossesse, pathologie cardiaque sévère, AVC récent.
> Toujours avoir le consentement du patient avant de réaliser ce test.
"""

HVT_SYMPTOMES = [
    # Neurologiques / sensoriels
    "Vertiges / étourdissements",
    "Céphalées",
    "Vision trouble / flou visuel",
    "Fourmillements des extrémités (mains, pieds)",
    "Fourmillements péribuccaux",
    "Engourdissements",
    "Spasmes musculaires / tétanie",
    # Cardio-respiratoires
    "Essoufflement",
    "Douleur / oppression thoracique",
    "Palpitations",
    "Sensation de manque d'air",
    # Psychologiques / émotionnels
    "Anxiété",
    "Sentiment de panique",
    "Dépersonnalisation",
    # Autres
    "Nausées",
    "Fatigue / épuisement soudain",
    "Bouche sèche",
    "Bâillements répétés",
]

# ════════════════════════════════════════════════════════════
# clinical_data.py
# ════════════════════════════════════════════════════════════
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
