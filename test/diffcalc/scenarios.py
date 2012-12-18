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

from diffcalc.ub.reflections import _Reflection
from diffcalc.hkl.vlieg.geometry  import VliegPosition as P


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


########################################################################
def sessions():
    return (session1, session2, session3)
