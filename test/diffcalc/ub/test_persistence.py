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
import tempfile
import time
from nose.tools import eq_  # @UnresolvedImport

try:
    from gda.configuration.properties import LocalProperties
except ImportError:
    print "Could not import LocalProperties to configure database locations."

from diffcalc.ub.persistence import UbCalculationNonPersister, UBCalculationJSONPersister


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
        self.persister = UbCalculationNonPersister()

    def testSaveAndLoad(self):
        self.persister.save('string1', 'ub1')


class TestUBCalculationJSONPersister(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        print self.tmpdir
        self.persister = UBCalculationJSONPersister(self.tmpdir)
        f = open(os.path.join(self.tmpdir, 'unexpected_file'), 'w')
        f.close()
        
    def test_list_with_empty_dir(self):
        eq_(self.persister.list(), [])
        
    def test_save_load(self):
        d = {'a' : 1, 'b': 2}
        self.persister.save(d, 'first')
        eq_(self.persister.load('first'), d)

    def test_save_overwites(self):
        d1 = {'a' : 1, 'b': 2}
        self.persister.save(d1, 'first')
        eq_(self.persister.load('first'), d1)

        d2 = {'a' : 3, 'b': 4, 'c' : 5}
        self.persister.save(d2, 'first')
        eq_(self.persister.load('first'), d2)

    def test_list(self):
        d = {'a' : 1, 'b': 2}
        self.persister.save(d, 'first')
        eq_(self.persister.list(), ['first'])
        
    def test_multiple_list(self):
        d = {'a' : 1, 'b': 2}
        self.persister.save(d, 'first')
        time.sleep(.5)
        self.persister.save(d, 'second')
        time.sleep(.5)
        self.persister.save(d, 'alphabetically_first')
        eq_(self.persister.list(), ['alphabetically_first', 'second', 'first'])
        
    def test_remove_list(self):
        d = {'a' : 1, 'b': 2}
        self.persister.save(d, 'first')
        self.persister.remove('first')
        eq_(self.persister.list(), [])
        
    

