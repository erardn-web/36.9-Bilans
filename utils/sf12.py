"""
SF-12 – Short Form Health Survey (12 items)
Version française validée (Gandek et al., 1998)
Produit deux scores composites : PCS-12 (physique) et MCS-12 (mental)
ainsi que les 8 dimensions estimées.

Scoring : méthode des coefficients de régression (Ware et al., 1996)
avec normes de la population générale américaine (mean=50, SD=10).
"""

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
