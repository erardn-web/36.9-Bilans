"""
Données cliniques pour le bilan Lombalgie.
Classification SIN/ROM/EOR/MOM, drapeaux, diagnostics différentiels, SOAP.
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  CLASSIFICATION CLINIQUE
# ═══════════════════════════════════════════════════════════════════════════════

GROUPES_CLINIQUES = [
    ("—",   "— Non classifié —",    ""),
    ("SIN", "🔴 Groupe SIN",
     "Douleur intense (EVA > 7/10), haute irritabilité. "
     "La douleur persiste longtemps après l'arrêt du stimulus. "
     "→ Soulagement, techniques douces Grades I-II, éducation neuro-centrée."),
    ("ROM", "🟠 Groupe ROM",
     "Douleur durant le mouvement, limitation marquée de la mobilité. "
     "→ Focus sur la récupération d'amplitude, favoriser le glissement tissulaire."),
    ("EOR", "🟡 Groupe EOR",
     "Douleur uniquement en fin d'amplitude (End of Range). Faible irritabilité. "
     "→ Mobilisation intensive (dans la douleur), Grades III-IV pour la prolifération tissulaire."),
    ("MOM", "🟢 Groupe MOM",
     "Momentary Pain : douleur brève lors d'une charge spécifique, disparaît instantanément. "
     "→ Renforcement fonctionnel, tests de provocation et désensibilisation."),
]

GROUPES_OPTIONS   = [g[1] for g in GROUPES_CLINIQUES]
GROUPES_CODES     = [g[0] for g in GROUPES_CLINIQUES]
GROUPES_DESC      = {g[0]: g[2] for g in GROUPES_CLINIQUES}
GROUPES_COLORS    = {"SIN": "#d32f2f", "ROM": "#f57c00",
                     "EOR": "#fbc02d", "MOM": "#388e3c", "—": "#888"}

# ═══════════════════════════════════════════════════════════════════════════════
#  DRAPEAUX ROUGES
# ═══════════════════════════════════════════════════════════════════════════════

DRAPEAUX_ROUGES = [
    "Âge < 20 ans ou > 55 ans avec douleur nouvelle",
    "Traumatisme violent récent",
    "Douleur non mécanique (constante, nocturne, indépendante de la position)",
    "Douleur thoracique associée",
    "Antécédent de cancer",
    "Usage prolongé de corticoïdes",
    "Consommation de drogues IV / immunodépression",
    "Perte de poids inexpliquée",
    "Syndrome de la queue de cheval (troubles sphinctériens, anesthésie en selle)",
    "Déficit neurologique progressif",
    "Déformation structurale sévère",
    "Fièvre / état général altéré",
]

DRAPEAUX_JAUNES = [
    "Croyances négatives sur la douleur (catastrophisme)",
    "Peur du mouvement / kinésiophobie",
    "Comportement d'évitement marqué",
    "Dépression / anxiété associée",
    "Faible soutien social ou familial",
    "Insatisfaction au travail / conflit professionnel",
    "Litige juridique ou compensation en cours",
    "Attentes thérapeutiques irréalistes",
    "Historique de douleur chronique",
    "Hypervigilance corporelle",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNOSTICS DIFFÉRENTIELS
# ═══════════════════════════════════════════════════════════════════════════════

DIAG_DIFF = {
    "🦴 Structuraux": [
        "Hernie discale",
        "Sténose canalaire",
        "Spondylolisthésis",
        "Fracture vertébrale",
        "Arthrose facettaire (syndrome facettaire)",
        "Sacro-iliite",
    ],
    "💪 Musculo-fascial": [
        "Syndrome myofascial du psoas",
        "Syndrome myofascial du carré des lombes",
        "Syndrome myofascial des érecteurs du rachis",
        "Syndrome myofascial des fessiers",
        "Contracture paravertébrale",
    ],
    "🧠 Neurologique": [
        "Radiculopathie L4",
        "Radiculopathie L5",
        "Radiculopathie S1",
        "Syndrome de la queue de cheval",
        "Sensibilisation centrale",
    ],
    "🔴 Pathologies graves (drapeaux rouges)": [
        "Spondylarthrite ankylosante",
        "Tumeur / métastase vertébrale",
        "Infection (spondylodiscite)",
        "Fracture ostéoporotique",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
#  LOCALISATIONS DE LA DOULEUR
# ═══════════════════════════════════════════════════════════════════════════════

LOCALISATIONS = [
    "Lombaire basse (L4-S1)",
    "Lombaire haute (T12-L3)",
    "Sacro-iliaque droite",
    "Sacro-iliaque gauche",
    "Fessière droite",
    "Fessière gauche",
    "Irradiation membre inf. droit",
    "Irradiation membre inf. gauche",
    "Bilatérale",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  COMPORTEMENT DE LA DOULEUR
# ═══════════════════════════════════════════════════════════════════════════════

FACTEURS_AGGRAVANTS = [
    "Flexion", "Extension", "Rotation droite", "Rotation gauche",
    "Latéroflexion droite", "Latéroflexion gauche",
    "Station assise prolongée", "Station debout prolongée",
    "Marche", "Montée/descente d'escaliers",
    "Port de charges", "Toux / éternuement",
    "Position couchée", "Réveil matinal",
]

FACTEURS_SOULAGEANTS = [
    "Repos", "Chaleur", "Froid", "Mouvement doux",
    "Position couchée sur le dos", "Position couchée sur le ventre",
    "Position fœtale", "Marche",
    "Antalgiques", "AINS", "Étirements",
]

TYPES_DOULEUR = [
    "Mécanique (liée au mouvement)",
    "Inflammatoire (nocturne, raideur matinale)",
    "Neuropathique (brûlure, décharge électrique)",
    "Mixte",
]

RYTHME_DOULEUR = [
    "Continue", "Intermittente", "Nocturne uniquement",
    "Matinale puis amélioration", "En fin de journée",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  TESTS CLINIQUES OBJECTIFS
# ═══════════════════════════════════════════════════════════════════════════════

TESTS_CLINIQUES = {
    "Tests de mobilité": [
        "Flexion lombaire (Schober modifié)",
        "Extension lombaire",
        "Latéroflexion droite / gauche",
        "Rotation droite / gauche",
    ],
    "Tests neurologiques": [
        "Lasègue (SLR) droit",
        "Lasègue (SLR) gauche",
        "Lasègue croisé",
        "Test de Bragard",
        "Réflexe rotulien",
        "Réflexe achilléen",
        "Sensibilité dermatomes L4/L5/S1",
        "Force quadriceps / tibial ant. / triceps sural",
    ],
    "Tests sacro-iliaques": [
        "FABER (Patrick)",
        "Gaenslen",
        "Compression sacro-iliaque",
        "Distraction sacro-iliaque",
        "Test de Gillet (marche)",
    ],
    "Tests de provocation discale": [
        "Valsalva",
        "Compression axiale",
        "Décompression axiale",
    ],
    "Tests de contrôle moteur": [
        "Test d'activation TVA",
        "Test de Trendelenburg",
        "Test pont fessier unilatéral",
    ],
}

RESULTATS_TEST = ["—", "Négatif", "Positif droit", "Positif gauche", "Positif bilatéral", "Non réalisé"]
