"""templates/hanche.py — Template Hanche post-chirurgicale (PTH)"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.nrs       import NRS
from tests.hoos       import HOOS
from tests.psfs       import PSFS
from tests.groc       import GROC
from tests.tug       import TUG
from tests.sts       import STS
from tests.six_mwt   import SixMWT

from tests.testing_global import TestingGlobal

HANCHE = register_template(BilanTemplate(
    template_id = "hanche",
    nom         = "Hanche post-chirurgicale",
    icone       = "🦴",
    description = "Bilan hanche — PTH, fracture — HOOS, testing musculaire, 6MWT",
    tests       = [
        NRS, HOOS, TestingGlobal,
        TUG, STS, SixMWT,
        PSFS, GROC,
    ],
))
