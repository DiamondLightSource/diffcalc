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

import os
import shutil
import unittest

try:
    from gda.configuration.properties import LocalProperties
except ImportError:
    print "Could not import LocalProperties to configure database locations."

from diffcalc.ub.persistence import UbCalculationNonPersister


def prepareEmptyGdaVarFolder():
    vartest_dir = os.path.join(os.getcwd(), 'var_test')
    LocalProperties.set('gda.var', vartest_dir)
    if os.path.exists(vartest_dir):
        print "Removing existing gda.var: ", vartest_dir
        shutil.rmtree(vartest_dir)
    print "Creating gda.var: ", vartest_dir
    os.mkdir(vartest_dir)


class TestUBCalculationNonPersister(unittest.TestCase):

    def setUp(self):
        self.p = UbCalculationNonPersister()

    def testSaveAndLoad(self):
        self.p.save('string1', 'ub1')
