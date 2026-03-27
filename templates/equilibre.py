"""
templates/equilibre.py — Template Bilan d'Équilibre
"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.questionnaires.mrc_dyspnee    import MRCDyspnee
from tests.tests_cliniques.tinetti       import Tinetti
from tests.tests_cliniques.berg          import Berg
from tests.tests_cliniques.tug           import TUG
from tests.tests_cliniques.sts           import STS
from tests.tests_cliniques.unipodal      import Unipodal
from tests.tests_cliniques.sppb          import SPPB
from tests.tests_cliniques.testing_mi    import TestingMI
from tests.tests_cliniques.leg_press     import LegPress

EQUILIBRE = register_template(BilanTemplate(
    template_id = "equilibre",
    nom         = "Bilan d'Équilibre",
    icone       = "⚖️",
    description = "Équilibre, marche et mobilité fonctionnelle",
    tests       = [
        Tinetti, Berg, TUG, STS, Unipodal, SPPB,
        MRCDyspnee, TestingMI, LegPress,
    ],
))
