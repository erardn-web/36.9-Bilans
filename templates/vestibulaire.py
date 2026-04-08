"""templates/vestibulaire.py — Template Troubles Vestibulaires"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

# Outcome measures vestibulaires validés
from tests.dhi        import DHI          # Dizziness Handicap Inventory
from tests.hit6       import HIT6         # Impact céphalées / vertiges
from tests.abc_scale  import ABCScale     # Activities-specific Balance Confidence
from tests.fes_i      import FESI         # Falls Efficacy Scale

# Tests d'équilibre et de marche
from tests.mini_bestest import MiniBESTest # Mini-BESTest (recommandé vestibulaire)
from tests.tinetti    import Tinetti       # Équilibre + marche /28
from tests.berg       import Berg          # Berg Balance Scale /56
from tests.tug        import TUG          # Timed Up and Go
from tests.unipodal   import Unipodal     # Station unipodal
from tests.gait_speed import GaitSpeed4m  # Vitesse de marche 4m

# Psychologique et fonctionnel
from tests.had        import HAD           # Anxiété / dépression (fréquents)
from tests.psfs       import PSFS          # Objectifs fonctionnels spécifiques
from tests.groc       import GROC          # Changement global perçu

from tests.testing_global import TestingGlobal

VESTIBULAIRE = register_template(BilanTemplate(
    template_id = "vestibulaire",
    nom         = "Troubles vestibulaires",
    icone       = "🌀",
    description = (
        "Bilan physiothérapie vestibulaire — VPPB, névrite, labyrinthite, "
        "déhiscence, névrome. DHI, Mini-BESTest, ABC Scale, équilibre, marche."
    ),
    tests = [
        # 1. Outcome measures spécifiques vertiges
        DHI,
        HIT6,
        ABCScale,
        FESI,
        # 2. Équilibre statique et dynamique
        MiniBESTest,
        Berg,
        Tinetti,
        Unipodal,
        # 3. Mobilité fonctionnelle
        TUG,
        GaitSpeed4m,
        # 4. Psychologique (anxiété très fréquente en vestibulaire)
        HAD,
        # 5. Fonctionnel / suivi
        PSFS,
        GROC,
    ],
))
