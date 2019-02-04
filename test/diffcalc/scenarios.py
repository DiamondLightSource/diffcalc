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

from datetime import datetime
from math import asin, sin, cos, atan2

from diffcalc.ub.reflections import _Reflection
from diffcalc.hkl.vlieg.geometry import VliegPosition
from diffcalc.hkl.you.geometry import YouPosition
from diffcalc.hkl.you.calc import sign
from diffcalc.util import TORAD, TODEG


class YouPositionScenario(YouPosition):
    """Convert six-circle Vlieg diffractometer angles into 4S+2D You geometry"""
    def __init__(self, alpha=None, delta=None, gamma=None, omega=None,
                 chi=None, phi=None):
        self.mu = alpha
        self.eta = omega
        self.chi = chi
        self.phi = phi
        self.unit = 'DEG'
        asin_delta = asin(sin(delta*TORAD) * cos(gamma*TORAD))*TODEG  # Eq.(83)
        vals_delta = [asin_delta, 180. - asin_delta]
        idx, _ = min([(i, abs(delta - d)) for i, d in enumerate(vals_delta)], key=lambda x: x[1])
        self.delta = vals_delta[idx]
        sgn = sign(cos(self.delta * TORAD))
        self.nu = atan2(sgn*(cos(delta*TORAD)*cos(gamma*TORAD)*sin(alpha*TORAD) + cos(alpha*TORAD)*sin(gamma*TORAD)),
                        sgn*(cos(delta*TORAD)*cos(gamma*TORAD)*cos(alpha*TORAD) - sin(alpha*TORAD)*sin(gamma*TORAD)))*TODEG   # Eq.(84)


class SessionScenario:
    """
    A test scenario. The test case must have __name, lattice and bmatrix set
    and if umatrix is set then so must ref 1 and ref 2. Matrices should be 3*3
    python arrays of lists and ref1 and ref2 in the format (h, k, l, position,
    energy, tag)."""

    def __init__(self):
        self.name = None
        self.lattice = None
        self.bmatrix = None
        self.ref1 = None
        self.ref2 = None
        self.umatrix = None
        self.calculations = []  # CalculationScenarios

    def __str__(self):
        toReturn = "\nTestScenario:"
        toReturn += "\n     name: " + self.name
        toReturn += "\n  lattice:" + str(self.lattice)
        toReturn += "\n  bmatrix:" + str(self.bmatrix)
        toReturn += "\n     ref1:" + str(self.ref1)
        toReturn += "\n     ref2:" + str(self.ref2)
        toReturn += "\n  umatrix:" + str(self.umatrix)
        return toReturn


class CalculationScenario:
    """
    Used as part of a test scenario. A UB matrix appropriate for this
    calcaultion will have been calculated or loaded
    """
    def __init__(self, tag, package, mode, energy, modeToTest, modeNumber):
        self.tag = tag
        self.package = package
        self.mode = mode
        self.energy = energy
        self.wavelength = 12.39842 / energy
        self.modeToTest = modeToTest
        self.modeNumber = modeNumber
        self.hklList = None  # hkl triples
        self.posList = []
        self.paramList = []


def sessions(P=VliegPosition):
    ############################ SESSION0 ############################
    # From the dif_init.mat next to dif_dos.exe on Vlieg'session2 cd
    #session2 = SessionScenario()
    #session2.name = 'latt1'
    #session2.lattice = ([4.0004, 4.0004, 2.270000, 90, 90, 90])
    #session2.bmatrix = (((1.570639, 0, 0) ,(0.0, 1.570639, 0) ,
    #                      (0.0, 0.0, 2.767923)))
    #self.scenarios.append(session2)
    
    
    ############################ SESSION1 ############################
    # From b16 on 27June2008 (From Chris Nicklin)
    
    session1 = SessionScenario()
    session1.name = "b16_270608"
    session1.time = datetime.now()
    session1.lattice = ((3.8401, 3.8401, 5.43072, 90, 90, 90))
    session1.bmatrix = (((1.636204, 0, 0), (0, 1.636204, 0), (0, 0, 1.156971)))
    session1.ref1 = _Reflection(1, 0, 1.0628,
                               P(5.000, 22.790, 0.000, 1.552, 22.400, 14.255),
                               10, 'ref1', session1.time)
    session1.ref2 = _Reflection(0, 1, 1.0628,
                               P(5.000, 22.790, 0.000, 4.575, 24.275, 101.320),
                               10, 'ref2', session1.time)
    session1.umatrix = ((0.997161, -0.062217, 0.042420),
                   (0.062542, 0.998022, -0.006371),
                   (-0.041940, 0.009006, 0.999080))
    session1.ref1calchkl = (1, 0, 1.0628)  # Must match the guessed value!
    session1.ref2calchkl = (-0.0329, 1.0114, 1.04)
    
    
    ############################ SESSION2 ############################
    # cubic crystal from bliss tutorial
    session2 = SessionScenario()
    session2.name = "cubic_from_bliss_tutorial"
    session2.time = datetime.now()
    session2.lattice = ((1.54, 1.54, 1.54, 90, 90, 90))
    session2.ref1 = _Reflection(1, 0, 0, P(0, 60, 0, 30, 0, 0),
                               12.39842 / 1.54, 'ref1', session2.time)
    session2.ref2 = _Reflection(0, 1, 0, P(0, 60, 0, 30, 0, -90),
                               12.39842 / 1.54, 'ref2', session2.time)
    session2.bmatrix = (((4.07999, 0, 0), (0, 4.07999, 0), (0, 0, 4.07999)))
    session2.umatrix = (((1, 0, 0), (0, -1, 0), (0, 0, -1)))
    session2.ref1calchkl = (1, 0, 0)  # Must match the guessed value!
    session2.ref2calchkl = (0, 1, 0)
    # sixc-0a : fixed omega = 0
    c = CalculationScenario('sixc-0a', 'sixc', '0', 12.39842 / 1.54, '4cBeq', 1)
    c.alpha = 0
    c.gamma = 0
    c.w = 0
    #c.hklList=((0.7, 0.9, 1.3), (1,0,0), (0,1,0), (1, 1, 0))
    c.hklList = ((0.7, 0.9, 1.3),)
    c.posList.append(
        P(0.000000, 119.669750, 0.000000, 59.834875, -48.747500, 307.874983651098))
    #c.posList.append(P(0.000000, 60.000000, 0.000000, 30.000, 0.000000, 0.000000))
    #c.posList.append(P(0.000000, 60.000000, 0.000000, 30.000, 0.000000, -90.0000))
    #c.posList.append(P(0.000000, 90.000000, 0.000000, 45.000, 0.000000, -45.0000))
    session2.calculations.append(c)
    
    
    ############################ SESSION3 ############################
    # AngleCalc scenarios from SPEC sixc. using crystal and alignment
    session3 = SessionScenario()
    session3.name = "spec_sixc_b16_270608"
    session3.time = datetime.now()
    session3.lattice = ((3.8401, 3.8401, 5.43072, 90, 90, 90))
    session3.bmatrix = (((1.636204, 0, 0), (0, 1.636204, 0), (0, 0, 1.156971)))
    session3.umatrix = ((0.997161, -0.062217, 0.042420),
                   (0.062542, 0.998022, -0.006371),
                   (-0.041940, 0.009006, 0.999080))
    session3.ref1 = _Reflection(1, 0, 1.0628,
                               P(5.000, 22.790, 0.000, 1.552, 22.400, 14.255),
                               12.39842 / 1.24, 'ref1', session3.time)
    session3.ref2 = _Reflection(0, 1, 1.0628,
                               P(5.000, 22.790, 0.000, 4.575, 24.275, 101.320),
                               12.39842 / 1.24, 'ref2', session3.time)
    session3.ref1calchkl = (1, 0, 1.0628)
    session3.ref2calchkl = (-0.0329, 1.0114, 1.04)
    # sixc-0a : fixed omega = 0
    ac = CalculationScenario('sixc-0a', 'sixc', '0', 12.39842 / 1.24, '4cBeq', 1)
    ac.alpha = 0
    ac.gamma = 0
    ac.w = 0
    ### with 'omega_low':-90, 'omega_high':270, 'phi_low':-180, 'phi_high':180
    ac.hklList = []
    ac.hklList.append((0.7, 0.9, 1.3))
    ac.posList.append(P(0.0, 27.352179, 0.000000, 13.676090, 37.774500, 53.965500))
    ac.paramList.append({'Bin': 8.3284, 'Bout': 8.3284, 'rho': 36.5258,
                         'eta': 0.1117, 'twotheta': 27.3557})
    
    ac.hklList.append((1, 0, 0))
    ac.posList.append(P(0., 18.580230, 0.000000, 9.290115, -2.403500, 3.589000))
    ac.paramList.append({'Bin': -0.3880, 'Bout': -0.3880, 'rho': -2.3721,
                         'eta': -0.0089, 'twotheta': 18.5826})
    
    ac.hklList.append((0, 1, 0))
    ac.posList.append(P(0., 18.580230, 0.000000, 9.290115, 0.516000, 93.567000))
    ac.paramList.append({'Bin':  0.0833, 'Bout':  0.0833, 'rho':  0.5092,
                         'eta': -0.0414, 'twotheta': 18.5826})
    
    ac.hklList.append((1, 1, 0))
    ac.posList.append(P(0., 26.394192, 0.000000, 13.197096, -1.334500, 48.602000))
    ac.paramList.append({'Bin': -0.3047, 'Bout': -0.3047, 'rho': -1.2992,
                         'eta': -0.0351, 'twotheta': 26.3976})
    
    session3.calculations.append(ac)
    
    ############################ SESSION4 ############################
    # test crystal
    
    session4 = SessionScenario()
    session4.name = "test_orth"
    session4.time = datetime.now()
    session4.lattice = ((1.41421, 1.41421, 1.00000, 90, 90, 90))
    session4.system = 'Orthorhombic'
    session4.bmatrix = (((4.44288, 0, 0), (0, 4.44288, 0), (0, 0, 6.28319)))
    session4.ref1 = _Reflection(0, 1, 2,
                               P(0.0000, 122.4938, 0.0000, 80.7181, 90.0000, -45.0000),
                               15., 'ref1', session4.time)
    session4.ref2 = _Reflection(1, 0, 2,
                               P(0.0000, 122.4938, 0.000, 61.2469, 70.5288, -45.0000),
                               15, 'ref2', session4.time)
    session4.ref3 = _Reflection(1, 0, 1,
                               P(0.0000, 60.8172, 0.000, 30.4086, 54.7356, -45.0000),
                               15, 'ref3', session4.time)
    session4.ref4 = _Reflection(1, 1, 2,
                               P(0.0000, 135.0736, 0.000, 67.5368, 63.4349, 0.0000),
                               15, 'ref4', session4.time)
    session4.reflist = (session4.ref1,
                        session4.ref2,
                        session4.ref3,
                        session4.ref4)
    session4.umatrix = ((0.70711, 0.70711, 0.00),
                   (-0.70711, 0.70711, 0.00),
                   (0.00, 0.00, 1.00))
    session4.ref1calchkl = (0, 1, 2)  # Must match the guessed value!
    session4.ref2calchkl = (1, 0, 2)
    
    
    ############################ SESSION5 ############################
    # test crystal
    
    session5 = SessionScenario()
    session5.name = "Dalyite"
    session5.time = datetime.now()
    session5.lattice = ((7.51, 7.73, 7.00, 106.0, 113.5, 99.5))
    session5.system = 'Triclinic'
    session5.bmatrix = (((0.96021, 0.27759, 0.49527), (0, 0.84559, 0.25738), (0, 0, 0.89760)))
    session5.ref1 = _Reflection(0, 1, 2,
                               P(0.0000, 23.7405, 0.0000, 11.8703, 46.3100, 43.1304),
                               12.3984, 'ref1', session5.time)
    session5.ref2 = _Reflection(1, 0, 3,
                               P(0.0000, 34.4282, 0.000, 17.2141, 46.4799, 12.7852),
                               12.3984, 'ref2', session5.time)
    session5.ref3 = _Reflection(2, 2, 6,
                               P(0.0000, 82.8618, 0.000, 41.4309, 41.5154, 26.9317),
                               12.3984, 'ref3', session5.time)
    session5.ref4 = _Reflection(4, 1, 4,
                               P(0.0000, 71.2763, 0.000, 35.6382, 29.5042, 14.5490),
                               12.3984, 'ref4', session5.time)
    session5.ref5 = _Reflection(8, 3, 1,
                               P(0.0000, 97.8850, 0.000, 48.9425, 5.6693, 16.7929),
                               12.3984, 'ref5', session5.time)
    session5.ref6 = _Reflection(6, 4, 5,
                               P(0.0000, 129.6412, 0.000, 64.8206, 24.1442, 24.6058),
                               12.3984, 'ref6', session5.time)
    session5.ref7 = _Reflection(3, 5, 7,
                               P(0.0000, 135.9159, 0.000, 67.9579, 34.3696, 35.1816),
                               12.3984, 'ref7', session5.time)
    session5.reflist = (session5.ref1,
                        session5.ref2,
                        session5.ref3,
                        session5.ref4,
                        session5.ref5,
                        session5.ref6,
                        session5.ref7
                        )
    session5.umatrix = (( 0.99982,  0.00073,  0.01903),
                        ( 0.00073,  0.99710, -0.07612),
                        (-0.01903,  0.07612,  0.99692))
    session5.ref1calchkl = (0, 1, 2)  # Must match the guessed value!
    session5.ref2calchkl = (1, 0, 3)
    
    
    ############################ SESSION6 ############################
    # test crystal
    
    session6 = SessionScenario()
    session6.name = "Acanthite"
    session6.time = datetime.now()
    session6.lattice = ((4.229, 6.931, 7.862, 90, 99.61, 90))
    session6.system = 'Monoclinic'
    session6.bmatrix = ((1.50688, 0.00000, 0.13532),
                         (0.00000, 0.90653, 0.00000),
                         (0.00000, 0.00000, 0.79918))
    session6.ref1 = _Reflection(0, 1, 2,
                               P(0.0000, 21.1188, 0.0000, 10.5594, 59.6447, 61.8432),
                               10., 'ref1', session6.time)
    session6.ref2 = _Reflection(1, 0, 3,
                               P(0.0000, 35.2291, 0.000, 62.4207, 87.1516, -90.0452),
                               10., 'ref2', session6.time)
    session6.ref3 = _Reflection(1, 1, 6,
                               P(0.0000, 64.4264, 0.000, 63.9009, 97.7940, -88.8808),
                               10., 'ref3', session6.time)
    session6.ref4 = _Reflection(1, 2, 2,
                               P(0.0000, 34.4369, 0.000, 72.4159, 60.1129, -29.0329),
                               10., 'ref4', session6.time)
    session6.ref5 = _Reflection(2, 2, 1,
                               P(0.0000, 43.0718, 0.000, 21.5359, 8.3873, 29.0230),
                               10., 'ref5', session6.time)
    session6.reflist = (session6.ref1,
                        session6.ref2,
                        session6.ref3,
                        session6.ref4,
                        session6.ref5,
                        )
    session6.umatrix = (( 0.99411, 0.00079,  0.10835),
                        ( 0.00460, 0.99876, -0.04949),
                        (-0.10825, 0.04969,  0.99288))
    session6.ref1calchkl = (0, 1, 2)  # Must match the guessed value!
    session6.ref2calchkl = (1, 0, 3)
    ########################################################################
    return (session1, session2, session3, session4, session5, session6)
