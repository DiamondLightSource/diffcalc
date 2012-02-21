import Jama

from numjy import linalg

from numjy.jama_matrix_wrapper import matrix


def hstack(list_of_column_matrices):
    ncol = len(list_of_column_matrices)
    nrow = list_of_column_matrices[0].shape[0]
    m = Jama.Matrix(nrow, ncol)
    for c, column_matrix in enumerate(list_of_column_matrices):
        m.setMatrix(0, nrow - 1, c, c, column_matrix.m)
    return matrix(m)
