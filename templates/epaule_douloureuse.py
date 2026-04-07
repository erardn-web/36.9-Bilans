"""templates/epaule_douloureuse.py — Template Épaule Douloureuse"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.eva                   import EVA
from tests.quick_dash            import QuickDASH
from tests.ases                  import ASES
from tests.amplitudes_epaule     import AmplitudesEpaule
from tests.testing_epaule        import TestingEpaule
from tests.tests_epaule_speciaux import TestsEpauleSpeciaux
from tests.classification_epaule import ClassificationEpaule
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
    ],
))
