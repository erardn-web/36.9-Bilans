"""
templates/bpco.py — Template BPCO
"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.spirometrie  import Spirometrie
from tests.six_mwt      import SixMWT
from tests.sts          import STS
from tests.mmrc         import MMRC
from tests.cat          import CAT
from tests.bode         import BODE
from tests.testing_mi   import TestingMI
from tests.leg_press    import LegPress

BPCO = register_template(BilanTemplate(
    template_id = "bpco",
    nom         = "BPCO",
    icone       = "🫁",
    description = "Bilan BPCO / pathologie respiratoire chronique",
    tests       = [Spirometrie, SixMWT, STS, MMRC, CAT, BODE, TestingMI, LegPress],
))
