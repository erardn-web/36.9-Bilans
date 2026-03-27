"""
templates/shv.py — Template Syndrome d'Hyperventilation
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.questionnaires.had            import HAD
from tests.questionnaires.sf12           import SF12
from tests.questionnaires.nijmegen       import Nijmegen
from tests.questionnaires.mrc_dyspnee    import MRCDyspnee
from tests.questionnaires.comorbidites   import Comorbidites
from tests.tests_cliniques.bolt              import BOLT
from tests.tests_cliniques.hvt               import HVT
from tests.tests_cliniques.gazometrie        import Gazometrie
from tests.tests_cliniques.pattern_respi     import PatternRespi
from tests.tests_cliniques.snif_pimax_pemax  import SNIFPimaxPemax
from tests.tests_cliniques.testing_mi        import TestingMI
from tests.tests_cliniques.leg_press         import LegPress

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
