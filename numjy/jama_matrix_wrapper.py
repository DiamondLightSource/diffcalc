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

import Jama


class matrix(object):

    def __init__(self, a):
        if isinstance(a, Jama.Matrix):
            self.m = a
        elif isinstance(a, basestring):
            l = []
            for row in a.strip().split(';'):
                l.append([float(element)
                          for element in row.replace(',', ' ').split()])
            self.m = Jama.Matrix(l)
        elif isinstance(a, matrix):
            self.m = Jama.Matrix(a.tolist())
        elif isinstance(a, (list, tuple)):
            if isinstance(a[0], (list, tuple)):
                # a is a list of lists (not rigorous test!)
                self.m = Jama.Matrix(a)
            else:
                # a is a row vector
                self.m = Jama.Matrix([a])
        else:
            # give it a go
            self.m = Jama.Matrix(a)

    def __eq__(self, other):
        nrow, ncol = self.shape
        b = matrix(Jama.Matrix(nrow, ncol))
        for i in range(nrow):
            for j in range(ncol):
                b[i, j] = self[i, j] == other[i, j]
        return b

    @property
    def shape(self):
        return self.m.getRowDimension(), self.m.getColumnDimension()

    def __len__(self):
        return self.m.getRowDimension()

    def all(self):  # @ReservedAssignment
        for row in self.m.array:
            if not all(row):
                return False
        return True

    def tolist(self):
        l = []
        nrow, ncol = self.shape
        for i in range(nrow):
            row = []
            for j in range(ncol):
                row.append(self[i, j])
            l.append(row)
        return l

    def sum(self):  # @ReservedAssignment
        return sum(sum(row) for row in self.m.array)

    @property
    def I(self):
        return matrix(self.m.inverse())

    @property
    def T(self):
        return matrix(self.m.transpose())

    def _scaler(self, scaler):
        return Jama.Matrix(self.shape[0], self.shape[1], scaler)

    def __add__(self, other):
        v = other.m if isinstance(other, matrix) else self._scaler(other)
        return matrix(self.m.plus(v))

    def __sub__(self, other):
        v = other.m if isinstance(other, matrix) else self._scaler(other)
        return matrix(self.m.minus(v))

    def __mul__(self, other):
        return matrix(self.m.times(other.m if isinstance(other, matrix) else
                                   other))

    def __div__(self, other):
        # dividend = other.I if isinstance(other, matrix) else 1. /float(other)
        return self.__mul__(1. / float(other))

    def __getitem__(self, key):
        i, j = key
        return self.m.get(i, j)

    def __setitem__(self, key, value):
        i, j = key
        self.m.set(i, j, value)

    def __str__(self):
        insides = ['  '.join([str(el) for el in row]) for row in self.tolist()]
        return '[[' + ']\n ['.join(insides) + ']]'

    def __repr__(self):
        return 'matrix(' + '\n       '.join(self.__str__().split('\n')) + ')'
