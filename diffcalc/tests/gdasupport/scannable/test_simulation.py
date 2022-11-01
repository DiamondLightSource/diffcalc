###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

from math import pi
import unittest
from pytest import approx

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.gdasupport.scannable.simulation import SimulatedCrystalCounter, \
    Gaussian
from diffcalc.hkl.vlieg.geometry import Fourc
from diffcalc.util import nearlyEqual
from diffcalc.tests.tools import mneq_


class MockScannable(object):
    def __init__(self):
        self.pos = None

    def getPosition(self):
        return self.pos


class MockEquation(object):

    def __call__(self, dh, dk, dl):
        self.dHkl = dh, dk, dl
        return 1


class TestSimulatedCrystalCounter(object):

    def setup_method(self):
        self.diff = MockScannable()
        self.wl = MockScannable()
        self.wl.pos = 1.
        self.eq = MockEquation()
        self.scc = SimulatedCrystalCounter('det', self.diff, Fourc(), self.wl,
                                           self.eq)

    def testInit(self):
        assert list(self.scc.getInputNames()) == ['det_count']
        assert list(self.scc.getExtraNames()) == []
        assert self.scc.chiMissmount == 0.
        assert self.scc.phiMissmount == 0.

    def testCalcUB(self):
        UB = matrix([[2 * pi, 0, 0], [0, 2 * pi, 0], [0, 0, 2 * pi]])
        mneq_(self.scc.UB, UB)

    def testGetHkl(self):
        self.diff.pos = [60, 30, 0, 0]
        hkl = self.scc.getHkl()
        assert hkl == approx((1, 0, 0))

        self.diff.pos = [60, 31, 0, 0]
        hkl = self.scc.getHkl()
        assert hkl == approx((0.999847695156391, 0.017452406437283574, 0))

    def testGetPosition(self):
        self.diff.pos = [60, 30, 0, 0]
        self.scc.asynchronousMoveTo(2)
        count = self.scc.getPosition()
        assert self.eq.dHkl == approx((0, 0, 0))
        assert count == 2

        self.diff.pos = [60, 31, 0, 0]
        count = self.scc.getPosition()
        dHkl = (0.999847695156391 - 1, .017452406437283574, 0)
        assert self.eq.dHkl == approx(dHkl)
        assert count == 2

    def test__repr__(self):
        self.diff.pos = [60, 30, 0, 0]
        print self.scc.__repr__()


class TestGaussianEquation(object):
    def setup_method(self):
        self.eq = Gaussian(1.)

    def test__call__(self):
        assert self.eq(0, 0, 0) == 0.3989422804014327
