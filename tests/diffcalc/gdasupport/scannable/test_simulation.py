from math import pi
import unittest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter, \
    Gaussian
from diffcalc.geometry import fourc
from diffcalc.utils import nearlyEqual
from tests.tools import mneq_


class MockScannable(object):
    def __init__(self):
        self.pos = None

    def getPosition(self):
        return self.pos


class MockEquation(object):

    def __call__(self, dh, dk, dl):
        self.dHkl = dh, dk, dl
        return 1


class TestSimulatedCrystalCounter(unittest.TestCase):

    def setUp(self):
        self.diff = MockScannable()
        self.wl = MockScannable()
        self.wl.pos = 1.
        self.eq = MockEquation()
        self.scc = SimulatedCrystalCounter('det', self.diff, fourc(), self.wl,
                                           self.eq)

    def testInit(self):
        self.assertEquals(list(self.scc.getInputNames()), ['det_count'])
        self.assertEquals(list(self.scc.getExtraNames()), [])
        self.assertEquals(self.scc.chiMissmount, 0.)
        self.assertEquals(self.scc.phiMissmount, 0.)

    def testCalcUB(self):
        UB = matrix([[2 * pi, 0, 0], [0, 2 * pi, 0], [0, 0, 2 * pi]])
        mneq_(self.scc.UB, UB)

    def testGetHkl(self):
        self.diff.pos = [60, 30, 0, 0]
        hkl = self.scc.getHkl()
        self.assert_(nearlyEqual(hkl, (1, 0, 0), .0000001),
                     "%s!=\n%s" % (hkl, (1, 0, 0)))

        self.diff.pos = [60, 31, 0, 0]
        hkl = self.scc.getHkl()
        self.assert_(nearlyEqual(hkl,
                                 (0.999847695156391, 0.017452406437283574, 0),
                                 .0000001), "%s!=\n%s" % (hkl, (1, 0, 0)))

    def testGetPosition(self):
        self.diff.pos = [60, 30, 0, 0]
        self.scc.asynchronousMoveTo(2)
        count = self.scc.getPosition()
        self.assert_(nearlyEqual(self.eq.dHkl, (0, 0, 0), .00001))
        self.assertEqual(count, 2)

        self.diff.pos = [60, 31, 0, 0]
        count = self.scc.getPosition()
        dHkl = (0.999847695156391 - 1, .017452406437283574, 0)
        self.assert_(nearlyEqual(self.eq.dHkl, dHkl, .00001),
                      "%s!=\n%s" % (self.eq.dHkl, dHkl))
        self.assertEqual(count, 2)

    def test__repr__(self):
        self.diff.pos = [60, 30, 0, 0]
        print self.scc.__repr__()


class TestGaussianEquation(unittest.TestCase):
    def setUp(self):
        self.eq = Gaussian(1.)

    def test__call__(self):
        self.assertEquals(self.eq(0, 0, 0), 0.3989422804014327)
