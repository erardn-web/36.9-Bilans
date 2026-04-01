"""templates/genou.py — Template Genou post-chirurgical (LCA, PTG)"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.tests_cliniques.nrs       import NRS
from tests.questionnaires.koos       import KOOS
from tests.questionnaires.lysholm    import Lysholm
from tests.questionnaires.psfs       import PSFS
from tests.questionnaires.groc       import GROC
from tests.tests_cliniques.tug       import TUG
from tests.tests_cliniques.sts       import STS
from tests.tests_cliniques.unipodal  import Unipodal
from tests.tests_cliniques.testing_mi import TestingMI

GENOU = register_template(BilanTemplate(
    template_id = "genou",
    nom         = "Genou post-chirurgical",
    icone       = "🦵",
    description = "Bilan genou — LCA, PTG, ménisque — KOOS, Lysholm, testing musculaire",
    tests       = [
        NRS, KOOS, Lysholm, TestingMI,
        TUG, STS, Unipodal,
        PSFS, GROC,
    ],
))
