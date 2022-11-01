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

import unittest
from diffcalc import settings
import pytest

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix
try:
    from gdascripts.pd.dummy_pds import DummyPD  # @UnusedImport
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import DummyPD


from diffcalc.gdasupport.scannable.base import ScannableGroup
from diffcalc.gdasupport.scannable.diffractometer import \
    DiffractometerScannableGroup
from diffcalc.gdasupport.scannable.hkl import Hkl
from diffcalc.gdasupport.scannable.parameter import \
    DiffractionCalculatorParameter
from diffcalc.gdasupport.scannable.slave_driver import \
    NuDriverForSixCirclePlugin
from diffcalc.hkl.vlieg.geometry import SixCircleGammaOnArmGeometry, \
    SixCircleGeometry, Fivec, Fourc
from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.hardware import ScannableHardwareAdapter
from diffcalc.tests.tools import aneq_, mneq_
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc.util import DiffcalcException, MockRawInput
from diffcalc.tests import scenarios
import diffcalc.util  # @UnusedImport to overide raw_input
from diffcalc.gdasupport.minigda.command import sim

diffcalc.util.DEBUG = True

def prepareRawInput(listOfStrings):
    diffcalc.util.raw_input = MockRawInput(listOfStrings)


prepareRawInput([])


def createDummyAxes(names):
    result = []
    for name in names:
        result.append(DummyPD(name))
    return result


class BaseTestDiffractionCalculatorWithData(object):

    def setSessionAndCalculation(self):
        raise Exception("Abstract")

    def setup_method(self):
        self.geometry = SixCircleGammaOnArmGeometry()
        self.hardware = DummyHardwareAdapter(
            ('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'))
        settings.hardware = self.hardware
        settings.geometry = self.geometry
        settings.ubcalc_persister = UbCalculationNonPersister()
        from diffcalc.dc import dcvlieg as dc
        reload(dc)
        self.dc = dc
        self.setSessionAndCalculation()
        prepareRawInput([])

    def setDataAndReturnObject(self, sessionScenario, calculationScenario):
        self.sess = sessionScenario
        self.calc = calculationScenario
        return self

    def test_angles_to_hkl(self):
        with pytest.raises(DiffcalcException):
            self.dc.angles_to_hkl((1, 2, 3, 4, 5, 6))  # no energy set
        settings.hardware.energy = 10
        with pytest.raises(DiffcalcException):
            self.dc.angles_to_hkl((1, 2, 3, 4, 5, 6))  # no ub calculated 
        s = self.sess
        c = self.calc

        # setup session info
        self.dc.newub(s.name)
        self.dc.setlat(s.name, *s.lattice)
        r = s.ref1
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        r = s.ref2
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        self.dc.calcub()

        # check the ubcalculation is okay before continuing
        # (useful to check for typos!)
        mneq_(self.dc.ubcalc.UB,
              matrix(s.umatrix) * matrix(s.bmatrix), 4,
              note="wrong UB matrix after calculating U")
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            hkl = c.hklList[idx]
            pos = c.posList[idx]
            # 1) specifying energy explicitely
            ((h, k, l), params) = self.dc.angles_to_hkl(pos.totuple(), c.energy)
            msg = ("wrong hkl calc for TestScenario=%s, AngleTestScenario"
                   "=%s, pos=%s):\n  expected hkl=%f %f %f\n  returned hkl="
                   "%f %f %f "
                   % (s.name, c.tag, str(pos), hkl[0], hkl[1], hkl[2], h, k, l)
                   )
            assert [h, k, l] == pytest.approx(hkl, abs=.001)
#             self.assert_((abs(h - hkl[0]) < .001) & (abs(k - hkl[1]) < .001)
#                          & (abs(l - hkl[2]) < .001), msg)
            # 2) specifying energy via hardware
            settings.hardware.energy = c.energy
            msg = ("wrong hkl calcualted for TestScenario=%s, "
                   "AngleTestScenario=%s, pos=%s):\n  expected hkl=%f %f %f\n"
                   "  returned hkl=%f %f %f " %
                   (s.name, c.tag, str(pos), hkl[0], hkl[1], hkl[2], h, k, l))
            ((h, k, l), params) = self.dc.angles_to_hkl(pos.totuple())
            assert [h, k, l] == pytest.approx(hkl, abs=.001)
            del params

    def test_hkl_to_angles(self):
        s = self.sess
        c = self.calc

        ## setup session info
        self.dc.newub(s.name)
        self.dc.setlat(s.name, *s.lattice)
        r = s.ref1
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        r = s.ref2
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        self.dc.calcub()
        # check the ubcalculation is okay before continuing
        # (useful to check for typos !)
        mneq_(self.dc.ubcalc.UB,
              matrix(s.umatrix) * matrix(s.bmatrix), 4,
              note="wrong UB matrix after calculating U")

        ## setup calculation info
        self.dc.hklmode(c.modeNumber)
        # Set fixed parameters
        if c.alpha != None:
            self.dc.setpar('alpha', c.alpha)
        if c.gamma != None:
            self.dc.setpar('gamma', c.alpha)

        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            (h, k, l) = c.hklList[idx]

            expectedangles = \
                self.geometry.internal_position_to_physical_angles(c.posList[idx])
            (angles, params) = self.dc.hkl_to_angles(h, k, l, c.energy)
            expectedAnglesStr = ("%f " * len(expectedangles)) % expectedangles
            anglesString = ("%f " * len(angles)) % angles
            namesString = (("%s " * len(self.hardware.get_axes_names()))
                           % self.hardware.get_axes_names())
            note = ("wrong position calcualted for TestScenario=%s, "
                    "AngleTestScenario=%s, hkl=%f %f %f:\n"
                    "                       { %s }\n"
                    "  expected pos=%s\n  returned pos=%s "
                    % (s.name, c.tag, h, k, l, namesString, expectedAnglesStr,
                       anglesString))
            mneq_(matrix([list(expectedangles)]), matrix([list(angles)]), 2,
                  note=note)
            del params

    def testSimWithHklAndSixc(self):
        dummyAxes = createDummyAxes(
            ['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'])
        dummySixcScannableGroup = ScannableGroup('sixcgrp', dummyAxes)
        sixcdevice = DiffractometerScannableGroup(
            'SixCircleGammaOnArmGeometry', self.dc, dummySixcScannableGroup)
        hkldevice = Hkl('hkl', sixcdevice, self.dc)
        with pytest.raises(TypeError):
            sim()
        with pytest.raises(TypeError):
            sim(hkldevice)
        with pytest.raises(TypeError):
            sim(hkldevice, 1, 2, 3)
        with pytest.raises(TypeError):
            sim('not a proper scannable', 1)
        with pytest.raises(TypeError):
            sim(hkldevice, (1, 2, 'not a number'))
        with pytest.raises(TypeError):
            sim(hkldevice, 1)
        with pytest.raises(ValueError):
            sim(hkldevice, (1, 2, 3, 4))

        s = self.sess
        c = self.calc
        # setup session info
        self.dc.newub(s.name)
        self.dc.setlat(s.name, *s.lattice)
        r = s.ref1
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        r = s.ref2
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        self.dc.calcub()

        # check the ubcalculation is okay before continuing
        # (useful to check for typos!)
        mneq_(self.dc.ubcalc.UB,
              (matrix(s.umatrix) * (matrix(s.bmatrix))),
              4, note="wrong UB matrix after calculating U")
        self.hardware.energy = c.energy
        # Test each hkl/position pair
        for idx in range(len(c.hklList)):
            hkl = c.hklList[idx]
            pos = c.posList[idx].totuple()
            sim(sixcdevice, pos)
            sim(hkldevice, hkl)

    def testCheckub(self):
        ## setup session info
        s = self.sess
        self.dc.newub(s.name)
        self.dc.setlat(s.name, *s.lattice)
        r = s.ref1
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        r = s.ref2
        self.dc.addref(
            [r.h, r.k, r.l], r.pos.totuple(), r.energy, r.tag)
        self.dc.calcub()
        print "*** checkub ***"
        print self.dc.checkub()
        print "***************"


class TestDiffractionCalculatorHklWithDataSess2Calc0(
    BaseTestDiffractionCalculatorWithData):
    def setSessionAndCalculation(self):
        self.sess = scenarios.sessions()[1]
        self.calc = self.sess.calculations[0]


class TestDiffractionCalculatorHklWithDataSess3Calc0(
    BaseTestDiffractionCalculatorWithData):
    def setSessionAndCalculation(self):
        self.sess = scenarios.sessions()[2]
        self.calc = self.sess.calculations[0]


class TestSixcBase(object):

    def createDiffcalcAndScannables(self, geometryClass):
        self.en = DummyPD('en')
        dummy = createDummyAxes(
            ['alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'])
        group = ScannableGroup('sixcgrp', dummy)
        self.sixc = DiffractometerScannableGroup('sixc', None, group)
        
        self.hardware = DummyHardwareAdapter(
            ('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'))
        settings.hardware = ScannableHardwareAdapter(self.sixc, self.en)
        settings.geometry = geometryClass()
        settings.ubcalc_persister = UbCalculationNonPersister()
        from diffcalc.dc import dcvlieg as dc
        reload(dc)
        self.dc = dc
        

        self.sixc.diffcalc = self.dc
        self.hkl = Hkl('hkl', self.sixc, self.dc)


class TestFourcBase(object):

    def createDiffcalcAndScannables(self):
        self.en = DummyPD('en')
        dummy = createDummyAxes(['delta', 'omega', 'chi', 'phi'])
        scannableGroup = ScannableGroup('fourcgrp', dummy)
        self.fourc = DiffractometerScannableGroup(
            'fourc', None, scannableGroup)
        
        settings.hardware = ScannableHardwareAdapter(self.fourc, self.en)
        settings.geometry = Fourc()
        settings.ubcalc_persister = UbCalculationNonPersister()

        from diffcalc.dc import dcvlieg as dc
        reload(dc)
        self.dc = dc
        
        self.fourc.diffcalc = self.dc
        self.hkl = Hkl('hkl', self.fourc, self.dc)


class SixCircleGammaOnArmTest(TestSixcBase):

    def setup_method(self):
        TestSixcBase.createDiffcalcAndScannables(self,
                                                 SixCircleGammaOnArmGeometry)
        self.hklverbose = Hkl('hkl', self.sixc, self.dc,
                              ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        settings.hardware.set_cut('phi', -180)  # cut phi at -180 to match dif
        self.orient()

    def orient(self):
        self.dc.newub('b16_270608')
        self.dc.setlat('xtal', 3.8401, 3.8401, 5.43072)
        self.en(12.39842 / 1.24)
        self.sixc([5.000, 22.790, 0.000, 1.552, 22.400, 14.255])
        self.dc.addref([1, 0, 1.0628])
        self.sixc([5.000, 22.790, 0.000, 4.575, 24.275, 101.320])
        self.dc.addref([0, 1, 1.0628])
        self.dc.checkub()

    def testDiffractionCalculatorScannableIntegration(self):
        betain = DiffractionCalculatorParameter('betain', 'betain',
                                                self.dc.parameter_manager)
        betain.asynchronousMoveTo(12.34)
        self.assertEqual(betain.getPosition(), 12.34)

    def mode(self, mode, alpha=0, gamma=0, betain=0, betaout=0, phi=0, sig=0,
             tau=0):
        self.dc.hklmode(mode)
        self.dc.setpar('alpha', alpha)
        self.dc.setpar('gamma', gamma)
        self.dc.setpar('betain', betain)
        self.dc.setpar('betaout', betaout)
        self.dc.setpar('phi', phi)
        self.dc.sigtau(sig, tau)

    def test1(self):
        self.mode(1)
        self.hkl([.7, .9, 1.3])
        aneq_((0., 27.3557, 0., 13.6779, 37.7746, 53.9654), self.sixc(), 4)
        print self.hkl
        print self.hklverbose

    def test2(self):
        self.mode(1, alpha=5, gamma=0)
        self.hkl([.7, .9, 1.3])
        aneq_((5., 26.9296, 0., 8.4916, 27.2563, 59.5855), self.sixc(), 4)

    def test3(self):
        self.mode(1, alpha=5, gamma=10)
        self.hkl([.7, .9, 1.3])
        aneq_((5., 22.9649, 10., 42.2204, 4.9721, 23.0655), self.sixc(), 4)

    def test4(self):
        self.mode(2, alpha=5, gamma=10, betain=4)

        self.hkl([.7, .9, 1.3])
        aneq_((5, 22.9649, 10., -11.8850, 4.7799, 80.4416),
              self.sixc(), 4, note="[alpha, delta, gamma, omega, chi, phi")

    def test5(self):
        self.mode(1, alpha=5, gamma=10, sig=-1.3500, tau=-106)
        self.hkl([.7, .9, 1.3])
        aneq_((5., 22.9649, 10., 30.6586, 4.5295, 35.4036), self.sixc(), 4)

    def test6(self):
        self.mode(2, alpha=5, gamma=10, sig=-1.3500, tau=-106, betain=6)
        self.hkl([.7, .9, 1.3])
        aneq_((5., 22.9649, 10., 2.2388, 4.3898, 65.4395), self.sixc(), 4)

    def test7(self):
        self.mode(3, alpha=5, gamma=10, sig=-1.3500, tau=-106, betaout=7)
        self.hkl([.7, .9, 1.3])
        aneq_((5., 22.9649, 10., 43.4628, 5.0387, 21.7292), self.sixc(), 4)

    def test7a(self):
        self.mode(5, phi=10)  # Fix phi
        self.hkl([.7, .9, 1.3])

    def test8(self):
        #8
        self.mode(10, gamma=10, sig=-1.35, tau=-106)  # 5cgBeq
        self.hkl([.7, .9, 1.3])
        aneq_((6.1937, 22.1343, 10., 46.9523, 1.5102, 18.8112), self.sixc(), 3)

    def test9(self):
        self.mode(13, alpha=5, gamma=10, sig=-1.35, tau=-106)  # 5cgBeq
        self.hkl([.7, .9, 1.3])
        aneq_((5., 22.2183, 11.1054, 65.8276, 2.5180, -0.0749), self.sixc(), 4)

    def test10(self):
        self.mode(20, sig=-1.35, tau=-106)  # 6czBeq
        self.hkl([.7, .9, 1.3])
        aneq_((8.1693, 22.0156, 8.1693, -40.2188, 1.35, 106.), self.sixc(), 4)

    def test11(self):
        self.mode(21, betain=8, sig=-1.35, tau=-106)  # 6czBin
        self.hkl([.7, .9, 1.3])
        aneq_((8., 22.0156, 8.3386, -40.0939, 1.3500, 106.), self.sixc(), 4)

    def test12(self):
        self.mode(22, betaout=1, sig=-1.35, tau=-106)  # 6czBin
        self.hkl([.7, .9, 1.3])
        aneq_((15.4706, 22.0994, 1., -45.5521, 1.3500, 106.), self.sixc(), 4)


class ZAxisGammaOnBaseTest(TestSixcBase):

    def setup_method(self):
        TestSixcBase.createDiffcalcAndScannables(self, SixCircleGeometry)
        self.hklverbose = Hkl('hkl', self.sixc, self.dc, ('Bout'))
        self.orient()

    def orient(self):
        self.dc.newub('From DDIF')
        self.dc.setlat('cubic', 1, 1, 1)
        self.en(12.39842 / 1)
        self.dc.setu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.dc.hklmode(20)  # zaxis, bisecting
        self.dc.sigtau(0, 0)

    def checkHKL(self, hkl, adgocp=None, betaout=None, nu=None):
        self.hklverbose.asynchronousMoveTo(hkl)
        aneq_(self.sixc(), list(adgocp), 3)
        aneq_(self.hklverbose(), (hkl[0], hkl[1], hkl[2], betaout), 3)

    def testHKL_001(self):
        self.checkHKL([0, 0.0000001, 1], [30, 0, 60, 90, 0, 0], betaout=30, nu=0)

    def testHKL_010(self):
        self.checkHKL([0, 1, 0], [0, 60, 0, 120, 0, 0], betaout=0, nu=0)

    def testHKL_011(self):
        self.checkHKL([0, 1, 1], [30, 54.7356, 90, 125.2644, 0, 0],
                      betaout=30, nu=-54.7356)

    def testHKL_100(self):
        self.checkHKL([1, 0, 0], [0, 60, 0, 30, 0, 0], betaout=0, nu=0)

    def testHKL_101(self):
        self.checkHKL([1, 0, 1], [30, 54.7356, 90, 35.2644, 0, 0],
                      betaout=30, nu=-54.7356)

    def testHKL_110(self):
        #TODO: Modify test to ask that in this case gamma is left unmoved
        self.checkHKL([1, 1, 0], [0, 90, 0, 90, 0, 0], betaout=0, nu=0)

    def testHKL_1_1_0001(self):
        self.checkHKL([1, 1, .0001], [0.0029, 89.9971, 90.0058, 90., 0, 0],
                      betaout=0.0029, nu=89.9971)

    def testHKL_111(self):
        self.checkHKL([1, 1, 1], [30, 54.7356, 150, 99.7356, 0, 0],
                      betaout=30, nu=54.7356)

    def testHKL_11_0_0(self):
        self.checkHKL([1.1, 0, 0], [0, 66.7340, 0., 33.3670, 0, 0],
                      betaout=0, nu=0)

    def testHKL_09_0_0(self):
        self.checkHKL([.9, 0, 0], [0, 53.4874, 0, 26.7437, 0, 0],
                      betaout=0, nu=0)

    def testHKL_07_08_08(self):
        self.checkHKL([.7, .8, .8], [23.5782, 59.9980, 76.7037, 84.2591, 0, 0],
                      betaout=23.5782, nu=-49.1014)

    def testHKL_07_08_09(self):
        self.checkHKL([.7, .8, .9], [26.7437, 58.6754, 86.6919, 85.3391, 0, 0],
                      betaout=26.7437, nu=-55.8910)

    def testHKL_07_08_1(self):
        self.checkHKL([.7, .8, 1], [30, 57.0626, 96.8659, 86.6739, 0, 0],
                      betaout=30, nu=-63.0210)


class ZAxisGammaOnBaseIncludingNuRotationTest(ZAxisGammaOnBaseTest):

    def setup_method(self):
        ZAxisGammaOnBaseTest.setup_method(self)
        self.nu = DummyPD('nu')
        self.sixc.slaveScannableDriver = NuDriverForSixCirclePlugin(self.nu)


class SixcGammaOnBaseTest(TestSixcBase):

    def setup_method(self):
        TestSixcBase.createDiffcalcAndScannables(self, SixCircleGeometry)
        self.hklverbose = Hkl('hkl', self.sixc, self.dc, ('Bout'))
        self.orient()

    def orient(self):
        self.dc.newub('From DDIF')
        self.dc.setlat('cubic', 1, 1, 1)
        self.en(12.39842 / 1)
        self.dc.setu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.dc.sigtau(0, 0)

    def testToFigureOut101and011(self):
        self.hkl([1, 0, 1])
        print "101: ", self.sixc()
        self.hkl([0, 1, 1])
        print "011: ", self.sixc()
        print "**"

    def testOrientation(self):
        self.dc.newub('cubic')
        self.dc.setlat('cubic', 1, 1, 1)
        self.en(39842 / 1)
        self.dc.sigtau(0, 0)
        self.sixc([0, 90, 0, 45, 45, 0])
        self.dc.addref([1, 0, 1])
        self.sixc([0, 90, 0, 45, 45, 90])
        self.dc.addref([0, 1, 1])
        self.dc.checkub()
        res = self.dc.ubcalc.U
        des = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        mneq_(res, des, 4)
#         print "***"
#         self.dc.dc()
        print "***"
        self.dc.showref()
        print "***"
        self.dc.hklmode()
        print "***"


class FiveCircleTest(object):

    def setup_method(self):
        self.en = DummyPD('en')
        dummy = createDummyAxes(['alpha', 'delta', 'omega', 'chi', 'phi'])
        group = ScannableGroup('fivecgrp', dummy)
        self.fivec = DiffractometerScannableGroup('fivec', None, group)
        
        settings.hardware = ScannableHardwareAdapter(self.fivec, self.en)
        settings.geometry = Fivec()
        settings.ubcalc_persister = UbCalculationNonPersister()
        from diffcalc.dc import dcvlieg as dc
        reload(dc)
        self.dc = dc
        
        self.fivec.diffcalc = self.dc
        self.hkl = Hkl('hkl', self.fivec, self.dc)
        self.hklverbose = Hkl('hkl', self.fivec, self.dc,
                              ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()

    def orient(self):
        self.dc.newub('b16_270608')
        self.dc.setlat('xtal', 3.8401, 3.8401, 5.43072)
        self.en(12.39842 / 1.24)
        self.fivec([5.000, 22.790, 1.552, 22.400, 14.255])
        self.dc.addref([1, 0, 1.0628])
        self.fivec([5.000, 22.790, 4.575, 24.275, 101.320])
        self.dc.addref([0, 1, 1.0628])
        self.dc.checkub()

    def testSetGammaFails(self):
        self.assertRaises(
            DiffcalcException, self.dc.setpar, 'gamma', 9999)

    def test1(self):
        self.dc.hklmode(1)
        self.dc.setpar('alpha', 0)
        self.hkl([.7, .9, 1.3])
        aneq_((0., 27.3557, 13.6779, 37.7746, 53.9654), self.fivec(), 4)

    def test2(self):
        self.dc.hklmode(1)
        self.dc.setpar('alpha', 5)
        self.hkl([.7, .9, 1.3])
        aneq_((5., 26.9296, 8.4916, 27.2563, 59.5855), self.fivec(), 4)


class FourCircleTest(TestFourcBase):

    def setup_method(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.dc,
                              ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()

    def orient(self):
        self.dc.newub('fromDiffcalcItself')
        # This dataset generated by diffcalc code itself
        # (not a proper test of code guts)
        self.dc.setlat('xtal', 3.8401, 3.8401, 5.43072)
        self.en(12.39842 / 1.24)
        self.fourc([22.790, 1.552, 22.400, 14.255])
        self.dc.addref([1, 0, 1.0628])
        self.fourc([22.790, 4.575, 24.275, 101.320])
        self.dc.addref([0, 1, 1.0628])
        self.dc.checkub()

    def testSetGammaFails(self):
        self.assertRaises(
            DiffcalcException, self.dc.setpar, 'gamma', 9999)

    def test1(self):
        self.dc.hklmode(1)
        self.hkl([.7, .9, 1.3])
        aneq_((27.3557325339904, 13.67786626699521, 23.481729970652825,
               47.81491152277463), self.fourc(), 4)


class FourCircleWithcubic(TestFourcBase):

    def setup_method(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.dc,
                              ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()

    def setUp3(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.dc,
                              ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()

    def orient(self):
        self.dc.newub('cubic')
        # This dataset generated by diffcalc code itself
        # (not a proper test of code guts)
        self.dc.setlat('cube', 1, 1, 1, 90, 90, 90)
        self.en(12.39842)
        self.fourc([60, 30, 0, 0])
        self.dc.addref([1, 0, 0])
        self.fourc([60, 30, 90, 0])
        self.dc.addref([0, 0, 1])
        self.dc.checkub()

    def testHkl100(self):
        self.dc.hklmode(1)
        self.dc.sigtau(0, 0)
        self.hkl([1, 0, 0])
        aneq_(self.fourc(), (60, -60, 0, 90), 4)
        #dif gives
        #h       k       l       alpha    delta    gamma    omega      chi  phi
        #1.000   0.000   0.000   0.  60.   0.0000 -60.0000   0.0000  90.0000
        #beta_in beta_out      rho      eta twotheta
        #-0.0000   0.0000   0.0000   0.0000  60.0000

    def testHkl001(self):
        self.dc.hklmode(1)
        self.dc.sigtau(0, 0)
        self.hkl([0, 0, 1])
        aneq_(self.fourc()[0:3], (60, 30, 90), 4)  # (phi is undetermined here)
        #h       k       l        alpha    delta    gamma    omega      ch  phi
        #0.000   0.000   1.000   0.0000  60.   0.  30.0000  90.0000  45.0000
        #                          beta_in beta_out      rho      eta twotheta
        #                          30.0000  30.0000  60.0000   0.5236  60.0000

    def testHkl110(self):
        self.dc.hklmode(1)
        self.dc.sigtau(0, 0)
        self.hkl([1, 1, 0])
        # TODO: No check here!
        #    h       k       l    alpha    delta    gamma    omega   chi    phi
        #1.000   1.000   0.000   0.  90.   0.0000 135.0000   0.0000 -45.0000
        #                          beta_in beta_out      rho      eta twotheta
        #                           0.0000  -0.0000  -0.0000   0.0000  90.0000


class FourCircleForI06Experiment(TestFourcBase):

    def setup_method(self):
        TestFourcBase.createDiffcalcAndScannables(self)
        self.hklverbose = Hkl('hkl', self.fourc, self.dc,
                              ('theta', '2theta', 'Bin', 'Bout', 'azimuth'))
        self.orient()

    def orient(self):
        self.en(1.650)
        self.dc.newub('cubic')
        self.dc.setlat('xtal', 5.34, 5.34, 13.2, 90, 90, 90)
        self.dc.setu([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.dc.hklmode(5)
        self.dc.setpar('phi', -90)
        self.dc.setcut('phi', -180)  # @UndefinedVariable

    def testHkl001(self):
        self.hkl([0, 0, 1])
        aneq_(self.fourc(), [33.07329403295449, 16.536647016477247, 90., -90.],
              note="[delta, omega, chi, phi]")

#    def testHkl100(self):
#        self.pos_hkl(1, 0, 0)
#        aneq_(self.pos_fourc(),
#              [89.42926563609406, 134.71463281804702, 90.0, -90.0],
#              note="[delta, omega, chi, phi]")

    def testHkl101(self):
        self.hkl([1, 0, 1])
        aneq_(self.fourc(), [98.74666191021282, 117.347760720783, 90., -90.],
              note="[delta, omega, chi, phi]")
