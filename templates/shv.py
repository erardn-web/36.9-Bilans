"""
templates/shv.py — Template Syndrome d'Hyperventilation
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.had            import HAD
from tests.sf12           import SF12
from tests.nijmegen       import Nijmegen
from tests.mrc_dyspnee    import MRCDyspnee
from tests.comorbidites   import Comorbidites
from tests.bolt              import BOLT
from tests.hvt               import HVT
from tests.gazometrie        import Gazometrie
from tests.pattern_respi     import PatternRespi
from tests.snif_pimax_pemax  import SNIFPimaxPemax
from tests.testing_mi        import TestingMI
from tests.leg_press         import LegPress

SHV = register_template(BilanTemplate(
    template_id = "shv",
    nom         = "Syndrome d'Hyperventilation",
    icone       = "🫁",
    description = "Bilan SHV complet",
    tests       = [
        HAD, SF12, BOLT, HVT, Nijmegen,
        Gazometrie, PatternRespi, SNIFPimaxPemax,
        MRCDyspnee, Comorbidites, TestingMI, LegPress,
    ],
))
