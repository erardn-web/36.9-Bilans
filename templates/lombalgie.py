"""
templates/lombalgie.py — Template Lombalgie
"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.tests_cliniques.eva                      import EVA
from tests.tests_cliniques.drapeaux                 import Drapeaux
from tests.tests_cliniques.mobilite_lombaire        import MobiliteLombaire
from tests.tests_cliniques.luomajoki                import Luomajoki
from tests.tests_cliniques.tests_objectifs_lombaire import TestsObjectifsLombaire
from tests.tests_cliniques.classification_lombaire  import ClassificationLombaire
from tests.tests_cliniques.odi                      import ODI
from tests.tests_cliniques.tampa                    import Tampa
from tests.tests_cliniques.orebro                   import Orebro
from tests.tests_cliniques.testing_mi               import TestingMI
from tests.tests_cliniques.leg_press                import LegPress

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
