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


class UBCalculationPersister(object):
    """Attempts to the use the gda's database to store ub calculation state
    """
    def __init__(self):
        try:
            from gda.util.persistence import LocalJythonShelfManager
            from gda.util.persistence.LocalDatabase import \
                LocalDatabaseException
            self.shelf = LocalJythonShelfManager.getLocalObjectShelf(
                'diffcalc.ub')
        except ImportError, e:
            print ("!!! UBCalculationPersister could not import the gda database "
                   "code: " + repr(e))
            self.shelf = None
        except LocalDatabaseException, e:
            print ("UBCalculationPersister could not connect to the gda "
                   "database: " + repr(e))
            self.shelf = None

    def save(self, state, key):
        if self.shelf is not None:
            self.shelf[key] = state
        else:
            print "<<<no database available to save UB calculation>>>"

    def load(self, name):
        if self.shelf is not None:
            return self.shelf[name]
        raise IOError("Could not load UB calculation: no database available")

    def list(self):  # @ReservedAssignment
        if self.shelf is not None:
            names = list(self.shelf.keys())
            names.sort()
            return names
        else:
            return []

    def remove(self, name):
        if self.shelf is not None:
            del self.shelf[name]
        raise IOError("Could not remove UB calculation: no database available")


class UbCalculationNonPersister(UBCalculationPersister):
    """
    A version of UBCalculationPersister that simply stores to a local dict
    rather than a database. Useful for testing.
    """
    def __init__(self):
        self.shelf = dict()
