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
from diffcalc.ub.reflections import ReflectionList
from diffcalc.hkl.you.geometry  import YouPosition as Pos, SixCircle
from diffcalc.util import DiffcalcException
import pytest


class TestReflectionList(object):

    def setup_method(self):
        self._geometry = SixCircle()
        self.reflist = ReflectionList(self._geometry,
                                      ['a', 'd', 'g', 'o', 'c', 'p'])
        self.time = datetime.now()
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        self.reflist.add_reflection(1, 2, 3, pos, 1000, "ref1", self.time)
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        self.reflist.add_reflection(1.1, 2.2, 3.3, pos, 1100, "ref2", self.time)

    def test_add_reflection(self):
        assert len(self.reflist) == 2
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        self.reflist.add_reflection(11.1, 12.2, 13.3, pos, 1100, "ref2", self.time)

    def testGetReflection(self):
        answered = self.reflist.getReflection(1)
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        desired = ([1, 2, 3], pos, 1000, "ref1", self.time)
        assert answered == desired
        answered = self.reflist.getReflection('ref1')
        assert answered == desired

    def testRemoveReflection(self):
        self.reflist.removeReflection(1)
        answered = self.reflist.getReflection(1)
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        desired = ([1.1, 2.2, 3.3], pos, 1100, "ref2", self.time)
        assert answered == desired
        self.reflist.removeReflection("ref2")
        assert self.reflist._reflist == []

    def testedit_reflection(self):
        ps = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        self.reflist.edit_reflection(1, 10, 20, 30, ps, 1000, "new1", self.time)
        assert (self.reflist.getReflection(1)
                == ([10, 20, 30], ps, 1000, "new1", self.time))
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        assert (self.reflist.getReflection(2)
                == ([1.1, 2.2, 3.3], pos, 1100, "ref2", self.time))
        self.reflist.edit_reflection("ref2", 1.1, 2.2, 3.3, pos, 1100, "new2", self.time)
        assert (self.reflist.getReflection("new2")
                == ([1.1, 2.2, 3.3], pos, 1100, "new2", self.time))
        self.reflist.edit_reflection("new2", 10, 20, 30, pos, 1100, "new1", self.time)
        assert (self.reflist.getReflection("new1")
                == ([10, 20, 30], ps, 1000, "new1", self.time))

    def testSwapReflection(self):
        self.reflist.swap_reflections(1, 2)
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        assert (self.reflist.getReflection(1)
                == ([1.1, 2.2, 3.3], pos, 1100, "ref2", self.time))
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        assert (self.reflist.getReflection(2)
                 == ([1, 2, 3], pos, 1000, "ref1", self.time))
        self.reflist.swap_reflections("ref1", "ref2")
        pos = Pos(0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 'DEG')
        assert (self.reflist.getReflection(2)
                == ([1.1, 2.2, 3.3], pos, 1100, "ref2", self.time))
        pos = Pos(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 'DEG')
        assert (self.reflist.getReflection(1)
                 == ([1, 2, 3], pos, 1000, "ref1", self.time))

    def createRefStateDicts(self):
        ref_0 = {
            'h': 1,
            'k': 2,
            'l': 3,
            'position': (0.1, 0.2, 0.3, 0.4, 0.5, 0.6),
            'energy': 1000,
            'tag': "ref1",
            'time': repr(self.time)
        }
        ref_1 = {
            'h': 1.1,
            'k': 2.2,
            'l': 3.3,
            'position': (0.11, 0.22, 0.33, 0.44, 0.55, 0.66),
            'energy': 1100,
            'tag': "ref2",
            'time': repr(self.time)
        }
        return ref_0, ref_1