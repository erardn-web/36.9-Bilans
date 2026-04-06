"""
templates/lombalgie.py — Template Lombalgie
"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.eva                      import EVA
from tests.drapeaux                 import Drapeaux
from tests.mobilite_lombaire        import MobiliteLombaire
from tests.luomajoki                import Luomajoki
from tests.tests_objectifs_lombaire import TestsObjectifsLombaire
from tests.classification_lombaire  import ClassificationLombaire
from tests.odi                      import ODI
from tests.tampa                    import Tampa
from tests.orebro                   import Orebro
from tests.testing_mi               import TestingMI
from tests.leg_press                import LegPress

LOMBALGIE = register_template(BilanTemplate(
    template_id = "lombalgie",
    nom         = "Lombalgie",
    icone       = "🦴",
    description = "Bilan lombalgie complet — SOAP, classification SIN/ROM/EOR/MOM, ODI, Tampa, Örebro",
    tests       = [
        EVA, Drapeaux,
        MobiliteLombaire, Luomajoki, TestsObjectifsLombaire,
        ClassificationLombaire,
        ODI, Tampa, Orebro,
        TestingMI, LegPress,
    ],
))
