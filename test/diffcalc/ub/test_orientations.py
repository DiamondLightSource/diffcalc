###
# Copyright 2008-2019 Diamond Light Source Ltd.
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
from diffcalc.ub.orientations import OrientationList
from diffcalc.hkl.you.geometry  import YouPosition as Pos, SixCircle
from diffcalc.util import DiffcalcException
import pytest


class TestOrientationList(object):

    def setup_method(self):
        self._geometry = SixCircle()
        self.orientlist = OrientationList(self._geometry,
                                      ['a', 'd', 'g', 'o', 'c', 'p'])
        self.time = datetime.now()
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        self.orientlist.add_orientation(1, 2, 3, 0.1, 0.2, 0.3, pos, "orient1", self.time)
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        self.orientlist.add_orientation(1.1, 2.2, 3.3, 0.11, 0.12, 0.13, pos, "orient2", self.time)

    def test_add_orientation(self):
        assert len(self.orientlist) == 2
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        self.orientlist.add_orientation(10, 20, 30, 0.1, 0.2, 0.3, pos, "orient1", self.time)

    def testGetOrientation(self):
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        answered = self.orientlist.getOrientation(1)
        desired = ([1, 2, 3], [0.1, 0.2, 0.3], pos, "orient1", self.time)
        assert answered == desired
        answered = self.orientlist.getOrientation("orient1")
        assert answered == desired

    def testRemoveOrientation(self):
        self.orientlist.removeOrientation(1)
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        answered = self.orientlist.getOrientation(1)
        desired = ([1.1, 2.2, 3.3], [0.11, 0.12, 0.13], pos, "orient2", self.time)
        assert answered == desired
        self.orientlist.removeOrientation("orient2")
        assert self.orientlist._orientlist == []

    def testedit_orientation(self):
        ps = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        self.orientlist.edit_orientation(1, 10, 20, 30, 1, 2, 3, ps, "new1", self.time)
        assert (self.orientlist.getOrientation(1)
                == ([10, 20, 30], [1, 2, 3], ps, "new1", self.time))
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        assert (self.orientlist.getOrientation(2)
                == ([1.1, 2.2, 3.3], [0.11, 0.12, 0.13], pos, "orient2", self.time))
        self.orientlist.edit_orientation("orient2", 1.1, 2.2, 3.3, 1.11, 1.12, 1.13, pos, "new2", self.time)
        assert (self.orientlist.getOrientation("new2")
                == ([1.1, 2.2, 3.3], [1.11, 1.12, 1.13], pos, "new2", self.time))
        self.orientlist.edit_orientation("new2", 1.1, 2.2, 3.3, 1.11, 1.12, 1.13, pos, "new1", self.time)
        assert (self.orientlist.getOrientation("new1")
                == ([10, 20, 30], [1, 2, 3], ps, "new1", self.time))

    def testSwapOrientation(self):
        self.orientlist.swap_orientations(1, 2)
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        assert (self.orientlist.getOrientation(1)
                == ([1.1, 2.2, 3.3], [0.11, 0.12, 0.13], pos, "orient2", self.time))
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        assert (self.orientlist.getOrientation(2)
                 == ([1, 2, 3], [0.1, 0.2, 0.3], pos, "orient1", self.time))
        self.orientlist.swap_orientations("orient1", "orient2")
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        assert (self.orientlist.getOrientation(2)
                == ([1.1, 2.2, 3.3], [0.11, 0.12, 0.13], pos, "orient2", self.time))
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        assert (self.orientlist.getOrientation(1)
                 == ([1, 2, 3], [0.1, 0.2, 0.3], pos, "orient1", self.time))
