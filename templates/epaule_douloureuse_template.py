"""templates/epaule_douloureuse.py — Template Épaule Douloureuse"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.tests_cliniques.eva                   import EVA
from tests.tests_cliniques.quick_dash            import QuickDASH
from tests.tests_cliniques.ases                  import ASES
from tests.tests_cliniques.amplitudes_epaule     import AmplitudesEpaule
from tests.tests_cliniques.testing_epaule        import TestingEpaule
from tests.tests_cliniques.tests_epaule_speciaux import TestsEpauleSpeciaux
from tests.tests_cliniques.classification_epaule import ClassificationEpaule
from tests.tests_cliniques.testing_mi            import TestingMI
from tests.tests_cliniques.leg_press             import LegPress

EPAULE_DOULOUREUSE = register_template(BilanTemplate(
    template_id = "epaule_douloureuse",
    nom         = "Épaule douloureuse",
    icone       = "🦾",
    description = "Bilan épaule douloureuse — EVA, QuickDASH, ASES, amplitudes, testing, tests spéciaux, classification",
    tests       = [
        EVA,
        QuickDASH,
        ASES,
        AmplitudesEpaule,
        TestingEpaule,
        TestsEpauleSpeciaux,
        ClassificationEpaule,
        TestingMI,
        LegPress,
    ],
))
