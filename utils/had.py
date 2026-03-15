"""
Échelle HAD – Hospital Anxiety and Depression Scale
Version française validée (Zigmond & Snaith, 1983)
"""

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
