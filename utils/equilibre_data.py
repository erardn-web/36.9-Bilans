"""
equilibre_data.py — Données cliniques Équilibre / Gériatrie
Tests : Tinetti, STS 1min, Équilibre unipodal, TUG, Berg, SPPB
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  TINETTI — Performance Oriented Mobility Assessment (POMA)
# ═══════════════════════════════════════════════════════════════════════════════

TINETTI_EQUILIBRE = [
    ("tin_eq_assis",    "Équilibre en position assise",
     [(0,"Penche ou glisse de la chaise"), (1,"Stable, sûr")]),
    ("tin_eq_lever",    "Lever de chaise",
     [(0,"Incapable sans aide"), (1,"Capable avec aide des bras"),
      (2,"Capable sans aide des bras")]),
    ("tin_eq_tentlever","Tentatives de lever",
     [(0,"Incapable sans aide"), (1,"Plus d'une tentative"),
      (2,"Une seule tentative")]),
    ("tin_eq_debout_5s","Équilibre debout (5 premières secondes)",
     [(0,"Instable (chancelle, bouge les pieds, balancement du tronc)"),
      (1,"Stable avec appui ou canne"), (2,"Stable sans appui")]),
    ("tin_eq_debout",   "Équilibre debout",
     [(0,"Instable"), (1,"Stable mais appui large ou canne"),
      (2,"Pieds joints, sans appui, stable")]),
    ("tin_eq_pousse",   "Équilibre lors d'une légère poussée sternale (3 fois)",
     [(0,"Commence à tomber"), (1,"Chancelle, s'agrippe, se stabilise"),
      (2,"Stable")]),
    ("tin_eq_yeuxferm", "Équilibre yeux fermés (pieds joints)",
     [(0,"Instable"), (1,"Stable")]),
    ("tin_eq_demi_tour","Demi-tour (360°)",
     [(0,"Pas discontinus ou instable"), (1,"Pas continus et instable"),
      (2,"Pas continus et stable")]),
    ("tin_eq_assis2",   "S'asseoir",
     [(0,"Instable, tombe dans la chaise"),
      (1,"Utilise les bras ou mouvement saccadé"),
      (2,"Sûr, mouvement fluide")]),
]

TINETTI_MARCHE = [
    ("tin_ma_init",     "Initiation de la marche",
     [(0,"Hésitation ou plusieurs tentatives"), (1,"Marche immédiate sans hésitation")]),
    ("tin_ma_long_r",   "Longueur de pas — pied droit",
     [(0,"Ne dépasse pas le pied gauche"),
      (1,"Dépasse le pied gauche")]),
    ("tin_ma_long_g",   "Longueur de pas — pied gauche",
     [(0,"Ne dépasse pas le pied droit"),
      (1,"Dépasse le pied droit")]),
    ("tin_ma_haut_r",   "Hauteur du pas — pied droit",
     [(0,"Pied traîné ou levé > 5 cm"),
      (1,"Pied levé proprement 1–5 cm")]),
    ("tin_ma_haut_g",   "Hauteur du pas — pied gauche",
     [(0,"Pied traîné ou levé > 5 cm"),
      (1,"Pied levé proprement 1–5 cm")]),
    ("tin_ma_symm",     "Symétrie du pas",
     [(0,"Longueur inégale"), (1,"Pas de longueur égale")]),
    ("tin_ma_cont",     "Continuité du pas",
     [(0,"Arrêts ou discontinuités"),
      (1,"Les pas semblent continus")]),
    ("tin_ma_ligne",    "Trajectoire (sur 3 m)",
     [(0,"Déviation marquée"),
      (1,"Légère déviation ou aide technique"),
      (2,"Droite, sans aide")]),
    ("tin_ma_tronc",    "Stabilité du tronc",
     [(0,"Balancement marqué ou utilise aide technique"),
      (1,"Pas de balancement, mais fléchit genou/dos ou écarte les bras"),
      (2,"Pas de balancement, pas de flexion, pas d'écart des bras")]),
    ("tin_ma_ecart",    "Écart des chevilles (base de sustentation)",
     [(0,"Talons écartés"), (1,"Talons presque joints en marchant")]),
]

TINETTI_EQ_KEYS   = [t[0] for t in TINETTI_EQUILIBRE]
TINETTI_MA_KEYS   = [t[0] for t in TINETTI_MARCHE]
TINETTI_ALL_KEYS  = TINETTI_EQ_KEYS + TINETTI_MA_KEYS
TINETTI_EQ_MAX    = sum(max(s for s,_ in t[2]) for t in TINETTI_EQUILIBRE)  # 16
TINETTI_MA_MAX    = sum(max(s for s,_ in t[2]) for t in TINETTI_MARCHE)     # 12


def compute_tinetti(answers: dict) -> dict:
    eq = sum(int(answers.get(k, -1)) for k in TINETTI_EQ_KEYS if answers.get(k, "") != "")
    ma = sum(int(answers.get(k, -1)) for k in TINETTI_MA_KEYS if answers.get(k, "") != "")
    eq_count = sum(1 for k in TINETTI_EQ_KEYS if str(answers.get(k,"")).strip() != "")
    ma_count = sum(1 for k in TINETTI_MA_KEYS if str(answers.get(k,"")).strip() != "")
    if eq_count == 0 and ma_count == 0:
        return {"eq": None, "ma": None, "total": None, "color": "#888", "interpretation": ""}
    total = (eq if eq_count else 0) + (ma if ma_count else 0)
    if total < 19:
        color, interp = "#d32f2f", "Risque élevé de chute (< 19)"
    elif total < 24:
        color, interp = "#f57c00", "Risque modéré de chute (19–23)"
    else:
        color, interp = "#388e3c", "Risque faible de chute (≥ 24)"
    return {"eq": eq if eq_count else None, "ma": ma if ma_count else None,
            "total": total, "color": color, "interpretation": interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  BERG BALANCE SCALE (14 items, 0–4)
# ═══════════════════════════════════════════════════════════════════════════════

BERG_ITEMS = [
    ("berg_1",  "1. Position assise à position debout",
     [(0,"Nécessite assistance modérée ou maximale"),
      (1,"Nécessite assistance minimale"),
      (2,"Capable après plusieurs essais"),
      (3,"Capable sans aide mais instable"),
      (4,"Capable sans aide, stable")]),
    ("berg_2",  "2. Station debout sans appui (2 min)",
     [(0,"Incapable de tenir 30 secondes sans aide"),
      (1,"Doit s'appuyer, peut tenir 30 secondes"),
      (2,"Capable de tenir 30 secondes"),
      (3,"Capable de tenir 2 minutes avec supervision"),
      (4,"Capable de tenir 2 minutes en sécurité")]),
    ("berg_3",  "3. Position assise sans dossier (2 min)",
     [(0,"Incapable sans support"),
      (1,"Peut tenir 10 secondes"),
      (2,"Peut tenir 30 secondes"),
      (3,"Peut tenir 2 minutes avec supervision"),
      (4,"Peut tenir 2 minutes en sécurité")]),
    ("berg_4",  "4. Position debout à position assise",
     [(0,"Nécessite aide pour s'asseoir"),
      (1,"S'assied de façon indépendante mais descente non contrôlée"),
      (2,"Utilise le dos des jambes contre la chaise pour contrôler"),
      (3,"Contrôle la descente à l'aide des mains"),
      (4,"S'assied de façon sécuritaire avec usage minimal des mains")]),
    ("berg_5",  "5. Transferts",
     [(0,"Nécessite deux personnes pour assistance/supervision"),
      (1,"Nécessite une personne"),
      (2,"Capable avec indications verbales ou supervision"),
      (3,"Capable mais nécessite utilisation des mains"),
      (4,"Capable en toute sécurité avec usage minimal des mains")]),
    ("berg_6",  "6. Station debout yeux fermés (10 sec)",
     [(0,"Nécessite aide pour ne pas tomber"),
      (1,"Incapable de garder les yeux fermés 3 secondes mais stable"),
      (2,"Peut tenir 3 secondes"),
      (3,"Peut tenir 10 secondes avec supervision"),
      (4,"Peut tenir 10 secondes en sécurité")]),
    ("berg_7",  "7. Station debout pieds joints",
     [(0,"Nécessite aide pour la position, incapable de tenir 15 sec"),
      (1,"Nécessite aide pour la position, peut tenir 15 secondes"),
      (2,"Peut tenir 30 secondes mais pas 1 minute"),
      (3,"Peut tenir 1 minute avec supervision"),
      (4,"Peut tenir 1 minute en sécurité")]),
    ("berg_8",  "8. Atteindre vers l'avant, bras tendu",
     [(0,"Perd l'équilibre ou nécessite support externe"),
      (1,"Atteint vers l'avant mais nécessite supervision"),
      (2,"Peut atteindre > 5 cm en sécurité"),
      (3,"Peut atteindre > 12 cm en sécurité"),
      (4,"Peut atteindre > 25 cm en sécurité")]),
    ("berg_9",  "9. Ramasser un objet au sol depuis la position debout",
     [(0,"Incapable ou nécessite aide pour maintenir l'équilibre"),
      (1,"Incapable de ramasser, s'approche à 2,5–5 cm avec supervision"),
      (2,"Incapable mais peut s'approcher 2,5 cm en toute sécurité"),
      (3,"Peut ramasser l'objet avec supervision"),
      (4,"Peut ramasser l'objet en sécurité")]),
    ("berg_10", "10. Se retourner pour regarder derrière (gauche et droite)",
     [(0,"Nécessite aide pour ne pas perdre l'équilibre"),
      (1,"Nécessite supervision lors du mouvement"),
      (2,"Effectue la rotation vers le côté mais perd l'équilibre"),
      (3,"Regarde derrière d'un côté seulement"),
      (4,"Regarde derrière des deux côtés, bon transfert de poids")]),
    ("berg_11", "11. Rotation de 360°",
     [(0,"Nécessite assistance lors de la rotation"),
      (1,"Nécessite supervision"),
      (2,"Capable mais lentement (> 4 secondes par direction)"),
      (3,"Capable en toute sécurité d'un côté en ≤ 4 secondes"),
      (4,"Capable en toute sécurité dans les deux directions en ≤ 4 secondes")]),
    ("berg_12", "12. Poser les pieds alternativement sur un tabouret",
     [(0,"Nécessite aide pour ne pas tomber"),
      (1,"Peut compléter > 2 touches avec peu d'aide"),
      (2,"Peut compléter 4 touches avec supervision"),
      (3,"Peut compléter 8 touches sans aide avec supervision"),
      (4,"Peut compléter 8 touches de façon indépendante en ≤ 20 secondes")]),
    ("berg_13", "13. Station debout, un pied en avant de l'autre (tandem)",
     [(0,"Perd l'équilibre lors du pas ou en restant debout"),
      (1,"Nécessite aide pour faire le pas mais peut tenir 15 secondes"),
      (2,"Peut faire un petit pas indépendamment et tenir 30 secondes"),
      (3,"Peut placer le pied en avant indépendamment et tenir 30 secondes"),
      (4,"Peut placer le pied en tandem et tenir 30 secondes")]),
    ("berg_14", "14. Station sur un pied",
     [(0,"Incapable ou nécessite aide pour ne pas tomber"),
      (1,"Essaie de lever le pied, incapable de tenir 3 secondes"),
      (2,"Peut lever le pied et tenir ≥ 3 secondes"),
      (3,"Peut lever le pied et tenir 5–10 secondes"),
      (4,"Peut lever le pied et tenir > 10 secondes")]),
]

BERG_KEYS = [b[0] for b in BERG_ITEMS]

def compute_berg(answers: dict) -> dict:
    vals = [int(answers[k]) for k in BERG_KEYS if str(answers.get(k,"")).strip() != ""]
    if not vals:
        return {"score": None, "color": "#888", "interpretation": ""}
    total = sum(vals)
    if total <= 20:
        color, interp = "#d32f2f", "Risque élevé de chute — fauteuil roulant recommandé (0–20)"
    elif total <= 40:
        color, interp = "#f57c00", "Risque modéré — marche avec aide (21–40)"
    else:
        color, interp = "#388e3c", "Risque faible — marche indépendante (41–56)"
    return {"score": total, "color": color, "interpretation": interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  SPPB — Short Physical Performance Battery
# ═══════════════════════════════════════════════════════════════════════════════

SPPB_BALANCE_OPTS = [
    (0, "Incapable de tenir 10 sec pieds joints (côte à côte)"),
    (1, "Pieds joints 10 sec mais pas semi-tandem 10 sec"),
    (2, "Semi-tandem 10 sec mais pas tandem 10 sec"),
    (3, "Tandem 10 sec mais < 3 sec"),
    (4, "Tandem ≥ 3 sec — 10 sec complet"),
]
SPPB_WALK_OPTS = [
    (0, "Incapable de marcher 4 mètres"),
    (1, "≥ 8.70 secondes"),
    (2, "6.21–8.70 secondes"),
    (3, "4.82–6.20 secondes"),
    (4, "< 4.82 secondes"),
]
SPPB_CHAIR_OPTS = [
    (0, "Incapable de compléter 5 levers"),
    (1, "≥ 16.70 secondes"),
    (2, "13.70–16.69 secondes"),
    (3, "11.20–13.69 secondes"),
    (4, "< 11.20 secondes"),
]

def compute_sppb(bal, walk, chair) -> dict:
    vals = [v for v in [bal, walk, chair] if v is not None]
    if not vals:
        return {"score": None, "color": "#888", "interpretation": ""}
    total = sum(vals)
    if total <= 6:
        color, interp = "#d32f2f", "Limitation sévère (0–6)"
    elif total <= 9:
        color, interp = "#f57c00", "Limitation modérée (7–9)"
    else:
        color, interp = "#388e3c", "Bonne mobilité (10–12)"
    return {"score": total, "color": color, "interpretation": interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  Google Sheets headers — Bilans_Equilibre
# ═══════════════════════════════════════════════════════════════════════════════

def get_equilibre_headers():
    h = ["bilan_id","patient_id","date_bilan","type_bilan","praticien","notes_generales"]
    # Tinetti équilibre
    h += TINETTI_EQ_KEYS + ["tinetti_eq_score"]
    # Tinetti marche
    h += TINETTI_MA_KEYS + ["tinetti_ma_score","tinetti_total","tinetti_interpretation"]
    # STS 1 min
    h += ["sts_1min_reps","sts_1min_interpretation"]
    # Équilibre unipodal
    h += ["unipodal_d_ouvert","unipodal_g_ouvert","unipodal_d_ferme","unipodal_g_ferme"]
    # TUG
    h += ["tug_temps","tug_aide","tug_interpretation"]
    # Berg
    h += BERG_KEYS + ["berg_score","berg_interpretation"]
    # SPPB
    h += ["sppb_balance","sppb_walk_time","sppb_walk_score",
          "sppb_chair_time","sppb_chair_score","sppb_score","sppb_interpretation"]
    return h
