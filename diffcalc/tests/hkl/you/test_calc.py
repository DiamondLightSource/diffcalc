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

from math import pi, cos, sin
from nose.tools import raises
from mock import Mock
from diffcalc import settings

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

from diffcalc.hardware import DummyHardwareAdapter
from diffcalc.hkl.you.calc import YouHklCalculator
from diffcalc.hkl.you.constraints import YouConstraintManager
from diffcalc.tests.tools import assert_array_almost_equal, \
    assert_second_dict_almost_in_first, arrayeq_
from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.util import y_rotation, z_rotation, DiffcalcException
from diffcalc.hkl.you.geometry import YouPosition as Pos, SixCircle, YouGeometry
from diffcalc.hkl.you.calc import youAnglesToHkl

TORAD = pi / 180
TODEG = 180 / pi
I = matrix('1 0 0; 0 1 0; 0 0 1')

from diffcalc.settings import NUNAME

class Pair:

    def __init__(self, name, hkl, position, fails=False):
        self.name = name
        self.hkl = hkl
        self.position = position
        self.fails = fails


def createMockUbcalc(UB):
    ubcalc = Mock()
    ubcalc.tau = 0
    ubcalc.sigma = 0
    ubcalc.UB = UB
    ubcalc.n_phi = matrix([[0], [0], [1]])
    ubcalc.surf_nphi = matrix([[0], [0], [1]])
    return ubcalc


def createMockHardwareMonitor():
    names = ['mu', 'delta', NUNAME, 'eta', 'chi', 'phi']
    hardware = DummyHardwareAdapter(names)

    hardware.set_lower_limit('delta', 0)
    hardware.set_upper_limit('delta', 179.999)
    hardware.set_lower_limit(NUNAME, 0)
    hardware.set_upper_limit(NUNAME, 179.999)
    hardware.set_lower_limit('mu', 0)
    hardware.set_lower_limit('eta', 0)
    hardware.set_upper_limit('chi', 179.999)
    hardware.set_lower_limit('chi', -10)
    hardware.set_cut('phi', -179.999)
    return hardware


class _BaseTest(object):

    def setup_method(self):
        self.mock_ubcalc = createMockUbcalc(None)
        settings.geometry = SixCircle()
        self.constraints = YouConstraintManager()
        self.calc = YouHklCalculator(self.mock_ubcalc, self.constraints)

        self.mock_hardware = createMockHardwareMonitor()
        self.mock_hardware.set_lower_limit('delta', 0)
        self.mock_hardware.set_upper_limit('delta', 179.999)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        self.mock_hardware.set_upper_limit(NUNAME, 179.999)
        self.mock_hardware.set_lower_limit('mu', 0)
        self.mock_hardware.set_lower_limit('eta', 0)
        self.mock_hardware.set_upper_limit('chi', 179.999)
        self.mock_hardware.set_lower_limit('chi', -10)
        self.mock_hardware.set_cut('phi', -179.999)
        settings.hardware = self.mock_hardware

        self.places = 5

    def _configure_ub(self):
        ZROT = z_rotation(self.zrot * TORAD)  # -PHI
        YROT = y_rotation(self.yrot * TORAD)  # +CHI
        U = ZROT * YROT
        UB = U * self.B
        self.mock_ubcalc.UB = UB

    def _check_hkl_to_angles(self, testname, zrot, yrot, hkl, pos_expected,
                             wavelength, virtual_expected={}):
        print ('_check_hkl_to_angles(%s, %.1f, %.1f, %s, %s, %.2f, %s)' %
               (testname, zrot, yrot, hkl, pos_expected, wavelength,
                virtual_expected))
        self.zrot, self.yrot = zrot, yrot
        self._configure_ub()

        pos, virtual = self.calc.hklToAngles(hkl[0], hkl[1], hkl[2],
                                             wavelength)
        assert_array_almost_equal(pos.totuple(), pos_expected.totuple(),
                                  self.places)
        assert_second_dict_almost_in_first(virtual, virtual_expected)

    def _check_angles_to_hkl(self, testname, zrot, yrot, hkl_expected, pos,
                             wavelength, virtual_expected={}):
        print ('_check_angles_to_hkl(%s, %.1f, %.1f, %s, %s, %.2f, %s)' %
               (testname, zrot, yrot, hkl_expected, pos, wavelength,
                virtual_expected))
        self.zrot, self.yrot = zrot, yrot
        self._configure_ub()
        hkl, virtual = self.calc.anglesToHkl(pos, wavelength)
        assert_array_almost_equal(hkl, hkl_expected, self.places, note="***Test (not diffcalc!) incorrect*** : the desired settings do not map to the target hkl")
        assert_second_dict_almost_in_first(virtual, virtual_expected)

    @raises(DiffcalcException)
    def _check_hkl_to_angles_fails(self, *args):
        self._check_hkl_to_angles(*args)

    def case_generator(self):
        for case in self.case_dict.values():
            yield (self._check_angles_to_hkl, case.name, self.zrot, self.yrot,
                   case.hkl, case.position, self.wavelength, {})
            test_method = (self._check_hkl_to_angles_fails if case.fails else
                           self._check_hkl_to_angles)
            yield (test_method, case.name, self.zrot, self.yrot, case.hkl,
                                case.position, self.wavelength, {})


class _TestCubic(_BaseTest):

    def setup_method(self):
        _BaseTest.setup_method(self)
        self.B = I * 2 * pi


class _TestCubicVertical(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('100', (1, 0, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=0 - self.yrot,
                     phi=0 + self.zrot, unit='DEG')),
            Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=4 - self.yrot,
                     phi=0 + self.zrot, unit='DEG'),),
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=90 + self.zrot, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=90 - self.yrot,
                     phi=0 + self.zrot, unit='DEG')),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=0, delta=97.46959231642, nu=0,
                      eta=97.46959231642/2, chi=86.18592516571 - self.yrot,
                      phi=0 + self.zrot, unit='DEG')),
            Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=86 - self.yrot,
                     phi=0 + self.zrot, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_various_zrot_and_yrot0(self):
        for zrot in [0, 2, -2, 45, -45, 90, -90]:  # -180, 180 work if recut
            self.makes_cases(zrot, 0)
            self.case_dict['001'].fails = True  # q||n
            for case_tuple in self.case_generator():
                yield case_tuple

    def test_hkl_to_angles_zrot1_yrot2(self):
        self.makes_cases(1, 2)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_hkl_to_angles_zrot1_yrotm2(self):
        self.makes_cases(1, -2)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_hkl_to_angles_zrotm1_yrot2(self):
        self.makes_cases(-1, 2)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_hkl_to_angles_zrotm1_yrotm2(self):
        self.makes_cases(-1, -2)
        for case_tuple in self.case_generator():
            yield case_tuple

    def testHklDeltaGreaterThan90(self):
        wavelength = 1            
        hkl = (0.1, 0, 1.5)
        pos = Pos(mu=0, delta=97.46959231642, nu=0,
                      eta=97.46959231642/2, chi=86.18592516571,
                      phi=0, unit='DEG')
        self._check_hkl_to_angles('', 0, 0, hkl, pos, wavelength)


class TestCubicVertical_aeqb(_TestCubicVertical):

    def setup_method(self):
        _TestCubicVertical.setup_method(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0, NUNAME: 0}


class TestCubicVertical_psi_90(_TestCubicVertical):
    '''mode psi=90 should be the same as mode a_eq_b'''

    def setup_method(self):
        _TestCubicVertical.setup_method(self)
        self.constraints._constrained = {'psi': 90 * TORAD, 'mu': 0, NUNAME: 0}

    def test_pairs_various_zrot_and_yrot0(self):
        for zrot in [0, 2, -2, 45, -45, 90, -90]:  # -180, 180 work if recut
            self.makes_cases(zrot, 0)
            self.case_dict['001'].fails = True  # q||n psi is undefined
            for case_tuple in self.case_generator():
                yield case_tuple

    def test_hkl_to_angles_zrot1_yrotm2(self):
        self.constraints._constrained = {'psi': -90 * TORAD, 'mu': 0, NUNAME: 0}
        super(TestCubicVertical_psi_90, self).test_hkl_to_angles_zrot1_yrotm2()

    def test_hkl_to_angles_zrotm1_yrotm2(self):
        self.constraints._constrained = {'psi': -90 * TORAD, 'mu': 0, NUNAME: 0}
        super(TestCubicVertical_psi_90, self).test_hkl_to_angles_zrotm1_yrotm2()

class TestCubicVertical_qaz_90(_TestCubicVertical):
    '''mode psi=90 should be the same as mode a_eq_b'''

    def setup_method(self):
        _TestCubicVertical.setup_method(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0,
                                         'qaz': 90 * TORAD}


class TestCubicVertical_ChiPhiMode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {NUNAME: 0, 'chi': 90. * TORAD, 'phi': 0.}
        self.mock_hardware.set_lower_limit('mu', -180.)
        self.mock_hardware.set_lower_limit('eta', -180.)
        self.places = 5

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('110', (1, 1, 0),
                 Pos(mu=-90, delta=90, nu=0, eta=90, chi=90,
                     phi=0, unit='DEG')),
            Pair('100-->001', (sin(4 * TORAD), 0, cos(4 * TORAD)),
                 Pos(mu=-8.01966360660, delta=60, nu=0, eta=29.75677306273, chi=90,
                     phi=0, unit='DEG'),),
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=60, nu=0, eta=120, chi=90, phi=0, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30 - self.yrot, chi=90,
                     phi=0, unit='DEG')),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=-5.077064540005, delta=97.46959231642, nu=0,
                      eta=48.62310452627, chi=90 - self.yrot,
                      phi=0 + self.zrot, unit='DEG')),
            Pair('010-->001', (0, cos(86 * TORAD), sin(86 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=34, chi=90,
                     phi=0, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple

class TestCubic_FixedPhiMode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'mu': 0, NUNAME: 0, 'phi': 0}
        self.mock_hardware.set_upper_limit('chi', 180.)
        self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('100', (1, 0, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=0 - self.yrot,
                     phi=0, unit='DEG')),
            Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=4 - self.yrot,
                     phi=0, unit='DEG'),),
            #Pair('010', (0, 1, 0),
            #     Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=0, phi=90, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=90 - self.yrot,
                     phi=0, unit='DEG')),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=0, delta=97.46959231642, nu=0,
                      eta=97.46959231642/2 + self.zrot, chi=86.18592516571 - self.yrot,
                      phi=0, unit='DEG')),
            Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=86 - self.yrot,
                     phi=0, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_various_zrot0_and_yrot(self):
        for yrot in [0, 2, -2, 45, -45, 90, -90]:  # -180, 180 work if recut
            self.makes_cases(0, yrot)
            for case_tuple in self.case_generator():
                yield case_tuple

class TestCubic_FixedPhi30Mode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'mu': 0, NUNAME: 0, 'phi': 30 * TORAD}
        self.mock_hardware.set_upper_limit('chi', 180.)
        self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('100', (1, 0, 0),
                 Pos(mu=0, delta=60, nu=0, eta=0 + self.zrot, chi=0 - self.yrot,
                     phi=30, unit='DEG')),
            #Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
            #     Pos(mu=0, delta=60, nu=0, eta=0 + self.zrot, chi=4 - self.yrot,
            #         phi=30, unit='DEG'),),
            #Pair('010', (0, 1, 0),
            #     Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=0, phi=90, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=90 - self.yrot,
                     phi=30, unit='DEG')),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=0, delta=97.46959231642, nu=0,
                      eta=46.828815370173 + self.zrot, chi=86.69569481984 - self.yrot,
                      phi=30, unit='DEG')),
            #Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
            #     Pos(mu=0, delta=60, nu=0, eta=0 + self.zrot, chi=86 - self.yrot,
            #         phi=30, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_and_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple

class TestCubic_FixedPhiMode010(TestCubic_FixedPhiMode):

    def setup_method(self):
        TestCubic_FixedPhiMode.setup_method(self)
        self.constraints._constrained = {'mu': 0, NUNAME: 0, 'phi': 90 * TORAD}

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30 + self.zrot, chi=0, phi=90, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_various_zrot0_and_yrot(self):
        for yrot in [0, 2, -2, 45, -45, 90, -90]:  # -180, 180 work if recut
            self.makes_cases(0, yrot)
            
            for case_tuple in self.case_generator():
                yield case_tuple

class TestCubicVertical_MuEtaMode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {NUNAME: 0, 'mu': 90. * TORAD, 'eta': 0.}
        self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('011', (0, 1, 1),
                 Pos(mu=90, delta=90, nu=0, eta=0, chi=0,
                     phi=90, unit='DEG')),
            Pair('100-->001', (sin(4 * TORAD), 0, cos(4 * TORAD)),
                 Pos(mu=90, delta=60, nu=0, eta=0, chi=56,
                     phi=0, unit='DEG'),),
            Pair('010', (0, 1, 0),
                 Pos(mu=90, delta=60, nu=0, eta=0, chi=-30, phi=90, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=90, delta=60, nu=0, eta=0, chi=60,
                     phi=0, unit='DEG'), fails=True),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=90, delta=97.46959231642, nu=0,
                      eta=0, chi=37.45112900750 - self.yrot,
                      phi=0 + self.zrot, unit='DEG')),
            Pair('010-->001', (0, cos(86 * TORAD), sin(86 * TORAD)),
                 Pos(mu=90, delta=60, nu=0, eta=0, chi=56,
                     phi=90, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubic_FixedRefMuPhiMode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'psi': 90 * TORAD, 'mu': 0, 'phi': 0}
        self.mock_hardware.set_upper_limit('chi', 180.)
        self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('100', (1, 0, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=0,
                     phi=0, unit='DEG')),
            Pair('010-->100', (sin(4 * TORAD), cos(4 * TORAD), 0),
                 Pos(mu=0, delta=60, nu=0, eta=120 - 4, chi=0,
                     phi=0, unit='DEG'),),
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=60, nu=0, eta=120, chi=0, phi=0, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=90,
                     phi=0, unit='DEG'), fails=True),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=0, delta=97.46959231642, nu=0,
                      eta=97.46959231642/2, chi=86.18592516571,
                      phi=0, unit='DEG')),
            Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=86,
                     phi=0, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_various_zrot0_and_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubic_FixedRefEtaPhiMode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'psi': 0, 'eta': 0, 'phi': 0}
        self.mock_hardware.set_upper_limit('chi', 180.)
        self.mock_hardware.set_lower_limit('chi', -180.)
        self.mock_hardware.set_upper_limit('mu', 180.)
        self.mock_hardware.set_lower_limit('mu', -180.)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('100', (1, 0, 0),
                 Pos(mu=-90, delta=60, nu=0, eta=0, chi=30,
                     phi=0, unit='DEG')),
            Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                 Pos(mu=-90, delta=60, nu=0, eta=0, chi=30 + 4,
                     phi=0, unit='DEG'),),
            Pair('010', (0, 1, 0),
                 Pos(mu=120, delta=0, nu=60, eta=0, chi=180, phi=0, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=90,
                     phi=0, unit='DEG'), fails=True),
            Pair('0.1 0 1.5', (0.1, 0, 0.15),  # cover case where delta > 90 !
                  Pos(mu=-90, delta=10.34318, nu=0,
                      eta=0, chi=61.48152,
                      phi=0, unit='DEG')),
            Pair('010-->001', (0, cos(4 * TORAD), sin(4 * TORAD)),
                 Pos(mu=120 + 4, delta=0, nu=60, eta=0, chi=180,
                     phi=0, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_various_zrot0_and_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubicVertical_Bisect(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {NUNAME: 0, 'bisect': None, 'omega': 0}
        self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('101', (1, 0, 1),
                 Pos(mu=0, delta=90, nu=0, eta=45, chi=45,
                     phi=0, unit='DEG')),
            Pair('10m1', (1, 0, -1),
                 Pos(mu=0, delta=90, nu=0, eta=45, chi=-45,
                     phi=0, unit='DEG')),
            Pair('011', (0, 1, 1),
                 Pos(mu=0, delta=90, nu=0, eta=45, chi=45,
                     phi=90, unit='DEG')),
            Pair('100-->001', (sin(4 * TORAD), 0, cos(4 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=86,
                     phi=0, unit='DEG'),),
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=90, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=90,
                     phi=0, unit='DEG'), fails=True),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=0, delta=97.46959231642, nu=0,
                      eta=48.73480, chi=86.18593 - self.yrot,
                      phi=0 + self.zrot, unit='DEG')),
            Pair('010-->001', (0, cos(86 * TORAD), sin(86 * TORAD)),
                 Pos(mu=0, delta=60, nu=0, eta=30, chi=86,
                     phi=90, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubicVertical_Bisect_NuMu(TestCubicVertical_Bisect):

    def setup_method(self):
        TestCubicVertical_Bisect.setup_method(self)
        self.constraints._constrained = {NUNAME: 0, 'bisect': None, 'mu': 0}


class TestCubicVertical_Bisect_qaz(TestCubicVertical_Bisect):

    def setup_method(self):
        TestCubicVertical_Bisect.setup_method(self)
        self.constraints._constrained = {'qaz': 90. * TORAD, 'bisect': None, 'mu': 0}


class TestCubicHorizontal_Bisect(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'delta': 0, 'bisect': None, 'omega': 0}
        self.mock_hardware.set_lower_limit('chi', 0.)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
            Pair('101', (1, 0, 1),
                 Pos(mu=45, delta=0, nu=90, eta=0, chi=45,
                     phi=180, unit='DEG')),
            Pair('10m1', (1, 0, -1),
                 Pos(mu=45, delta=0, nu=90, eta=0, chi=135,
                     phi=180, unit='DEG')),
            Pair('011', (0, 1, 1),
                 Pos(mu=45, delta=0, nu=90, eta=0, chi=45,
                     phi=-90, unit='DEG')),
            Pair('100-->001', (sin(4 * TORAD), 0, cos(4 * TORAD)),
                 Pos(mu=30, delta=0, nu=60, eta=0, chi=4,
                     phi=180, unit='DEG'),),
            Pair('010', (0, 1, 0),
                 Pos(mu=30, delta=0, nu=60, eta=0, chi=90, phi=-90, unit='DEG')),
            Pair('001', (0, 0, 1),
                 Pos(mu=30, delta=0, nu=60, eta=0, chi=0,
                     phi=0, unit='DEG'), fails=True),
            Pair('0.1 0 1.5', (0.1, 0, 1.5),  # cover case where delta > 90 !
                  Pos(mu=48.73480, delta=0, nu=97.46959231642,
                      eta=0, chi=3.81407 - self.yrot,
                      phi=180 + self.zrot, unit='DEG')),
            Pair('010-->001', (0, cos(86 * TORAD), sin(86 * TORAD)),
                 Pos(mu=30, delta=0, nu=60, eta=0, chi=4,
                     phi=-90, unit='DEG')),
        )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubicHorizontal_Bisect_NuMu(TestCubicHorizontal_Bisect):

    def setup_method(self):
        TestCubicHorizontal_Bisect.setup_method(self)
        self.constraints._constrained = {'delta': 0, 'bisect': None, 'eta': 0}


class TestCubicHorizontal_Bisect_qaz(TestCubicHorizontal_Bisect):

    def setup_method(self):
        TestCubicHorizontal_Bisect.setup_method(self)
        self.constraints._constrained = {'qaz': 0, 'bisect': None, 'eta': 0}


class SkipTestYouHklCalculatorWithCubicMode_aeqb_delta_60(_TestCubicVertical):
    '''
    Works to 4-5 decimal places but chooses different solutions when phi||eta .
    Skip all tests.
    '''

    def setup_method(self):
        _TestCubicVertical.setup_method(self)
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0,
                                         'delta': 60 * TORAD}
        self.places = 5


class _TestCubicHorizontal(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)

    def makes_cases(self, zrot, yrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=90 + self.yrot,
                      phi=-180 + self.zrot, unit='DEG')),
             Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=90 - 4 + self.yrot,
                      phi=-180 + self.zrot, unit='DEG')),
             Pair('010', (0, 1, 0),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=90,
                      phi=-90 + self.zrot, unit='DEG'), fails=True),  # degenrate case mu||phi
             Pair('001', (0, 0, 1),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0 - self.yrot,
                      phi=0 + self.zrot, unit='DEG')),
             Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0 - 4 - self.yrot,
                      phi=0 + self.zrot, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        self.case_dict['001'].fails = True  # q||n
        self.case_dict['100'].fails = True  # mu||phi
        self.case_dict['100-->001'].position.phi = 180  # not -180
        for case_tuple in self.case_generator():
            yield case_tuple

#    def test_pairs_various_zrot_and_yrot0(self):
#        for zrot in [0, 2, -2, 45, -45, 90, -90]:
# -180, 180 work but with cut problem
#            self.makes_cases(zrot, 0)
#            self.case_dict['001'].fails = True # q||n
#            for case_tuple in self.case_generator():
#                yield case_tuple

    def test_hkl_to_angles_zrot1_yrot2(self):
        self.makes_cases(1, 2)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_hkl_to_angles_zrot1_yrotm2(self):
        self.makes_cases(1, -2)
        for case_tuple in self.case_generator():
            yield case_tuple


class TestCubicHorizontal_qaz0_aeqb(_TestCubicHorizontal):

    def setup_method(self):
        _TestCubicHorizontal.setup_method(self)
        self.constraints._constrained = {'a_eq_b': None, 'qaz': 0, 'eta': 0}


class TestCubicHorizontal_delta0_aeqb(_TestCubicHorizontal):

    def setup_method(self):
        _TestCubicHorizontal.setup_method(self)
        self.constraints._constrained = {'a_eq_b': None, 'delta': 0, 'eta': 0}


class TestCubic_FixedDeltaEtaPhi0Mode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'eta': 0, 'delta': 0, 'phi': 0}
        self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, yrot, zrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=-90 - self.yrot,
                      phi=0, unit='DEG')),
             Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi= -90 + 4 - self.yrot,
                      phi=0, unit='DEG')),
             Pair('010', (0, 1, 0),
                  Pos(mu=120, delta=0, nu=60, eta=0, chi=0,
                      phi=0, unit='DEG'), fails=True),  # degenerate case chi||q
             Pair('001', (0, 0, 1),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0 - self.yrot,
                      phi=0, unit='DEG')),
             Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0 - 4 - self.yrot,
                      phi=0, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_pairs_various_zrot0_and_yrot(self):
        for yrot in [0, 2, -2, 45, -45, 90, -90]:
            self.makes_cases(yrot, 0)
            for case_tuple in self.case_generator():
                yield case_tuple
    
class TestCubic_FixedDeltaEtaPhi30Mode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'eta': 0, 'delta': 0, 'phi': 30 * TORAD}
        self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, yrot, zrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=0, delta=0, nu=60, eta=0, chi=-90 - self.yrot,
                      phi=30, unit='DEG')),
             Pair('010', (0, 1, 0),
                  Pos(mu=90, delta=0, nu=60, eta=0, chi=-90 - self.yrot,
                      phi=30, unit='DEG')),
             Pair('001', (0, 0, 1),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0 - self.yrot,
                      phi=30, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple

class TestCubic_FixedDeltaEtaChi0Mode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'eta': 0, 'delta': 0, 'chi': 0}
        #self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, yrot, zrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=120, delta=0, nu=60, eta=0, chi=0,
                      phi=-90 + self.zrot, unit='DEG')),
             Pair('100-->001', (cos(4 * TORAD), 0, sin(4 * TORAD)),
                  Pos(mu=120 - 4, delta=0, nu=60, eta=0, chi= 0,
                      phi=-90 + self.zrot, unit='DEG')),
             Pair('010', (0, 1, 0),
                  Pos(mu=120, delta=0, nu=60, eta=0, chi=0,
                      phi=self.zrot, unit='DEG')),
             Pair('001', (0, 0, 1),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=0,
                      phi=0, unit='DEG'), fails=True),  # degenerate case phi||q
             Pair('001-->100', (cos(86 * TORAD), 0, sin(86 * TORAD)),
                  Pos(mu=30 - 4 , delta=0, nu=60, eta=0, chi=0,
                      phi=90 + self.zrot, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_pairs_various_zrot_and_yrot0(self):
        for zrot in [0, 2, -2,]:
            self.makes_cases(0, zrot)
            for case_tuple in self.case_generator():
                yield case_tuple
    
class TestCubic_FixedDeltaEtaChi30Mode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'eta': 0, 'delta': 0, 'chi': 30 * TORAD}

    def makes_cases(self, yrot, zrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=120, delta=0, nu=60, eta=0, chi=30,
                      phi=-90, unit='DEG')),
             Pair('010', (0, 1, 0),
                  Pos(mu=120, delta=0, nu=60, eta=0, chi=30,
                      phi=0, unit='DEG')),
             Pair('100-->001', (-sin(30 * TORAD), 0, cos(30 * TORAD)),
                  Pos(mu=30, delta=0, nu=60, eta=0, chi=30,
                      phi=0, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

class TestCubic_FixedGamMuChi90Mode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'mu': 0, NUNAME: 0, 'chi': 90 * TORAD}
        #self.mock_hardware.set_lower_limit('chi', -180.)

    def makes_cases(self, yrot, zrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=0, delta=60, nu=0, eta=120, chi=90,
                      phi=-90 + self.zrot, unit='DEG')),
             Pair('010-->100', (sin(4 * TORAD), cos(4 * TORAD), 0),
                  Pos(mu=0, delta=60, nu=0, eta=120, chi= 90,
                      phi=-4 + self.zrot, unit='DEG')),
             Pair('010', (0, 1, 0),
                  Pos(mu=0, delta=60, nu=0, eta=120, chi=90,
                      phi=self.zrot, unit='DEG')),
             Pair('001', (0, 0, 1),
                  Pos(mu=0, delta=60, nu=0, eta=30, chi=90,
                      phi=0, unit='DEG'), fails=True),  # degenerate case phi||q
             Pair('100-->010', (sin(86 * TORAD), cos(86 * TORAD), 0),
                  Pos(mu=0, delta=60, nu=0, eta=120, chi=90,
                      phi=-90 + 4 + self.zrot, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple

    def test_pairs_various_zrot_and_yrot0(self):
        for zrot in [0, 2, -2,]:
            self.makes_cases(0, zrot)
            for case_tuple in self.case_generator():
                yield case_tuple
    
class TestCubic_FixedGamMuChi30Mode(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.constraints._constrained = {'mu': 0, NUNAME: 0, 'chi': 30 * TORAD}

    def makes_cases(self, yrot, zrot):
        self.zrot = zrot
        self.yrot = yrot
        self.wavelength = 1
        self.cases = (
             Pair('100', (1, 0, 0),
                  Pos(mu=0, delta=60, nu=0, eta=120, chi=30,
                      phi=-90, unit='DEG')),
             Pair('010', (0, 1, 0),
                  Pos(mu=0, delta=60, nu=0, eta=120, chi=30,
                      phi=0, unit='DEG')),
             Pair('100-->010', (sin(30 * TORAD), cos(30 * TORAD), 0),
                  Pos(mu=00, delta=60, nu=0, eta=120, chi=30,
                      phi=-30, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def test_pairs_zrot0_yrot0(self):
        self.makes_cases(0, 0)
        for case_tuple in self.case_generator():
            yield case_tuple

class TestAgainstSpecSixcB16_270608(_BaseTest):
    '''NOTE: copied from test.diffcalc.scenarios.session3'''
    def setup_method(self):
        _BaseTest.setup_method(self)

        U = matrix(((0.997161, -0.062217, 0.042420),
                    (0.062542, 0.998022, -0.006371),
                    (-0.041940, 0.009006, 0.999080)))

        B = matrix(((1.636204, 0, 0),
                    (0, 1.636204, 0),
                    (0, 0, 1.156971)))

        self.UB = U * B
        self.constraints._constrained = {'a_eq_b': None, 'mu': 0, NUNAME: 0}
        self.places = 2  # TODO: the Vlieg code got this to 3 decimal places

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def makes_cases(self, zrot, yrot):
        del zrot, yrot  # not used
        self.wavelength = 1.24
        self.cases = (
            Pair('7_9_13', (0.7, 0.9, 1.3),
                 Pos(mu=0, delta=27.352179, nu=0, eta=13.676090,
                     chi=37.774500, phi=53.965500, unit='DEG')),
            Pair('100', (1, 0, 0),
                 Pos(mu=0, delta=18.580230, nu=0, eta=9.290115,
                     chi=-2.403500, phi=3.589000, unit='DEG')),
            Pair('010', (0, 1, 0),
                 Pos(mu=0, delta=18.580230, nu=0, eta=9.290115,
                     chi=0.516000, phi=93.567000, unit='DEG')),
            Pair('110', (1, 1, 0),
                 Pos(mu=0, delta=26.394192, nu=0, eta=13.197096,
                     chi=-1.334500, phi=48.602000, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def case_generator(self):
        zrot, yrot = 999, 999
        for case in self.cases:
            yield (self._check_angles_to_hkl, case.name, zrot, yrot, case.hkl,
                   case.position, self.wavelength, {})
            test_method = (self._check_hkl_to_angles_fails if case.fails else
                           self._check_hkl_to_angles)
            yield (test_method, case.name, zrot, yrot, case.hkl, case.position,
                   self.wavelength, {})

    def test_hkl_to_angles_given_UB(self):
        self.makes_cases(None, None)  # xrot, yrot unused
        for case_tuple in self.case_generator():
            yield case_tuple


class TestThreeTwoCircleForDiamondI06andI10(_BaseTest):
    """
    This is a three circle diffractometer with only delta and omega axes
    and a chi axis with limited range around 90. It is operated with phi
    fixed and can only reach reflections with l (or z) component.

    The data here is taken from an experiment performed on Diamonds I06
    beamline.
    """

    def setup_method(self):
        _BaseTest.setup_method(self)
        self.constraints._constrained = {'phi': -pi / 2, NUNAME: 0, 'mu': 0}
        self.wavelength = 12.39842 / 1.650

    def _configure_ub(self):
        U = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        B = CrystalUnderTest('xtal', 5.34, 5.34, 13.2, 90, 90, 90).B
        self.mock_ubcalc.UB = U * B

    def testHkl001(self):
        hkl = (0, 0, 1)
        pos = Pos(mu=0, delta=33.07329403295449, nu=0, eta=16.536647016477247,
                  chi=90, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '001', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '001', 999, 999, hkl, pos, self.wavelength, {})

    def testHkl100(self):
        hkl = (1, 0, 0)
        pos = Pos(mu=0, delta=89.42926563609406, nu=0, eta=134.71463281804702,
                  chi=0, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '100', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '100', 999, 999, hkl, pos, self.wavelength, {})

    def testHkl101(self):
        hkl = (1, 0, 1)
        pos = Pos(mu=0, delta=98.74666191021282, nu=0, eta=117.347760720783,
                  chi=90, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '101', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '101', 999, 999, hkl, pos, self.wavelength, {})


class TestThreeTwoCircleForDiamondI06andI10Horizontal(_BaseTest):

    def setup_method(self):
        _BaseTest.setup_method(self)
        self.constraints._constrained = {'phi': -pi / 2, 'delta': 0, 'eta': 0}
        self.wavelength = 12.39842 / 1.650

    def _configure_ub(self):
        U = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        B = CrystalUnderTest('xtal', 5.34, 5.34, 13.2, 90, 90, 90).B
        self.mock_ubcalc.UB = U * B

    def testHkl001(self):
        hkl = (0, 0, 1)
        pos = Pos(mu=16.536647016477247, delta=0, nu=33.07329403295449, eta=0,
                  chi=0, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '001', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '001', 999, 999, hkl, pos, self.wavelength, {})

    @raises(DiffcalcException)  # q || chi
    def testHkl100(self):
        hkl = (1, 0, 0)
        pos = Pos(mu=134.71463281804702, delta=0, nu=89.42926563609406, eta=0,
                  chi=0, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '100', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '100', 999, 999, hkl, pos, self.wavelength, {})

    def testHkl101(self):
        hkl = (1, 0, 1)
        pos = Pos(mu=117.347760720783, delta=0, nu=98.74666191021282, eta=0,
                  chi=0, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '101', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '101', 999, 999, hkl, pos, self.wavelength, {})


class TestThreeTwoCircleForDiamondI06andI10ChiDeltaEta(TestThreeTwoCircleForDiamondI06andI10Horizontal):

    def setup_method(self):
        _BaseTest.setup_method(self)
        self.constraints._constrained = {'phi': -pi / 2, 'chi': 0, 'delta': 0}
        self.wavelength = 12.39842 / 1.650

    @raises(DiffcalcException)  # q || eta
    def testHkl001(self):
        hkl = (0, 0, 1)
        pos = Pos(mu=16.536647016477247, delta=0, nu=33.07329403295449, eta=0,
                  chi=0, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '001', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '001', 999, 999, hkl, pos, self.wavelength, {})

    def testHkl100(self):
        hkl = (1, 0, 0)
        pos = Pos(mu=134.71463281804702, delta=0, nu=89.42926563609406, eta=0,
                  chi=0, phi=-90, unit='DEG')
        self._check_angles_to_hkl(
            '100', 999, 999, hkl, pos, self.wavelength, {})
        self._check_hkl_to_angles(
            '100', 999, 999, hkl, pos, self.wavelength, {})

class TestFixedChiPhiPsiMode_DiamondI07SurfaceNormalHorizontal(_TestCubic):
    """
    The data here is taken from an experiment performed on Diamonds I07
    beamline, obtained using Vlieg's DIF software"""

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        self.mock_hardware.set_upper_limit('delta', 90)
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB
        # Set some random reference vector orientation
        # that won't coincide with the scattering vector direction.
        #self.mock_ubcalc.n_phi = matrix([[0.087867277], [0.906307787], [0.413383038]])
        #self.mock_ubcalc.n_phi = matrix([[0.], [1.], [0.]])

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl001(self):
        self._check((0, 0, 1),  # betaout=30
                    Pos(mu=30, delta=0, nu=60, eta=90, chi=0, phi=0, unit='DEG'), fails=True)

    def testHkl010(self):
        self._check((0, 1, 0),  # betaout=0
                    Pos(mu=0, delta=60, nu=0, eta=120, chi=0, phi=0, unit='DEG'))

    def testHkl011(self):
        self._check((0, 1, 1),  # betaout=30
                    Pos(mu=30, delta=54.7356, nu=90, eta=125.2644, chi=0, phi=0, unit='DEG'))

    def testHkl100(self):
        self._check((1, 0, 0),  # betaout=0
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0, unit='DEG'))

    def testHkl101(self):
        self._check((1, 0, 1),  # betaout=30
                    Pos(mu=30, delta=54.7356, nu=90, eta=35.2644, chi=0, phi=0, unit='DEG'))

    def testHkl110(self):
        self._check((1, 1, 0),  # betaout=0
                    Pos(mu=0, delta=90, nu=0, eta=90, chi=0, phi=0, unit='DEG'))

    def testHkl11nearly0(self):
        self.places = 3
        self._check((1, 1, .0001),  # betaout=0
                    Pos(mu=0.0029, delta=89.9971, nu=90.0058, eta=90, chi=0,
                      phi=0, unit='DEG'))

    def testHkl111(self):
        self._check((1, 1, 1),  # betaout=30
                    Pos(mu=30, delta=54.7356, nu=150, eta=99.7356, chi=0, phi=0, unit='DEG'))

    def testHklover100(self):
        self._check((1.1, 0, 0),  # betaout=0
                    Pos(mu=0, delta=66.7340, nu=0, eta=33.3670, chi=0, phi=0, unit='DEG'))

    def testHklunder100(self):
        self._check((.9, 0, 0),  # betaout=0
                    Pos(mu=0, delta=53.4874, nu=0, eta=26.7437, chi=0, phi=0, unit='DEG'))

    def testHkl788(self):
        self._check((.7, .8, .8),  # betaout=23.5782
                    Pos(mu=23.5782, delta=59.9980, nu=76.7037, eta=84.2591,
                      chi=0, phi=0, unit='DEG'))

    def testHkl789(self):
        self._check((.7, .8, .9),  # betaout=26.7437
                    Pos(mu=26.74368, delta=58.6754, nu=86.6919, eta=85.3391,
                      chi=0, phi=0, unit='DEG'))

    def testHkl7810(self):
        self._check((.7, .8, 1),  # betaout=30
                    Pos(mu=30, delta=57.0626, nu=96.86590, eta=86.6739, chi=0,
                      phi=0, unit='DEG'))


class SkipTestFixedChiPhiPsiModeSurfaceNormalVertical(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0,
                                         'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl001(self):
        self._check((0, 0, 1),  # betaout=30
                    Pos(mu=30, delta=0, nu=60, eta=90, chi=0, phi=0, unit='DEG'), fails=True)

    def testHkl010(self):
        self._check((0, 1, 0),  # betaout=0
                    Pos(mu=120, delta=0, nu=60, eta=0, chi=90, phi=0, unit='DEG'))

    def testHkl011(self):
        self._check((0, 1, 1),  # betaout=30
                    Pos(mu=30, delta=54.7356, nu=90, eta=125.2644, chi=0, phi=0, unit='DEG'))

    def testHkl100(self):
        self._check((1, 0, 0),  # betaout=0
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0, unit='DEG'))

    def testHkl101(self):
        self._check((1, 0, 1),  # betaout=30
                    Pos(mu=30, delta=54.7356, nu=90, eta=35.2644, chi=0, phi=0, unit='DEG'))

    def testHkl110(self):
        self._check((1, 1, 0),  # betaout=0
                    Pos(mu=0, delta=90, nu=0, eta=90, chi=0, phi=0, unit='DEG'))

    def testHkl11nearly0(self):
        self.places = 3
        self._check((1, 1, .0001),  # betaout=0
                    Pos(mu=0.0029, delta=89.9971, nu=90.0058, eta=90, chi=0,
                      phi=0, unit='DEG'))

    def testHkl111(self):
        self._check((1, 1, 1),  # betaout=30
                    Pos(mu=30, delta=54.7356, nu=150, eta=99.7356, chi=0, phi=0, unit='DEG'))

    def testHklover100(self):
        self._check((1.1, 0, 0),  # betaout=0
                    Pos(mu=0, delta=66.7340, nu=0, eta=33.3670, chi=0, phi=0, unit='DEG'))

    def testHklunder100(self):
        self._check((.9, 0, 0),  # betaout=0
                    Pos(mu=0, delta=53.4874, nu=0, eta=26.7437, chi=0, phi=0, unit='DEG'))

    def testHkl788(self):
        self._check((.7, .8, .8),  # betaout=23.5782
                    Pos(mu=23.5782, delta=59.9980, nu=76.7037, eta=84.2591,
                      chi=0, phi=0, unit='DEG'))

    def testHkl789(self):
        self._check((.7, .8, .9),  # betaout=26.7437
                    Pos(mu=26.74368, delta=58.6754, nu=86.6919, eta=85.3391,
                      chi=0, phi=0, unit='DEG'))

    def testHkl7810(self):
        self._check((.7, .8, 1),  # betaout=30
                    Pos(mu=30, delta=57.0626, nu=96.86590, eta=86.6739, chi=0,
                      phi=0, unit='DEG'))

class SkipTestFixedChiPhiPsiModeSurfaceNormalVerticalI16(_TestCubic):
    # testing with Chris N. for pre christmas 2012 i16 experiment

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.mock_hardware.set_lower_limit('nu', 0)
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0,
                                         'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
#        self._check_angles_to_hkl(
#            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl_1_1_0(self):
        self._check((1, 1, 0.001),  # betaout=0
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0, unit='DEG'))
        #(-89.9714,  89.9570,  90.0382,  90.0143,  90.0000,  0.0000)

    def testHkl_1_1_05(self):
        self._check((1, 1, 0.5),  # betaout=0
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0, unit='DEG'))

    def testHkl_1_1_1(self):
        self._check((1, 1, 1),  # betaout=0
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0, unit='DEG'))
        #    (-58.6003,  42.7342,  132.9004,  106.3249,  90.0000,  0.0000

    def testHkl_1_1_15(self):
        self._check((1, 1, 1.5),  # betaout=0
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0, unit='DEG'))


class TestConstrain3Sample_ChiPhiEta(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0,
                                         'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB
        # Set some random reference vector orientation
        # that won't coincide with the scattering vector direction.
        #self.mock_ubcalc.n_phi = matrix([[0.087867277], [0.906307787], [0.413383038]])

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl_all0_001(self):
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0}
        self._check((0, 0, 1),
                    Pos(mu=30, delta=0, nu=60, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_all0_010(self):
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0}
        self._check((0, 1, 0),
                    Pos(mu=120, delta=0, nu=60, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_all0_011(self):
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0}
        self._check((0, 1, 1),
                    Pos(mu=90, delta=0, nu=90, eta=0, chi=0, phi=0, unit='DEG'))
        
    def testHkl_phi30_100(self):
        self.constraints._constrained = {'chi': 0, 'phi': 30 * TORAD, 'eta': 0}
        self._check((1, 0, 0),
                    Pos(mu=0, delta=60, nu=0, eta=0, chi=0, phi=30, unit='DEG'))
        
    def testHkl_eta30_100(self):
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 30 * TORAD}
        self._check((1, 0, 0),
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=0, phi=0, unit='DEG'))
        
    def testHkl_phi90_110(self):
        self.constraints._constrained = {'chi': 0, 'phi': 90 * TORAD, 'eta': 0}
        self._check((1, 1, 0),
                    Pos(mu=0, delta=90, nu=0, eta=0, chi=0, phi=90, unit='DEG'))
        
    def testHkl_eta90_110(self):
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 90 * TORAD}
        self._check((1, 1, 0),
                    Pos(mu=0, delta=90, nu=0, eta=90, chi=0, phi=0, unit='DEG'))

    def testHkl_all0_1(self):
        self.mock_hardware.set_upper_limit('delta', 91)
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0 * TORAD}
        self._check((.01, .01, .1),
                    Pos(mu=8.6194, delta=0.5730, nu=5.7607, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_all0_2(self):
        self.mock_hardware.set_upper_limit('delta', 91)
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0 * TORAD}
        self._check((0, 0, .1),
                    Pos(mu=2.8660, delta=0, nu=5.7320, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_all0_3(self):
        self.mock_hardware.set_upper_limit('delta', 91)
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0 * TORAD}
        self._check((.1, 0, .01),
                    Pos(mu=30.3314, delta=5.7392, nu= 0.4970, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_show_all_solutionsall0_3(self):
        self.mock_hardware.set_upper_limit('delta', 91)
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0 * TORAD}
        self._check((.1, 0, .01),
                    Pos(mu=30.3314, delta=5.7392, nu= 0.4970, eta=0, chi=0, phi=0, unit='DEG'))
        #print self.calc.hkl_to_all_angles(.1, 0, .01, 1)

    def testHkl_all0_010to001(self):
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'eta': 0}
        self._check((0, cos(4 * TORAD), sin(4 * TORAD)),
                    Pos(mu=120-4, delta=0, nu=60, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_1(self):
        self.wavelength = .1
        self.constraints._constrained = {'chi': 0, 'phi': 0 * TORAD, 'eta': 0}
        self._check((0, 0, 1),
                    Pos(mu=2.8660, delta=0, nu=5.7320, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_2(self):
        self.wavelength = .1
        self.constraints._constrained = {'chi': 0, 'phi': 0 * TORAD, 'eta': 0}
        self._check((0, 0, 1),
                    Pos(mu=2.8660, delta=0, nu=5.7320, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_3(self):
        self.mock_hardware.set_upper_limit('delta', 91)
        self.wavelength = .1
        self.constraints._constrained = {'chi': 0, 'phi': 0 * TORAD, 'eta': 0}
        self._check((1, 0, .1),
                    Pos(mu= 30.3314, delta=5.7392, nu= 0.4970, eta=0, chi=0, phi=0, unit='DEG'))


class TestConstrain3Sample_MuChiPhi(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0,
                                         'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB
        # Set some random reference vector orientation
        # that won't coincide with the scattering vector direction.
        #self.mock_ubcalc.n_phi = matrix([[0.087867277], [0.906307787], [0.413383038]])

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl_all0_001(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0, 'mu': 0}
        self._check((0, 0, 1),
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=90, phi=0, unit='DEG'))

    def testHkl_all0_010(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0, 'mu': 0}
        self._check((0, 1, 0),
                    Pos(mu=0, delta=60, nu=0, eta=120, chi=90, phi=0, unit='DEG'))

    def testHkl_all0_011(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0, 'mu': 0}
        self._check((0, 1, 1),
                    Pos(mu=0, delta=90, nu=0, eta=90, chi=90, phi=0, unit='DEG'))
        
    def testHkl_etam60_100(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 90 * TORAD, 'mu': 0}
        self._check((1, 0, 0),
                    Pos(mu=0, delta=60, nu=0, eta=-60, chi=90, phi=90, unit='DEG'))
        
    def testHkl_eta90_m110(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0, 'mu': 90 * TORAD}
        self._check((-1, 1, 0),
                    Pos(mu=90, delta=90, nu=0, eta=90, chi=90, phi=0, unit='DEG'), fails=True)
        
    def testHkl_eta0_101(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 90 * TORAD, 'mu': 0}
        self._check((1, 0, 1),
                    Pos(mu=0, delta=90, nu=0, eta=0, chi=90, phi=90, unit='DEG'))
        
    def testHkl_all0_010to100(self):
        self.constraints._constrained = {'chi': 0, 'phi': 0, 'mu': 0}
        self._check((sin(4 * TORAD), cos(4 * TORAD), 0),
                    Pos(mu=0, delta=60, nu=0, eta=120 - 4, chi=0, phi=0, unit='DEG'))


class TestConstrain3Sample_MuEtaChi(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        self.constraints._constrained = {'chi': 90 * TORAD, 'eta': 0,
                                         'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB
        # Set some random reference vector orientation
        # that won't coincide with the scattering vector direction.
        #self.mock_ubcalc.n_phi = matrix([[0.087867277], [0.906307787], [0.413383038]])

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl_all0_001(self):
        self.constraints._constrained = {'eta': 30 * TORAD, 'chi': 90 * TORAD, 'mu': 0}
        self._check((0, 0, 1),
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=90, phi=0, unit='DEG'), fails=True)

    def testHkl_all0_010(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'eta': 120 * TORAD, 'mu': 0}
        self._check((0, 1, 0),
                    Pos(mu=0, delta=60, nu=0, eta=120, chi=90, phi=0, unit='DEG'))

    def testHkl_all0_011(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'eta': 90 * TORAD, 'mu': 0}
        self._check((0, 1, 1),
                    Pos(mu=0, delta=90, nu=0, eta=90, chi=90, phi=0, unit='DEG'), fails=True)
        
    def testHkl_phi90_100(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'eta': -60 * TORAD, 'mu': 0}
        self._check((1, 0, 0),
                    Pos(mu=0, delta=60, nu=0, eta=-60, chi=90, phi=90, unit='DEG'))
        
    def testHkl_phi0_m110(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'eta': 90 * TORAD, 'mu': 90 * TORAD}
        self._check((-1, 1, 0),
                    Pos(mu=90, delta=90, nu=0, eta=90, chi=90, phi=0, unit='DEG'))
        
    def testHkl_phi90_101(self):
        self.constraints._constrained = {'chi': 90 * TORAD, 'eta': 0, 'mu': 0}
        self._check((1, 0, 1),
                    Pos(mu=0, delta=90, nu=0, eta=0, chi=90, phi=90, unit='DEG'))
        
    def testHkl_all0_010to100(self):
        self.constraints._constrained = {'chi': 0, 'eta': 0, 'mu': 0}
        self._check((sin(4 * TORAD), cos(4 * TORAD), 0),
                    Pos(mu=0, delta=60, nu=0, eta=0, chi=0, phi=120 - 4, unit='DEG'))


class TestConstrain3Sample_MuEtaPhi(_TestCubic):

    def setup_method(self):
        _TestCubic.setup_method(self)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        self.constraints._constrained = {'chi': 90 * TORAD, 'phi': 0,
                                         'a_eq_b': None}
        self.wavelength = 1
        self.UB = I * 2 * pi
        self.places = 4

        self.mock_hardware.set_lower_limit('mu', None)
        self.mock_hardware.set_lower_limit('eta', None)
        self.mock_hardware.set_lower_limit('chi', None)

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False):
        self._check_angles_to_hkl(
            '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def testHkl_all0_001(self):
        self.constraints._constrained = {'eta': 0, 'phi': 0, 'mu': 30 * TORAD}
        self._check((0, 0, 1),
                    Pos(mu=30, delta=0, nu=60, eta=0, chi=0, phi=0, unit='DEG'))

    def testHkl_all0_010(self):
        self.constraints._constrained = {'eta': 120 * TORAD, 'phi': 0, 'mu': 0}
        self._check((0, 1, 0),
                    Pos(mu=0, delta=60, nu=0, eta=120, chi=90, phi=0, unit='DEG'), fails=True)

    def testHkl_all0_011(self):
        self.constraints._constrained = {'eta': 90 * TORAD, 'phi': 0, 'mu': 0}
        self._check((0, 1, 1),
                    Pos(mu=0, delta=90, nu=0, eta=90, chi=90, phi=0, unit='DEG'))
        
    def testHkl_chi90_100(self):
        self.constraints._constrained = {'eta': -60 * TORAD, 'phi': 90 * TORAD, 'mu': 0}
        self._check((1, 0, 0),
                    Pos(mu=0, delta=60, nu=0, eta=-60, chi=90, phi=90, unit='DEG'), fails=True)
        
    def testHkl_chi90_m110(self):
        self.constraints._constrained = {'eta': 90 * TORAD, 'phi': 0, 'mu': 90 * TORAD}
        self._check((-1, 1, 0),
                    Pos(mu=90, delta=90, nu=0, eta=90, chi=90, phi=0, unit='DEG'))
        
    def testHkl_chi90_101(self):
        self.constraints._constrained = {'eta': 0, 'phi': 90 * TORAD, 'mu': 0}
        self._check((1, 0, 1),
                    Pos(mu=0, delta=90, nu=0, eta=0, chi=90, phi=90, unit='DEG'), fails=True)
        
    def testHkl_all0_010to100(self):
        self.constraints._constrained = {'eta': 30 * TORAD, 'phi': 0, 'mu': 0}
        self._check((sin(4 * TORAD), 0, cos(4 * TORAD)),
                    Pos(mu=0, delta=60, nu=0, eta=30, chi=90 - 4, phi=0, unit='DEG'))


class TestHorizontalDeltaNadeta0_JiraI16_32_failure(_BaseTest):
    """
    The data here is taken from a trial experiment which failed. Diamond's internal Jira: 
    http://jira.diamond.ac.uk/browse/I16-32"""

    def setup_method(self):
        _BaseTest.setup_method(self)
        self.mock_hardware.set_lower_limit(NUNAME, 0)
        
        self.wavelength = 12.39842 / 8
        self.UB = matrix([[ -1.46410390e+00,  -1.07335571e+00,   2.44799214e-03],
                          [  3.94098508e-01,  -1.07091934e+00,  -6.41132943e-04],
                          [  7.93297438e-03,   4.01315826e-03,   4.83650166e-01]])
        self.places = 3

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False, skip_test_pair_verification=False):
        if not skip_test_pair_verification:
            self._check_angles_to_hkl(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def test_hkl_bisecting_works_okay_on_i16(self):
        self.constraints._constrained = {'delta': 0, 'a_eq_b': None, 'eta': 0}
        self._check([-1.1812112493619709, -0.71251524866987204, 5.1997083010199221],
                    Pos(mu=26, delta=0, nu=52, eta=0, chi=45.2453, phi=186.6933-360, unit='DEG'), fails=False)

    def test_hkl_psi90_works_okay_on_i16(self):
        # This is failing here but on the live one. Suggesting some extreme sensitivity?
        self.constraints._constrained = {'delta': 0, 'psi': -90 * TORAD, 'eta': 0}
        self._check([-1.1812112493619709, -0.71251524866987204, 5.1997083010199221],
                    Pos(mu=26, delta=0, nu=52, eta=0, chi=45.2453, phi=186.6933-360, unit='DEG'), fails=False)
        
    def test_hkl_alpha_17_9776_used_to_fail(self):
        # This is failing here but on the live one. Suggesting some extreme sensitivity?
        self.constraints._constrained = {'delta': 0, 'alpha': 17.9776 * TORAD, 'eta': 0}
        self._check([-1.1812112493619709, -0.71251524866987204, 5.1997083010199221],
                    Pos(mu=26, delta=0, nu=52, eta=0, chi=45.2453, phi=186.6933-360, unit='DEG'), fails=False)

    def test_hkl_alpha_17_9776_failing_after_bigger_small(self):
        # This is failing here but on the live one. Suggesting some extreme sensitivity?
        self.constraints._constrained = {'delta': 0, 'alpha': 17.8776 * TORAD, 'eta': 0}
        self._check([-1.1812112493619709, -0.71251524866987204, 5.1997083010199221],
                    Pos(mu=25.85, delta=0, nu=52, eta=0, chi=45.2453, phi=-173.518, unit='DEG'), fails=False)
  
#skip_test_pair_verification

def posFromI16sEuler(phi, chi, eta, mu, delta, gamma):
    return Pos(mu, delta, gamma, eta, chi, phi, unit='DEG')


class TestAnglesToHkl_I16Examples():

    def __init__(self):
        self.UB1 = matrix((
           (0.9996954135095477, -0.01745240643728364, -0.017449748351250637),
           (0.01744974835125045, 0.9998476951563913, -0.0003045864904520898),
           (0.017452406437283505, -1.1135499981271473e-16, 0.9998476951563912))
            ) * (2 * pi)
        self.WL1 = 1  # Angstrom

    def test_anglesToHkl_mu_0_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1), [1, 0, 0])

    def test_anglesToHkl_mu_0_gam_10(self):
        pos = posFromI16sEuler(1, 1, 30, 0, 60, 10).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1),
                 [1.00379806, -0.006578435, 0.08682408])

    def test_anglesToHkl_mu_10_gam_0(self):
        pos = posFromI16sEuler(1, 1, 30, 10, 60, 0).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1),
                 [0.99620193, 0.0065784359, 0.08682408])

    def test_anglesToHkl_arbitrary(self):
        pos = posFromI16sEuler(1.9, 2.9, 30.9, 0.9, 60.9, 2.9).inRadians()
        arrayeq_(youAnglesToHkl(pos, self.WL1, self.UB1),
                 [1.01174189, 0.02368622, 0.06627361])


class TestAnglesToHkl_I16Numerical(_BaseTest):

    def setup_method(self):
        _BaseTest.setup_method(self)

        self.UB = matrix((
           (1.11143,       0,       0),
           (      0, 1.11143,       0),
           (      0,       0, 1.11143))
            )

        self.constraints._constrained = {'mu':0, NUNAME: 0, 'phi': 0}
        self.wavelength = 1.
        self.places = 6

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB
        self.mock_ubcalc.n_phi = matrix([[0], [0], [1]])


    def _check(self, testname, hkl, pos, virtual_expected={}, fails=False, skip_test_pair_verification=False):
        if not skip_test_pair_verification:
            self._check_angles_to_hkl(
                testname, 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                testname, 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                testname, 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def test_hkl_to_angles_given_UB(self):
        self._check('I16_numeric', [2, 0, 0.000001],
                     posFromI16sEuler(0, 0.000029, 10.188639, 0, 20.377277, 0), fails=False)
        self._check('I16_numeric', [2, 0.000001, 0],
                     posFromI16sEuler(0, 0, 10.188667, 0, 20.377277, 0), fails=False)


class TestAnglesToHkl_I16GaAsExample(_BaseTest):

    def setup_method(self):
        _BaseTest.setup_method(self)

        self.UB = matrix((
           (-0.78935,   0.78234,   0.01191),
           (-0.44391,  -0.46172,   0.90831),
           ( 0.64431,   0.64034,   0.64039))
            )

        self.constraints._constrained = {'qaz': 90. * TORAD, 'alpha': 11. * TORAD, 'mu': 0.}
        self.wavelength = 1.239842
        self.places = 4

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB

    def _check(self, hkl, pos, virtual_expected={}, fails=False, skip_test_pair_verification=False):
        if not skip_test_pair_verification:
            self._check_angles_to_hkl(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        if fails:
            self._check_hkl_to_angles_fails(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)
        else:
            self._check_hkl_to_angles(
                '', 999, 999, hkl, pos, self.wavelength, virtual_expected)

    def test_hkl_to_angles_given_UB(self):
        self._check([1., 1., 1.],
                     posFromI16sEuler(10.7263, 89.8419, 11.0000, 0., 21.8976, 0.), fails=False)
        self._check([0., 0., 2.],
                     posFromI16sEuler(81.2389, 35.4478, 19.2083, 0., 25.3375, 0.), fails=False)


class FourCircleI21(YouGeometry):
    """For a diffractometer with angles:
          delta, eta, chi, phi
    """
    def __init__(self, beamline_axes_transform=None):
        YouGeometry.__init__(self, 'fourc', {'mu': 0, NUNAME: 0}, beamline_axes_transform)

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        delta_phys, eta_phys, chi_phys, phi_phys = physical_angle_tuple
        return Pos(0, delta_phys, 0, eta_phys, 90 - chi_phys, phi_phys, 'DEG')

    def internal_position_to_physical_angles(self, internal_position):
        clone_position = internal_position.clone()
        clone_position.changeToDegrees()
        _, delta_phys, _, eta_phys, chi_phys, phi_phys = clone_position.totuple()
        return delta_phys, eta_phys, 90 - chi_phys, phi_phys


class Test_I21ExamplesUB(_BaseTest):
    '''NOTE: copied from test.diffcalc.scenarios.session3'''

    def setup_method(self):
        _BaseTest.setup_method(self)

        self.i21_geometry = FourCircleI21(beamline_axes_transform = matrix('0 0 1; 0 1 0; 1 0 0'))
        settings.geometry = self.i21_geometry
        names = ['delta', 'eta', 'chi', 'phi']
        self.mock_hardware = DummyHardwareAdapter(names)
        settings.hardware = self.mock_hardware
        self.constraints = YouConstraintManager()
        self.calc = YouHklCalculator(self.mock_ubcalc, self.constraints)

        U = matrix(((1.0,  0., 0.),
                    (0.0, 0.18482, -0.98277),
                    (0.0, 0.98277,  0.18482)))

        B = matrix(((1.66222,     0.0,     0.0),
                    (    0.0, 1.66222,     0.0),
                    (    0.0,     0.0, 0.31260)))

        self.UB = U * B

        self.mock_hardware.set_lower_limit('delta', 0)
        self.mock_hardware.set_upper_limit('delta', 180.0)
        self.mock_hardware.set_lower_limit('eta', 0)
        self.mock_hardware.set_upper_limit('eta', 150)
        self.mock_hardware.set_lower_limit('chi', -41)
        self.mock_hardware.set_upper_limit('chi', 36)
        self.mock_hardware.set_lower_limit('phi', -100)
        self.mock_hardware.set_upper_limit('phi', 100)
        self.mock_hardware.set_cut('eta', 0)
        self.mock_hardware.set_cut('phi', -180)
        self.constraints._constrained = {'psi': 10 * TORAD, 'mu': 0, NUNAME: 0}
        self.wavelength = 12.39842 / .650
        self.places = 5

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB
        self.mock_ubcalc.n_phi = matrix([[0], [0.], [1.]])

    def makes_cases(self, zrot, yrot):
        del zrot, yrot  # not used
        self.cases = (
            Pair('0_0.2_0.25', (0.0, 0.2, 0.25),
                 Pos(mu=0, delta=62.44607, nu=0, eta=28.68407,
                     chi=90.0 - 0.44753, phi=-9.99008, unit='DEG')),
            Pair('0.25_0.2_0.1', (0.25, 0.2, 0.1),
                 Pos(mu=0, delta=108.03033, nu=0, eta=3.03132,
                     chi=90 - 7.80099, phi=87.95201, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def case_generator(self):
        zrot, yrot = 999, 999
        for case in self.cases:
            yield (self._check_angles_to_hkl, case.name, zrot, yrot, case.hkl,
                   case.position, self.wavelength, {})
            test_method = (self._check_hkl_to_angles_fails if case.fails else
                           self._check_hkl_to_angles)
            yield (test_method, case.name, zrot, yrot, case.hkl, case.position,
                   self.wavelength, {})

    def test_hkl_to_angles_given_UB(self):
        self.makes_cases(None, None)  # xrot, yrot unused
        for case_tuple in self.case_generator():
            yield case_tuple

class SkipTest_FixedAlphaMuChiSurfaceNormalHorizontal(_BaseTest):
    '''NOTE: copied from test.diffcalc.scenarios.session3'''
    def setup_method(self):
        _BaseTest.setup_method(self)

        U = matrix(((-0.71022,  0.70390, 0.01071),
                    (-0.39941, -0.41543, 0.81725),
                    (0.57971, 0.57615,  0.57618)))

        B = matrix(((1.11143,     0.0,     0.0),
                    (    0.0, 1.11143,     0.0),
                    (    0.0,     0.0, 1.11143)))

        self.UB = U * B

        self.constraints._constrained = {'alpha': 12., 'mu': 0, 'chi': 0}
        self.wavelength = 1.
        self.places = 5

    def _configure_ub(self):
        self.mock_ubcalc.UB = self.UB
        self.mock_ubcalc.n_phi = matrix([[0.], [0.], [1.]])

    def makes_cases(self, zrot, yrot):
        del zrot, yrot  # not used
        self.cases = (
            Pair('0_0_0.25', (2.0, 2.0,  0.),
                 Pos(mu=0, delta=79.85393, nu=0, eta=39.92540,
                     chi=90.0, phi=0.0, unit='DEG')),
            #Pair('0.25_0.25_0', (0.25, 0.25, 0.0),
            #     Pos(mu=0, delta=27.352179, nu=0, eta=13.676090,
            #         chi=37.774500, phi=53.965500, unit='DEG')),
            )
        self.case_dict = {}
        for case in self.cases:
            self.case_dict[case.name] = case

    def case_generator(self):
        zrot, yrot = 999, 999
        for case in self.cases:
            yield (self._check_angles_to_hkl, case.name, zrot, yrot, case.hkl,
                   case.position, self.wavelength, {})
            test_method = (self._check_hkl_to_angles_fails if case.fails else
                           self._check_hkl_to_angles)
            yield (test_method, case.name, zrot, yrot, case.hkl, case.position,
                   self.wavelength, {})

    def test_hkl_to_angles_given_UB(self):
        self.makes_cases(None, None)  # xrot, yrot unused
        for case_tuple in self.case_generator():
            yield case_tuple
