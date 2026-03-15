"""
SF-36 – Short Form Health Survey (36 items)
Version française validée (Leplège et al., 1998)
Scoring conforme à la méthode RAND/Ware.
"""

# ─── Items du questionnaire ──────────────────────────────────────────────────

SF36_Q1 = {
    "key": "q1",
    "texte": "En général, diriez-vous que votre santé est :",
    "options": [(1, "Excellente"), (2, "Très bonne"), (3, "Bonne"),
                (4, "Passable"), (5, "Mauvaise")],
}

SF36_Q2 = {
    "key": "q2",
    "texte": "Par rapport à il y a un an, comment évalueriez-vous votre état de santé actuel ?",
    "options": [(1, "Bien meilleure qu'il y a un an"), (2, "Plutôt meilleure qu'il y a un an"),
                (3, "À peu près pareille qu'il y a un an"),
                (4, "Plutôt moins bonne qu'il y a un an"),
                (5, "Bien moins bonne qu'il y a un an")],
}

SF36_Q3 = {
    "items": [
        ("q3a", "Activités intenses (course à pied, soulever des objets lourds, sports vigoureux)"),
        ("q3b", "Activités modérées (déplacer une table, faire le ménage, jardiner)"),
        ("q3c", "Soulever et porter des courses"),
        ("q3d", "Monter plusieurs étages par un escalier"),
        ("q3e", "Monter un seul étage par un escalier"),
        ("q3f", "Se pencher en avant, s'agenouiller, se baisser"),
        ("q3g", "Marcher plus d'un kilomètre et demi"),
        ("q3h", "Marcher plusieurs centaines de mètres"),
        ("q3i", "Marcher une centaine de mètres"),
        ("q3j", "Se laver ou s'habiller soi-même"),
    ],
    "intro": "Les questions suivantes portent sur des activités que vous pouvez faire au cours d'une journée ordinaire. "
             "Votre état de santé vous limite-t-il dans ces activités ?",
    "options": [(1, "Oui, très limité(e)"), (2, "Oui, un peu limité(e)"), (3, "Non, pas du tout limité(e)")],
}

SF36_Q4 = {
    "items": [
        ("q4a", "Avez-vous réduit le temps consacré à votre travail ou à vos activités habituelles ?"),
        ("q4b", "Avez-vous accompli moins de choses que vous le souhaitiez ?"),
        ("q4c", "Avez-vous été limité(e) dans le type de travail ou d'activités que vous pouviez faire ?"),
        ("q4d", "Avez-vous eu des difficultés à faire votre travail ou vos activités habituelles (plus d'efforts, par exemple) ?"),
    ],
    "intro": "Au cours des 4 dernières semaines, avez-vous eu des problèmes dans votre travail ou vos activités habituelles "
             "en raison de votre état de santé PHYSIQUE ?",
    "options": [(2, "Oui"), (1, "Non")],
}

SF36_Q5 = {
    "items": [
        ("q5a", "Avez-vous réduit le temps consacré à votre travail ou à vos activités habituelles ?"),
        ("q5b", "Avez-vous accompli moins de choses que vous le souhaitiez ?"),
        ("q5c", "Avez-vous eu des difficultés à faire votre travail ou vos activités habituelles avec moins de soin qu'avant ?"),
    ],
    "intro": "Au cours des 4 dernières semaines, avez-vous eu des problèmes dans votre travail ou vos activités habituelles "
             "en raison de problèmes ÉMOTIONNELS (comme vous sentir anxieux, déprimé ou irritable) ?",
    "options": [(2, "Oui"), (1, "Non")],
}

SF36_Q6 = {
    "key": "q6",
    "texte": "Au cours des 4 dernières semaines, dans quelle mesure votre état de santé ou vos problèmes émotionnels "
             "ont-ils gêné votre vie sociale et vos relations avec les autres (famille, amis, voisins, club...) ?",
    "options": [(1, "Pas du tout"), (2, "Un petit peu"), (3, "Modérément"),
                (4, "Beaucoup"), (5, "Extrêmement")],
}

SF36_Q7 = {
    "key": "q7",
    "texte": "Au cours des 4 dernières semaines, quelle a été l'intensité de vos douleurs physiques ?",
    "options": [(1, "Nulle"), (2, "Très faible"), (3, "Faible"),
                (4, "Modérée"), (5, "Forte"), (6, "Très forte")],
}

SF36_Q8 = {
    "key": "q8",
    "texte": "Au cours des 4 dernières semaines, dans quelle mesure la douleur a-t-elle gêné votre travail habituel "
             "(y compris les travaux à l'extérieur et à domicile) ?",
    "options": [(1, "Pas du tout"), (2, "Un petit peu"), (3, "Modérément"),
                (4, "Beaucoup"), (5, "Énormément")],
}

SF36_Q9_ITEMS = [
    ("q9a", "Plein(e) de vitalité"),
    ("q9b", "Très nerveux(se)"),
    ("q9c", "Si déprimé(e) que rien ne pouvait vous remonter le moral"),
    ("q9d", "Calme et détendu(e)"),
    ("q9e", "Plein(e) d'énergie"),
    ("q9f", "Découragé(e) et triste"),
    ("q9g", "Épuisé(e)"),
    ("q9h", "Heureux(se)"),
    ("q9i", "Fatigué(e)"),
]

SF36_Q9 = {
    "items": SF36_Q9_ITEMS,
    "intro": "Ces questions portent sur ce que vous avez ressenti et comment vous vous êtes comporté(e) "
             "au cours des 4 dernières semaines. Pour chaque question, quelle a été la fréquence de ces situations ?",
    "options": [(1, "Tout le temps"), (2, "La plupart du temps"), (3, "Souvent"),
                (4, "Quelquefois"), (5, "Rarement"), (6, "Jamais")],
}

SF36_Q10 = {
    "key": "q10",
    "texte": "Au cours des 4 dernières semaines, combien de fois des problèmes de santé ou émotionnels ont-ils gêné "
             "vos activités sociales (visites chez des amis, des parents...) ?",
    "options": [(1, "Tout le temps"), (2, "La plupart du temps"), (3, "Quelquefois"),
                (4, "Rarement"), (5, "Jamais")],
}

SF36_Q11 = {
    "items": [
        ("q11a", "Je tombe malade plus facilement que les autres"),
        ("q11b", "Je me porte aussi bien que n'importe qui"),
        ("q11c", "Je m'attends à ce que ma santé se dégrade"),
        ("q11d", "Je suis en parfaite santé"),
    ],
    "intro": "Dans quelle mesure les affirmations suivantes vous correspondent-elles ?",
    "options": [(1, "Tout à fait exacte"), (2, "Plutôt exacte"), (3, "Ne sais pas"),
                (4, "Plutôt fausse"), (5, "Absolument fausse")],
}


# ─── Scoring ─────────────────────────────────────────────────────────────────

def _recode(key, val):
    """Recodage selon la grille officielle SF-36 (RAND scoring)."""
    # Items à inverser ou recoder
    recode_map = {
        # Q1 : 1→100, 2→75, 3→50, 4→25, 5→0
        "q1":  {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
        # Q2 (non inclus dans les 8 dimensions)
        "q2":  {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
        # Q3a–j : 1→0, 2→50, 3→100
        **{f"q3{x}": {1: 0, 2: 50, 3: 100}
           for x in "abcdefghij"},
        # Q4a–d : 2(oui)→0, 1(non)→100  (items de limitation)
        **{f"q4{x}": {2: 0, 1: 100} for x in "abcd"},
        # Q5a–c : 2(oui)→0, 1(non)→100
        **{f"q5{x}": {2: 0, 1: 100} for x in "abc"},
        # Q6 : 1→100, 2→75, 3→50, 4→25, 5→0
        "q6":  {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
        # Q7 : 1→100, 2→80, 3→60, 4→40, 5→20, 6→0
        "q7":  {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0},
        # Q8 : 1→100, 2→75, 3→50, 4→25, 5→0  (douleur gêne travail)
        "q8":  {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
        # Q9a,d,e,h : vitalité/bien-être positifs → 1→100..6→0
        "q9a": {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0},
        "q9d": {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0},
        "q9e": {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0},
        "q9h": {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0},
        # Q9b,c,f,g,i : négatifs → 1→0..6→100
        "q9b": {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100},
        "q9c": {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100},
        "q9f": {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100},
        "q9g": {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100},
        "q9i": {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100},
        # Q10 : 1→0, 2→25, 3→50, 4→75, 5→100
        "q10": {1: 0, 2: 25, 3: 50, 4: 75, 5: 100},
        # Q11a,c : négatifs → 1→0..5→100
        "q11a": {1: 0, 2: 25, 3: 50, 4: 75, 5: 100},
        "q11c": {1: 0, 2: 25, 3: 50, 4: 75, 5: 100},
        # Q11b,d : positifs → 1→100..5→0
        "q11b": {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
        "q11d": {1: 100, 2: 75, 3: 50, 4: 25, 5: 0},
    }
    if val is None or val == "":
        return None
    mapping = recode_map.get(key)
    if mapping:
        return mapping.get(int(val))
    return None


def _mean(values):
    v = [x for x in values if x is not None]
    return round(sum(v) / len(v)) if v else None


def compute_sf36_scores(ans: dict) -> dict:
    """
    ans = {"q1": 3, "q3a": 2, ...}
    Retourne un dict avec les 8 dimensions (0-100).
    """
    r = {k: _recode(k, v) for k, v in ans.items()}

    pf = _mean([r.get(f"q3{x}") for x in "abcdefghij"])
    rp = _mean([r.get(f"q4{x}") for x in "abcd"])

    # BP : q7 et q8 combinés selon table de calibration simplifiée
    q7r = r.get("q7")
    q8r = r.get("q8")
    bp = _mean([q7r, q8r]) if q7r and q8r else q7r or q8r

    gh = _mean([r.get("q1"),
                r.get("q11a"), r.get("q11b"), r.get("q11c"), r.get("q11d")])

    vt = _mean([r.get("q9a"), r.get("q9e"), r.get("q9g"), r.get("q9i")])

    # SF : q6 et q10
    sf_score = _mean([r.get("q6"), r.get("q10")])

    re = _mean([r.get(f"q5{x}") for x in "abc"])

    mh = _mean([r.get("q9b"), r.get("q9c"), r.get("q9d"), r.get("q9f"), r.get("q9h")])

    return {
        "pf": pf, "rp": rp, "bp": bp, "gh": gh,
        "vt": vt, "sf": sf_score, "re": re, "mh": mh,
    }


SF36_DIMENSIONS = {
    "pf": "Fonctionnement physique",
    "rp": "Limitations dues à l'état physique",
    "bp": "Douleur physique",
    "gh": "Santé générale",
    "vt": "Vitalité",
    "sf": "Vie et relations sociales",
    "re": "Limitations dues à l'état émotionnel",
    "mh": "Santé psychique",
}
