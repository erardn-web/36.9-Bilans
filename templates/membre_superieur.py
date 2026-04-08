"""templates/membre_superieur.py — Template Membre supérieur générique"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.nrs                    import NRS
from tests.dash                    import DASH
from tests.psfs                    import PSFS
from tests.groc                    import GROC
from tests.amplitudes_epaule      import AmplitudesEpaule
from tests.tests_epaule_speciaux  import TestsEpauleSpeciaux

from tests.testing_global import TestingGlobal

MEMBRE_SUP = register_template(BilanTemplate(
    template_id = "membre_superieur",
    nom         = "Membre supérieur",
    icone       = "💪",
    description = "Bilan membre supérieur — épaule, coude, poignet — DASH, amplitudes, testing",
    tests       = [
        NRS, AmplitudesEpaule, TestingGlobal, TestsEpauleSpeciaux,
        DASH, PSFS, GROC,
    ],
))
