"""templates/genou.py — Template Genou post-chirurgical (LCA, PTG)"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.nrs       import NRS
from tests.koos       import KOOS
from tests.lysholm    import Lysholm
from tests.psfs       import PSFS
from tests.groc       import GROC
from tests.tug       import TUG
from tests.sts       import STS
from tests.unipodal  import Unipodal

from tests.testing_global import TestingGlobal

GENOU = register_template(BilanTemplate(
    template_id = "genou",
    nom         = "Genou post-chirurgical",
    icone       = "🦵",
    description = "Bilan genou — LCA, PTG, ménisque — KOOS, Lysholm, testing musculaire",
    tests       = [
        NRS, KOOS, Lysholm, TestingGlobal,
        TUG, STS, Unipodal,
        PSFS, GROC,
    ],
))
