"""templates/hanche.py — Template Hanche post-chirurgicale (PTH)"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.tests_cliniques.nrs       import NRS
from tests.questionnaires.hoos       import HOOS
from tests.questionnaires.psfs       import PSFS
from tests.questionnaires.groc       import GROC
from tests.tests_cliniques.tug       import TUG
from tests.tests_cliniques.sts       import STS
from tests.tests_cliniques.six_mwt   import SixMWT
from tests.tests_cliniques.testing_mi import TestingMI

HANCHE = register_template(BilanTemplate(
    template_id = "hanche",
    nom         = "Hanche post-chirurgicale",
    icone       = "🦴",
    description = "Bilan hanche — PTH, fracture — HOOS, testing musculaire, 6MWT",
    tests       = [
        NRS, HOOS, TestingMI,
        TUG, STS, SixMWT,
        PSFS, GROC,
    ],
))
