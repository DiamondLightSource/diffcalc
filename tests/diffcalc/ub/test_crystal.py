import unittest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.tools import assert_dict_almost_equal, mneq_
from diffcalc.ub.crystal import CrystalUnderTest
from tests.diffcalc import scenarios


class TestCrystalUnderTest(unittest.TestCase):

    def setUp(self):
        self.tclatt = []
        self.tcbmat = []

        # From the dif_init.mat next to dif_dos.exe on Vlieg's cd
        #self.tclatt.append([4.0004, 4.0004, 2.270000, 90, 90, 90])
        #self.tcbmat.append([[1.570639, 0, 0] ,[0.0, 1.570639, 0] ,
        #                    [0.0, 0.0, 2.767923]])

        # From b16 on 27June2008 (From Chris Nicklin)
        # self.tclatt.append([3.8401, 3.8401, 5.43072, 90, 90, 90])
        # self.tcbmat.append([[1.636204, 0, 0],[0, 1.636204, 0],
        #                     [0, 0, 1.156971]])

    def testGetBMatrix(self):
        # Check the calculated B Matrix
        for sess in scenarios.sessions():
            if sess.bmatrix is None:
                continue
            cut = CrystalUnderTest('tc', *sess.lattice)
            desired = matrix(sess.bmatrix)
            print desired.tolist()
            answer = cut.getBMatrix()
            print answer.tolist()
            note = "Incorrect B matrix calculation for scenario " + sess.name
            mneq_(answer, desired, 4, note=note)

    def test__str__(self):
        cut = CrystalUnderTest("HCl", 1, 2, 3, 4, 5, 6)
        print cut.__str__()

    def testGetState(self):
        cut = CrystalUnderTest("HCl", 1, 2, 3, 4, 5, 6)
        expected = {
            'name': 'HCl',
            'a': 1,
            'b': 2,
            'c': 3,
            'alpha': 4,
            'beta': 5,
            'gamma': 6
        }
        assert_dict_almost_equal(expected, cut.getStateDict())

        cut = CrystalUnderTest(**expected)
        assert_dict_almost_equal(expected, cut.getStateDict())
