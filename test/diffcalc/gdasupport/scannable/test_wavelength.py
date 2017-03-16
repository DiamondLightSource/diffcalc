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

from diffcalc.gdasupport.scannable.wavelength import Wavelength
try:
    from gdascripts.pd.dummy_pds import DummyPD
except ImportError:
    from diffcalc.gdasupport.minigda.scannable import DummyPD


class TestWavelength(object):

    def setup_method(self):
        self.en = DummyPD('en')
        self.wl = Wavelength('wl', self.en)

    def testIt(self):
        self.en.asynchronousMoveTo(12.39842)
        assert self.wl.getPosition() == 1

        self.wl.asynchronousMoveTo(1.)
        assert self.wl.getPosition() == 1.
        assert self.en.getPosition() == 12.39842
