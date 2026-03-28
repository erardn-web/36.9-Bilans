"""utils/search.py — Moteur de recherche fuzzy réutilisable (accents, fautes, distance)"""
import unicodedata, re

def normalize(text: str) -> str:
    """Supprime accents, met en minuscule, retire ponctuation."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()

def _levenshtein(a: str, b: str) -> int:
    """Distance de Levenshtein entre deux chaînes."""
    if len(a) < len(b): a, b = b, a
    if not b: return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j+1]+1, curr[j]+1,
                            prev[j] + (0 if ca == cb else 1)))
        prev = curr
    return prev[-1]

def fuzzy_score(query: str, corpus: str, tags: list = None) -> float:
    """
    Score de pertinence fuzzy entre query et corpus.
    - Normalise accents et casse
    - Cherche chaque mot de la query dans le corpus (partiel ou distance ≤ 2)
    - Bonus pour les tags exacts
    Retourne un score > 0 si pertinent, 0 sinon.
    """
    if not query.strip():
        return 0.0

    q_norm = normalize(query)
    c_norm = normalize(corpus)
    t_norm = [normalize(t) for t in (tags or [])]

    q_words = q_norm.split()
    c_words = c_norm.split()
    score = 0.0

    for qw in q_words:
        if len(qw) < 2:
            continue
        matched = False
        # Correspondance exacte ou partielle dans le corpus
        if qw in c_norm:
            score += 2.0
            matched = True
        else:
            # Correspondance partielle dans chaque mot du corpus
            for cw in c_words:
                if qw in cw or cw in qw:
                    score += 1.5
                    matched = True
                    break
            if not matched:
                # Distance de Levenshtein — tolérance selon longueur du mot
                max_dist = 1 if len(qw) <= 4 else 2
                for cw in c_words:
                    if abs(len(qw) - len(cw)) <= max_dist:
                        d = _levenshtein(qw, cw)
                        if d <= max_dist:
                            score += max(0.5, 1.5 - d * 0.5)
                            matched = True
                            break

        # Bonus tags
        for t in t_norm:
            if qw in t or _levenshtein(qw, t) <= 1:
                score += 1.0
                break

    return score


def search_items(query: str, items: list, key_fn) -> list:
    """
    Filtre et trie une liste d'items par score fuzzy.
    key_fn(item) -> (corpus_str, tags_list)
    Retourne les items avec score > 0, triés par score décroissant.
    """
    if not query.strip():
        return []
    scored = []
    for item in items:
        corpus, tags = key_fn(item)
        s = fuzzy_score(query, corpus, tags)
        if s > 0:
            scored.append((item, s))
    return [item for item, _ in sorted(scored, key=lambda x: -x[1])]
