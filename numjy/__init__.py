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
    import Jama
    from numjy import linalg
    from numjy.jama_matrix_wrapper import matrix
    JAMA = True
except ImportError:
    JAMA = False


def hstack(list_of_column_matrices):
    if not Jama:
        raise Exception('Jama not available, use numpy directly')
    ncol = len(list_of_column_matrices)
    nrow = list_of_column_matrices[0].shape[0]
    m = Jama.Matrix(nrow, ncol)
    for c, column_matrix in enumerate(list_of_column_matrices):
        m.setMatrix(0, nrow - 1, c, c, column_matrix.m)
    return matrix(m)
