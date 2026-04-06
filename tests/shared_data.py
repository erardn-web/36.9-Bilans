"""
tests/tests_cliniques/shared_data.py
Données cliniques de tous les tests (SHV, Équilibre, BPCO, Lombalgie...)
"""

HAD_QUESTIONS = [
    ("a1","A","Je me sens tendu(e) ou énervé(e) :",
     [(3,"La plupart du temps"),(2,"Souvent"),(1,"De temps en temps"),(0,"Jamais")]),
    ("d1","D","Je prends toujours autant de plaisir aux mêmes choses qu'autrefois :",
     [(0,"Oui, tout autant"),(1,"Pas autant"),(2,"Un peu seulement"),(3,"Presque plus")]),
    ("a2","A","J'éprouve des sensations de peur comme si quelque chose d'horrible allait m'arriver :",
     [(3,"Oui, très nettement"),(2,"Oui, mais ce n'est pas trop grave"),
      (1,"Un peu, mais ça ne m'inquiète pas"),(0,"Pas du tout")]),
    ("d2","D","Je ris facilement et vois le bon côté des choses :",
     [(0,"Autant que par le passé"),(1,"Plus autant qu'avant"),
      (2,"Vraiment moins qu'avant"),(3,"Plus du tout")]),
    ("a3","A","Les idées se bousculent dans ma tête :",
     [(3,"La plupart du temps"),(2,"Assez souvent"),
      (1,"De temps en temps"),(0,"Très occasionnellement")]),
    ("d3","D","Je me sens de bonne humeur :",
     [(3,"Jamais"),(2,"Rarement"),(1,"Assez souvent"),(0,"La plupart du temps")]),
    ("a4","A","Je peux rester tranquillement assis(e) à ne rien faire et me sentir décontracté(e) :",
     [(0,"Oui, quoi qu'il arrive"),(1,"Oui, en général"),(2,"Rarement"),(3,"Jamais")]),
    ("d4","D","J'ai l'impression de fonctionner au ralenti :",
     [(3,"Presque toujours"),(2,"Très souvent"),(1,"Parfois"),(0,"Jamais")]),
    ("a5","A","J'éprouve des sensations de peur et j'ai l'estomac noué :",
     [(0,"Jamais"),(1,"Parfois"),(2,"Assez souvent"),(3,"Très souvent")]),
    ("d5","D","Je ne m'intéresse plus à mon apparence :",
     [(3,"Plus du tout"),(2,"Je n'y accorde pas autant d'attention que je devrais"),
      (1,"Il se peut que je n'y fasse pas autant attention"),
      (0,"J'y prête autant d'attention que par le passé")]),
    ("a6","A","Je me sens agité(e) comme si j'avais continuellement besoin de bouger :",
     [(3,"Vraiment très souvent"),(2,"Assez souvent"),(1,"Pas tellement"),(0,"Pas du tout")]),
    ("d6","D","Je me réjouis à l'avance à l'idée de faire certaines choses :",
     [(0,"Autant qu'avant"),(1,"Un peu moins qu'avant"),
      (2,"Bien moins qu'avant"),(3,"Presque jamais")]),
    ("a7","A","J'éprouve des sensations soudaines de panique :",
     [(3,"Vraiment très souvent"),(2,"Assez souvent"),(1,"Pas tellement"),(0,"Jamais du tout")]),
    ("d7","D","Je peux prendre plaisir à un bon livre ou à une bonne émission de radio ou de télévision :",
     [(0,"Souvent"),(1,"Parfois"),(2,"Rarement"),(3,"Très rarement")]),
]


def compute_had_scores(answers: dict) -> dict:
    score_a = sum(answers.get(f"a{i}", 0) for i in range(1, 8))
    score_d = sum(answers.get(f"d{i}", 0) for i in range(1, 8))
    def interp(s):
        if s <= 7:  return "Normal (0–7)"
        if s <= 10: return "Douteux (8–10)"
        return "Pathologique (11–21)"
    return {"score_anxiete": score_a, "score_depression": score_d,
            "interp_anxiete": interp(score_a), "interp_depression": interp(score_d)}


# ─── SF-12 ────────────────────────────────────────────────────────────────────

SF12_QUESTIONS = [
    {"key":"q1","dim":"GH","texte":"En général, diriez-vous que votre santé est :",
     "options":[(1,"Excellente"),(2,"Très bonne"),(3,"Bonne"),(4,"Passable"),(5,"Mauvaise")]},
    {"key":"q2a","dim":"PF",
     "texte":"Activités modérées (déplacer une table, passer l'aspirateur) — Votre état de santé vous limite-t-il ?",
     "options":[(1,"Oui, très limité(e)"),(2,"Oui, un peu limité(e)"),(3,"Non, pas du tout limité(e)")]},
    {"key":"q2b","dim":"PF",
     "texte":"Monter plusieurs étages par un escalier — Votre état de santé vous limite-t-il ?",
     "options":[(1,"Oui, très limité(e)"),(2,"Oui, un peu limité(e)"),(3,"Non, pas du tout limité(e)")]},
    {"key":"q3a","dim":"RP",
     "intro":"Au cours des 4 dernières semaines, avez-vous eu des problèmes dans votre travail en raison de votre état de santé PHYSIQUE ?",
     "texte":"Avez-vous accompli moins de choses que vous le souhaitiez ?",
     "options":[(1,"Oui"),(2,"Non")]},
    {"key":"q3b","dim":"RP","texte":"Avez-vous été limité(e) dans certaines activités ?",
     "options":[(1,"Oui"),(2,"Non")]},
    {"key":"q4a","dim":"RE",
     "intro":"Au cours des 4 dernières semaines, avez-vous eu des problèmes en raison de problèmes ÉMOTIONNELS ?",
     "texte":"Avez-vous accompli moins de choses que vous le souhaitiez ?",
     "options":[(1,"Oui"),(2,"Non")]},
    {"key":"q4b","dim":"RE",
     "texte":"Avez-vous fait ce travail avec moins de soin que d'habitude ?",
     "options":[(1,"Oui"),(2,"Non")]},
    {"key":"q5","dim":"BP",
     "texte":"Au cours des 4 dernières semaines, dans quelle mesure la douleur a-t-elle gêné votre travail habituel ?",
     "options":[(1,"Pas du tout"),(2,"Un petit peu"),(3,"Modérément"),(4,"Beaucoup"),(5,"Énormément")]},
    {"key":"q6a","dim":"MH",
     "intro":"Ces questions portent sur ce que vous avez ressenti au cours des 4 dernières semaines.",
     "texte":"Vous êtes-vous senti(e) calme et détendu(e) ?",
     "options":[(1,"Tout le temps"),(2,"La plupart du temps"),(3,"Souvent"),
                (4,"Quelquefois"),(5,"Rarement"),(6,"Jamais")]},
    {"key":"q6b","dim":"VT","texte":"Avez-vous eu beaucoup d'énergie ?",
     "options":[(1,"Tout le temps"),(2,"La plupart du temps"),(3,"Souvent"),
                (4,"Quelquefois"),(5,"Rarement"),(6,"Jamais")]},
    {"key":"q6c","dim":"MH","texte":"Vous êtes-vous senti(e) abattu(e) et triste ?",
     "options":[(1,"Tout le temps"),(2,"La plupart du temps"),(3,"Souvent"),
                (4,"Quelquefois"),(5,"Rarement"),(6,"Jamais")]},
    {"key":"q7","dim":"SF",
     "texte":"Dans quelle mesure votre état de santé ou vos problèmes émotionnels ont-ils gêné vos activités sociales ?",
     "options":[(1,"Tout le temps"),(2,"La plupart du temps"),(3,"Quelquefois"),
                (4,"Rarement"),(5,"Jamais")]},
]
SF12_KEYS = [q["key"] for q in SF12_QUESTIONS]
SF12_DIMENSIONS = {
    "pf":"Fonctionnement physique","rp":"Limitations physiques",
    "bp":"Douleur physique","gh":"Santé générale","vt":"Vitalité",
    "sf":"Vie sociale","re":"Limitations émotionnelles","mh":"Santé psychique",
    "pcs":"Score composite physique (PCS-12)","mcs":"Score composite mental (MCS-12)",
}


def _recode_sf12(key, val):
    if val is None or val == "": return None
    v = int(val)
    maps = {
        "q1": {1:100,2:75,3:50,4:25,5:0},
        "q2a":{1:0,2:50,3:100},"q2b":{1:0,2:50,3:100},
        "q3a":{1:0,2:100},"q3b":{1:0,2:100},
        "q4a":{1:0,2:100},"q4b":{1:0,2:100},
        "q5": {1:100,2:75,3:50,4:25,5:0},
        "q6a":{1:100,2:80,3:60,4:40,5:20,6:0},
        "q6b":{1:100,2:80,3:60,4:40,5:20,6:0},
        "q6c":{1:0,2:20,3:40,4:60,5:80,6:100},
        "q7": {1:0,2:25,3:50,4:75,5:100},
    }
    return maps.get(key, {}).get(v)


def _mean(vals):
    v = [x for x in vals if x is not None]
    return round(sum(v)/len(v)) if v else None


def compute_sf12_scores(answers: dict) -> dict:
    r   = {k: _recode_sf12(k, v) for k, v in answers.items()}
    pf  = _mean([r.get("q2a"), r.get("q2b")])
    rp  = _mean([r.get("q3a"), r.get("q3b")])
    bp  = r.get("q5"); gh = r.get("q1"); vt = r.get("q6b")
    sf  = r.get("q7"); re = _mean([r.get("q4a"), r.get("q4b")])
    mh  = _mean([r.get("q6a"), r.get("q6c")])
    def z(score, mean, sd):
        return (score-mean)/sd if score is not None else 0
    ref = {"pf":(81.18,29.10),"rp":(80.52,34.50),"bp":(75.49,23.56),
           "gh":(72.21,20.16),"vt":(61.05,20.86),"sf":(83.59,22.37),
           "re":(86.41,30.09),"mh":(74.74,18.05)}
    scores_dim = {"pf":pf,"rp":rp,"bp":bp,"gh":gh,"vt":vt,"sf":sf,"re":re,"mh":mh}
    zs = {k: z(v,ref[k][0],ref[k][1]) for k,v in scores_dim.items() if v is not None}
    pcs_coef = {"pf":0.42402,"rp":0.35119,"bp":0.31754,"gh":0.24954,
                "vt":0.02877,"sf":-0.00753,"re":-0.19206,"mh":-0.22069}
    mcs_coef = {"pf":-0.22999,"rp":-0.12329,"bp":-0.09731,"gh":-0.01571,
                "vt":0.23534,"sf":0.26876,"re":0.43407,"mh":0.48581}
    pcs_raw = sum(zs.get(k,0)*v for k,v in pcs_coef.items())
    mcs_raw = sum(zs.get(k,0)*v for k,v in mcs_coef.items())
    pcs = round(pcs_raw*10+50, 1) if zs else None
    mcs = round(mcs_raw*10+50, 1) if zs else None
    return {"pf":pf,"rp":rp,"bp":bp,"gh":gh,"vt":vt,"sf":sf,"re":re,"mh":mh,"pcs":pcs,"mcs":mcs}


def interpret_pcs_mcs(score) -> str:
    if score is None: return "—"
    if score >= 55:   return "Au-dessus de la moyenne"
    if score >= 45:   return "Dans la moyenne (45–55)"
    if score >= 35:   return "En-dessous de la moyenne"
    return "Très en-dessous de la moyenne (< 35)"


# ─── BOLT ────────────────────────────────────────────────────────────────────

BOLT_DESCRIPTION = """
**Protocole :**
1. Le patient respire normalement pendant 1 à 2 minutes.
2. Après une **expiration normale** (pas forcée), le patient bloque sa respiration.
3. Chronométrer jusqu'aux **premières envies nettes de respirer**.
4. Relâcher et noter le temps en secondes.

> ⚠️ Il ne s'agit pas de résister le plus longtemps possible, mais de noter la **première envie** de respirer.
"""

def interpret_bolt(seconds: int) -> dict:
    if seconds is None: return {}
    if seconds < 10:  return {"cat":"Très altéré","color":"#d32f2f",
                               "desc":"Dysfonction respiratoire sévère, tolérance au CO₂ très basse."}
    if seconds < 20:  return {"cat":"Altéré","color":"#f57c00",
                               "desc":"Contrôle respiratoire altéré, possible SHV significatif."}
    if seconds < 40:  return {"cat":"Moyen","color":"#fbc02d",
                               "desc":"Tolérance au CO₂ correcte mais améliorable."}
    return {"cat":"Bon","color":"#388e3c","desc":"Bonne tolérance au CO₂, contrôle respiratoire satisfaisant."}


# ─── HVT ─────────────────────────────────────────────────────────────────────

HVT_DESCRIPTION = """
**Protocole :**
1. Expliquer au patient qu'il va volontairement respirer plus profondément et plus vite pendant **3 minutes**.
2. Lui demander de noter les symptômes qui apparaissent pendant le test.
3. Après le test, noter le **temps de retour à la normale**.
4. Le test est **positif** si les symptômes reproduits correspondent aux plaintes habituelles.

> ⚠️ Contre-indications : épilepsie, grossesse, cardiopathie sévère, AVC récent.
"""

HVT_SYMPTOMES = [
    "Vertiges / étourdissements","Céphalées","Vision trouble / flou visuel",
    "Fourmillements des extrémités (mains, pieds)","Fourmillements péribuccaux",
    "Engourdissements","Spasmes musculaires / tétanie","Essoufflement",
    "Douleur / oppression thoracique","Palpitations","Sensation de manque d'air",
    "Anxiété","Sentiment de panique","Dépersonnalisation",
    "Nausées","Fatigue / épuisement soudain","Bouche sèche","Bâillements répétés",
]

HVT_PHASES = [
    ("repos", "🟦 Repos",        [0,1,2,3]),
    ("hv",    "🔴 HV",           [1,2,3]),
    ("rec",   "🟩 Récupération", [1,2,3,4,5]),
]
HVT_PARAMS = [
    ("petco2","PetCO₂ (mmHg)", 0.0, 80.0, 0.5),
    ("fr",    "FR (cyc/min)",  0.0, 60.0, 1.0),
    ("spo2",  "SpO₂ (%)",      0.0,100.0, 0.5),
    ("fc",    "FC (bpm)",      0.0,220.0, 1.0),
]


# ─── Nijmegen ─────────────────────────────────────────────────────────────────

NIJMEGEN_ITEMS = [
    "Douleurs dans la poitrine","Sensation de tension","Vision trouble",
    "Étourdissements","Confusion ou perte de contact avec l'environnement",
    "Mains et/ou pieds froids","Fourmillements dans les mains et/ou les pieds",
    "Bouche sèche","Fourmillements autour de la bouche",
    "Rigidité dans les mains et/ou les pieds","Palpitations","Anxiété",
    "Respiration rapide","Respiration difficile","Sensation d'étouffement",
    "Ballonnements abdominaux",
]
NIJMEGEN_OPTIONS = [(0,"Jamais"),(1,"Rarement"),(2,"Parfois"),(3,"Souvent"),(4,"Très souvent")]
NIJMEGEN_KEYS    = [f"nij_{i+1}" for i in range(16)]


def compute_nijmegen(answers: dict) -> dict:
    total = sum(int(answers.get(k,0) or 0) for k in NIJMEGEN_KEYS)
    if total >= 23:   return {"score":total,"interpretation":"Positif — SHV probable (≥ 23)","color":"#d32f2f"}
    if total >= 15:   return {"score":total,"interpretation":"Borderline (15–22) — à surveiller","color":"#f57c00"}
    return {"score":total,"interpretation":"Négatif — SHV peu probable (< 15)","color":"#388e3c"}


# ─── Gazométrie ───────────────────────────────────────────────────────────────

GAZO_FIELDS = [
    ("gazo_ph",    "pH",              "7.35–7.45"),
    ("gazo_paco2", "PaCO₂ (mmHg)",   "35–45"),
    ("gazo_pao2",  "PaO₂ (mmHg)",    "75–100"),
    ("gazo_hco3",  "HCO₃⁻ (mmol/L)", "22–26"),
    ("gazo_sato2", "SatO₂ (%)",       "≥ 95"),
    ("gazo_fio2",  "FiO₂ (%)",        "21 air ambiant"),
]

def interpret_gazo(key, val):
    try: v = float(val)
    except (TypeError,ValueError): return None, ""
    ranges = {
        "gazo_ph":   (7.35,7.45,"Acidose","Alcalose"),
        "gazo_paco2":(35,45,"Hypocapnie","Hypercapnie"),
        "gazo_pao2": (75,100,"Hypoxémie",None),
        "gazo_hco3": (22,26,"Bas","Élevé"),
        "gazo_sato2":(95,100,"Désaturation",None),
    }
    if key not in ranges: return None, ""
    lo,hi,low_label,high_label = ranges[key]
    if v < lo:                    return False, f"⬇ {low_label} ({v})"
    if high_label and v > hi:     return False, f"⬆ {high_label} ({v})"
    return True, f"✓ Normal ({v})"


ETCO2_PATTERNS = [
    "Normal","Hypocapnie (ETCO₂ < 35 mmHg)","Hypocapnie sévère (ETCO₂ < 30 mmHg)",
    "Hypercapnie (ETCO₂ > 45 mmHg)","Pattern irrégulier","Non réalisé",
]


# ─── Pattern respiratoire ─────────────────────────────────────────────────────

PATTERN_MODES      = ["Diaphragmatique (normal)","Thoracique supérieur","Mixte","Paradoxal"]
PATTERN_AMPLITUDES = ["Normale","Superficielle","Profonde","Irrégulière"]
PATTERN_RYTHMES    = ["Régulier","Irrégulier","Avec apnées","Avec soupirs fréquents","Avec blocages"]


# ─── SNIF / PImax / PEmax ────────────────────────────────────────────────────

def interpret_mip_mep(val, predicted):
    try:
        pct = abs(float(val)) / abs(float(predicted)) * 100
        if pct >= 80: return pct, "Normal (≥ 80%)", "#388e3c"
        if pct >= 60: return pct, "Légèrement diminué (60–79%)", "#f57c00"
        return pct, "Diminué (< 60%)", "#d32f2f"
    except (TypeError, ValueError, ZeroDivisionError):
        return None, "—", "#888"


# ─── MRC Dyspnée ─────────────────────────────────────────────────────────────

MRC_GRADES = [
    (0,"Grade 0 — Pas de dyspnée sauf en cas d'exercice intense"),
    (1,"Grade 1 — Dyspnée lors d'une montée rapide ou d'une côte légère"),
    (2,"Grade 2 — Marche plus lentement que les personnes du même âge à plat, ou s'arrête à son propre rythme"),
    (3,"Grade 3 — S'arrête après 100 m ou quelques minutes à plat"),
    (4,"Grade 4 — Trop essoufflé(e) pour quitter la maison, ou essoufflé(e) en s'habillant/déshabillant"),
]


# ─── Comorbidités ────────────────────────────────────────────────────────────

COMORB_CATEGORIES = {
    "🫁 Respiratoires": [
        "Asthme","BPCO","Emphysème","Bronchectasies",
        "Rhinite / sinusite chronique","Apnées du sommeil (SAOS)","Fibrose pulmonaire",
    ],
    "❤️ Cardio-vasculaires": [
        "Insuffisance cardiaque","Hypertension artérielle","Arythmie / tachycardie",
        "Cardiopathie ischémique","Embolie pulmonaire (antécédent)",
    ],
    "🧠 Neurologiques / Psychiatriques": [
        "Trouble anxieux généralisé","Trouble panique","Dépression",
        "Stress post-traumatique","Épilepsie","Sclérose en plaques",
    ],
    "🦴 Musculo-squelettiques": [
        "Scoliose / cyphose","Douleurs chroniques","Fibromyalgie","Déformation thoracique",
    ],
    "⚗️ Métaboliques / Endocrines": [
        "Diabète","Dysthyroïdie","Anémie","Reflux gastro-œsophagien (RGO)","Grossesse",
    ],
    "💊 Traitements en cours": [
        "Bronchodilatateurs","Corticoïdes inhalés","Anxiolytiques / benzodiazépines",
        "Antidépresseurs","Bêtabloquants","Diurétiques",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  ÉQUILIBRE / GÉRIATRIE
# ═══════════════════════════════════════════════════════════════════════════════

TINETTI_EQUILIBRE = [
    ("tin_eq_assis",    "Équilibre en position assise",
     [(0,"Penche ou glisse de la chaise"), (1,"Stable, sûr")]),
    ("tin_eq_lever",    "Lever de chaise",
     [(0,"Incapable sans aide"), (1,"Capable avec aide des bras"), (2,"Capable sans aide des bras")]),
    ("tin_eq_tentlever","Tentatives de lever",
     [(0,"Incapable sans aide"), (1,"Plus d'une tentative"), (2,"Une seule tentative")]),
    ("tin_eq_debout_5s","Équilibre debout (5 premières secondes)",
     [(0,"Instable (chancelle, bouge les pieds, balancement du tronc)"),
      (1,"Stable avec appui ou canne"), (2,"Stable sans appui")]),
    ("tin_eq_debout",   "Équilibre debout",
     [(0,"Instable"), (1,"Stable mais appui large ou canne"), (2,"Pieds joints, sans appui, stable")]),
    ("tin_eq_pousse",   "Équilibre lors d'une légère poussée sternale (3 fois)",
     [(0,"Commence à tomber"), (1,"Chancelle, s'agrippe, se stabilise"), (2,"Stable")]),
    ("tin_eq_yeuxferm", "Équilibre yeux fermés (pieds joints)",
     [(0,"Instable"), (1,"Stable")]),
    ("tin_eq_demi_tour","Demi-tour (360°)",
     [(0,"Pas discontinus ou instable"), (1,"Pas continus et instable"), (2,"Pas continus et stable")]),
    ("tin_eq_assis2",   "S'asseoir",
     [(0,"Instable, tombe dans la chaise"), (1,"Utilise les bras ou mouvement saccadé"), (2,"Sûr, mouvement fluide")]),
]
TINETTI_MARCHE = [
    ("tin_ma_init",    "Initiation de la marche",
     [(0,"Hésitation ou plusieurs tentatives"), (1,"Marche immédiate sans hésitation")]),
    ("tin_ma_long_r",  "Longueur de pas — pied droit",
     [(0,"Ne dépasse pas le pied gauche"), (1,"Dépasse le pied gauche")]),
    ("tin_ma_long_g",  "Longueur de pas — pied gauche",
     [(0,"Ne dépasse pas le pied droit"), (1,"Dépasse le pied droit")]),
    ("tin_ma_haut_r",  "Hauteur du pas — pied droit",
     [(0,"Pied traîné ou levé > 5 cm"), (1,"Pied levé proprement 1–5 cm")]),
    ("tin_ma_haut_g",  "Hauteur du pas — pied gauche",
     [(0,"Pied traîné ou levé > 5 cm"), (1,"Pied levé proprement 1–5 cm")]),
    ("tin_ma_symm",    "Symétrie du pas",
     [(0,"Longueur inégale"), (1,"Pas de longueur égale")]),
    ("tin_ma_cont",    "Continuité du pas",
     [(0,"Arrêts ou discontinuités"), (1,"Les pas semblent continus")]),
    ("tin_ma_ligne",   "Trajectoire (sur 3 m)",
     [(0,"Déviation marquée"), (1,"Légère déviation ou aide technique"), (2,"Droite, sans aide")]),
    ("tin_ma_tronc",   "Stabilité du tronc",
     [(0,"Balancement marqué ou utilise aide technique"),
      (1,"Pas de balancement, mais fléchit genou/dos ou écarte les bras"),
      (2,"Pas de balancement, pas de flexion, pas d'écart des bras")]),
    ("tin_ma_ecart",   "Écart des chevilles (base de sustentation)",
     [(0,"Talons écartés"), (1,"Talons presque joints en marchant")]),
]
TINETTI_EQ_KEYS  = [t[0] for t in TINETTI_EQUILIBRE]
TINETTI_MA_KEYS  = [t[0] for t in TINETTI_MARCHE]
TINETTI_ALL_KEYS = TINETTI_EQ_KEYS + TINETTI_MA_KEYS
TINETTI_EQ_MAX   = sum(max(s for s,_ in t[2]) for t in TINETTI_EQUILIBRE)
TINETTI_MA_MAX   = sum(max(s for s,_ in t[2]) for t in TINETTI_MARCHE)


def compute_tinetti(answers: dict) -> dict:
    eq = sum(int(answers.get(k,-1)) for k in TINETTI_EQ_KEYS if answers.get(k,"") != "")
    ma = sum(int(answers.get(k,-1)) for k in TINETTI_MA_KEYS if answers.get(k,"") != "")
    eq_count = sum(1 for k in TINETTI_EQ_KEYS if str(answers.get(k,"")).strip() != "")
    ma_count = sum(1 for k in TINETTI_MA_KEYS if str(answers.get(k,"")).strip() != "")
    if eq_count == 0 and ma_count == 0:
        return {"eq":None,"ma":None,"total":None,"color":"#888","interpretation":""}
    total = (eq if eq_count else 0) + (ma if ma_count else 0)
    if total < 19:   color,interp = "#d32f2f","Risque élevé de chute (< 19)"
    elif total < 24: color,interp = "#f57c00","Risque modéré de chute (19–23)"
    else:            color,interp = "#388e3c","Risque faible de chute (≥ 24)"
    return {"eq":eq if eq_count else None,"ma":ma if ma_count else None,
            "total":total,"color":color,"interpretation":interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  BERG BALANCE SCALE
# ═══════════════════════════════════════════════════════════════════════════════

BERG_ITEMS = [
    ("berg_1","1. Position assise à position debout",
     [(0,"Nécessite assistance modérée ou maximale"),(1,"Nécessite assistance minimale"),
      (2,"Capable après plusieurs essais"),(3,"Capable sans aide mais instable"),(4,"Capable sans aide, stable")]),
    ("berg_2","2. Station debout sans appui (2 min)",
     [(0,"Incapable de tenir 30 secondes sans aide"),(1,"Doit s'appuyer, peut tenir 30 secondes"),
      (2,"Capable de tenir 30 secondes"),(3,"Capable de tenir 2 minutes avec supervision"),(4,"Capable de tenir 2 minutes en sécurité")]),
    ("berg_3","3. Position assise sans dossier (2 min)",
     [(0,"Incapable sans support"),(1,"Peut tenir 10 secondes"),(2,"Peut tenir 30 secondes"),
      (3,"Peut tenir 2 minutes avec supervision"),(4,"Peut tenir 2 minutes en sécurité")]),
    ("berg_4","4. Position debout à position assise",
     [(0,"Nécessite aide pour s'asseoir"),(1,"S'assied de façon indépendante mais descente non contrôlée"),
      (2,"Utilise le dos des jambes contre la chaise pour contrôler"),
      (3,"Contrôle la descente à l'aide des mains"),(4,"S'assied de façon sécuritaire avec usage minimal des mains")]),
    ("berg_5","5. Transferts",
     [(0,"Nécessite deux personnes"),(1,"Nécessite une personne"),
      (2,"Capable avec indications verbales"),(3,"Capable mais nécessite utilisation des mains"),
      (4,"Capable en toute sécurité avec usage minimal des mains")]),
    ("berg_6","6. Station debout yeux fermés (10 sec)",
     [(0,"Nécessite aide pour ne pas tomber"),(1,"Incapable de garder les yeux fermés 3 secondes mais stable"),
      (2,"Peut tenir 3 secondes"),(3,"Peut tenir 10 secondes avec supervision"),(4,"Peut tenir 10 secondes en sécurité")]),
    ("berg_7","7. Station debout pieds joints",
     [(0,"Nécessite aide, incapable de tenir 15 sec"),(1,"Nécessite aide, peut tenir 15 secondes"),
      (2,"Peut tenir 30 secondes mais pas 1 minute"),(3,"Peut tenir 1 minute avec supervision"),
      (4,"Peut tenir 1 minute en sécurité")]),
    ("berg_8","8. Atteindre vers l'avant, bras tendu",
     [(0,"Perd l'équilibre ou nécessite support"),(1,"Atteint mais nécessite supervision"),
      (2,"Peut atteindre > 5 cm"),(3,"Peut atteindre > 12 cm"),(4,"Peut atteindre > 25 cm")]),
    ("berg_9","9. Ramasser un objet au sol",
     [(0,"Incapable ou nécessite aide"),(1,"Incapable, s'approche 2,5–5 cm avec supervision"),
      (2,"Incapable mais s'approche 2,5 cm en sécurité"),(3,"Peut ramasser avec supervision"),
      (4,"Peut ramasser en sécurité")]),
    ("berg_10","10. Se retourner pour regarder derrière",
     [(0,"Nécessite aide"),(1,"Nécessite supervision"),(2,"Effectue la rotation mais perd l'équilibre"),
      (3,"Regarde derrière d'un côté seulement"),(4,"Regarde derrière des deux côtés")]),
    ("berg_11","11. Rotation de 360°",
     [(0,"Nécessite assistance"),(1,"Nécessite supervision"),(2,"Capable mais lentement (> 4 sec)"),
      (3,"Capable d'un côté en ≤ 4 secondes"),(4,"Capable dans les deux directions en ≤ 4 secondes")]),
    ("berg_12","12. Poser les pieds alternativement sur un tabouret",
     [(0,"Nécessite aide"),(1,"Peut compléter > 2 touches avec peu d'aide"),
      (2,"Peut compléter 4 touches avec supervision"),(3,"Peut compléter 8 touches sans aide avec supervision"),
      (4,"Peut compléter 8 touches en ≤ 20 secondes")]),
    ("berg_13","13. Station debout un pied en avant (tandem)",
     [(0,"Perd l'équilibre lors du pas"),(1,"Nécessite aide mais peut tenir 15 secondes"),
      (2,"Peut faire un petit pas et tenir 30 secondes"),(3,"Peut placer le pied en avant et tenir 30 secondes"),
      (4,"Peut placer en tandem et tenir 30 secondes")]),
    ("berg_14","14. Station sur un pied",
     [(0,"Incapable ou nécessite aide"),(1,"Essaie de lever le pied, < 3 secondes"),
      (2,"Peut lever le pied et tenir ≥ 3 secondes"),(3,"Peut tenir 5–10 secondes"),
      (4,"Peut tenir > 10 secondes")]),
]
BERG_KEYS = [b[0] for b in BERG_ITEMS]


def compute_berg(answers: dict) -> dict:
    vals = [int(answers[k]) for k in BERG_KEYS if str(answers.get(k,"")).strip() != ""]
    if not vals: return {"score":None,"color":"#888","interpretation":""}
    total = sum(vals)
    if total <= 20:   color,interp = "#d32f2f","Risque élevé de chute — fauteuil roulant recommandé (0–20)"
    elif total <= 40: color,interp = "#f57c00","Risque modéré — marche avec aide (21–40)"
    else:             color,interp = "#388e3c","Risque faible — marche indépendante (41–56)"
    return {"score":total,"color":color,"interpretation":interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  SPPB
# ═══════════════════════════════════════════════════════════════════════════════

SPPB_BALANCE_OPTS = [
    (0,"Incapable de tenir 10 sec pieds joints"),(1,"Pieds joints 10 sec mais pas semi-tandem 10 sec"),
    (2,"Semi-tandem 10 sec mais pas tandem 10 sec"),(3,"Tandem 10 sec mais < 3 sec"),
    (4,"Tandem ≥ 3 sec — 10 sec complet"),
]
SPPB_WALK_OPTS = [
    (0,"Incapable de marcher 4 mètres"),(1,"≥ 8.70 secondes"),(2,"6.21–8.70 secondes"),
    (3,"4.82–6.20 secondes"),(4,"< 4.82 secondes"),
]
SPPB_CHAIR_OPTS = [
    (0,"Incapable de compléter 5 levers"),(1,"≥ 16.70 secondes"),(2,"13.70–16.69 secondes"),
    (3,"11.20–13.69 secondes"),(4,"< 11.20 secondes"),
]

def compute_sppb(bal, walk, chair) -> dict:
    vals = [v for v in [bal,walk,chair] if v is not None]
    if not vals: return {"score":None,"color":"#888","interpretation":""}
    total = sum(vals)
    if total <= 6:   color,interp = "#d32f2f","Limitation sévère (0–6)"
    elif total <= 9: color,interp = "#f57c00","Limitation modérée (7–9)"
    else:            color,interp = "#388e3c","Bonne mobilité (10–12)"
    return {"score":total,"color":color,"interpretation":interp}


# ═══════════════════════════════════════════════════════════════════════════════
#  6MWT
# ═══════════════════════════════════════════════════════════════════════════════

def interpret_6mwt(distance: float) -> dict:
    if distance is None: return {"color":"#888","interpretation":""}
    if distance >= 400:   color,interp = "#388e3c","Bonne capacité fonctionnelle (≥ 400 m)"
    elif distance >= 300: color,interp = "#f57c00","Capacité modérée (300–399 m)"
    elif distance >= 150: color,interp = "#e64a19","Capacité limitée (150–299 m)"
    else:                 color,interp = "#d32f2f","Capacité très limitée (< 150 m)"
    return {"color":color,"interpretation":interp}
