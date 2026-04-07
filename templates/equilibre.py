"""
templates/equilibre.py — Template Bilan d'Équilibre
"""
from core.bilan_template import BilanTemplate
from core.registry import register_template

from tests.mrc_dyspnee    import MRCDyspnee
from tests.tinetti       import Tinetti
from tests.berg          import Berg
from tests.tug           import TUG
from tests.sts           import STS
from tests.unipodal      import Unipodal
from tests.sppb          import SPPB
from tests.testing_mi    import TestingMI
from tests.leg_press     import LegPress

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
