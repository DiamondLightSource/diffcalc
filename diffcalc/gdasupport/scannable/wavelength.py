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

try:
    from gdascripts.pd.dummy_pds import DummyPD
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import DummyPD


class Wavelength(DummyPD):

    def __init__(self, name, energyScannable,
                 energyScannableMultiplierToGetKeV=1):
        self.energyScannable = energyScannable
        self.energyScannableMultiplierToGetKeV = \
            energyScannableMultiplierToGetKeV

        DummyPD.__init__(self, name)

    def asynchronousMoveTo(self, pos):
        self.energyScannable.asynchronousMoveTo(
            (12.39842 / pos) / self.energyScannableMultiplierToGetKeV)

    def getPosition(self):
        energy = self.energyScannable.getPosition()
        if energy == 0:
            raise Exception(
                      "The energy is 0, so no wavelength could be calculated.run_All()")
        return 12.39842 / (energy * self.energyScannableMultiplierToGetKeV)

    def isBusy(self):
        return self.energyScannable.isBusy()

    def waitWhileBusy(self):
        return self.energyScannable.waitWhileBusy()
