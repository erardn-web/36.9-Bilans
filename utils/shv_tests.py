"""
Tests spécifiques au SHV :
  - BOLT (Body Oxygen Level Test)
  - Test d'hyperventilation volontaire (THV)
"""

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
