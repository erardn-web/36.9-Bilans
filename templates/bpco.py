"""
templates/bpco.py — Template BPCO
"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.tests_cliniques.spirometrie  import Spirometrie
from tests.tests_cliniques.six_mwt      import SixMWT
from tests.tests_cliniques.sts          import STS
from tests.tests_cliniques.mmrc         import MMRC
from tests.tests_cliniques.cat          import CAT
from tests.tests_cliniques.bode         import BODE
from tests.tests_cliniques.testing_mi   import TestingMI
from tests.tests_cliniques.leg_press    import LegPress

BPCO = register_template(BilanTemplate(
    template_id = "bpco",
    nom         = "BPCO",
    icone       = "🫁",
    description = "Bilan BPCO / pathologie respiratoire chronique",
    tests       = [Spirometrie, SixMWT, STS, MMRC, CAT, BODE, TestingMI, LegPress],
))
