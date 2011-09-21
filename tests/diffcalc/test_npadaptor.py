#from diffcalc.tools import assert_2darray_almost_equal
import unittest
try:
    from diffcalc.npadaptor import Matrix
    SKIP = False
except ImportError:
#    class TestMatrix(unittest.TestCase):
    print "Skipping TestJamaWrapperForNumpyTests as numpy could not be imported"
    SKIP = True



class TestMatrix(unittest.TestCase):
    
    def test__init__(self):
        if SKIP: return
        m = Matrix(2, 3)
        self.assertEqual(m.getArray(), [[0., 0., 0.], [0., 0., 0.]])
    
    def testGetArray(self):
        if SKIP: return
        m = Matrix([[1, 2, 3]])
        self.assertEqual(m.getArray(), [[1, 2, 3]])
        
        m = Matrix(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(m.getArray(), [[1, 2, 3], [4, 5, 6]])
        
    def testArrayAttributeAccess(self):
        if SKIP: return
        m = Matrix([[1, 2, 3]])
        self.assertEqual(m.array, [[1, 2, 3]])
        
        m = Matrix(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(m.array, [[1, 2, 3], [4, 5, 6]])
    
    def testSetMatrix(self):
        if SKIP: return
        m = Matrix([[1., 2., 3.], [4., 5., 6.]])
        m.setMatrix([0, 1], [1], Matrix([[2.2], [5.5]]))
        self.assertEqual(m.getArray(), [[1, 2.2, 3], [4, 5.5, 6]])
    
    def testMinus(self):
        if SKIP: return
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        self.assertEqual((m.minus(m)).getArray(), [[0, 0, 0], [0, 0, 0]])
        
    def testPlus(self):
        if SKIP: return
        m = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertEquals(m.plus(m).getArray(), [[ 2, 4, 6], [ 8, 10, 12], [14, 16, 18]]) 

    def testNormF(self):
        if SKIP: return
        m = Matrix([[1, 2, 3]])
        self.assertTrue(abs(m.normF() - 3.74165738677) < 1e-10)

    def testNorm1(self):
        if SKIP: return
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        self.assertEqual(m.norm1(), 9)
        
    def testTimesWithMatrices(self):
        if SKIP: return
        m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        m2 = m1.plus(m1)
        m1m2 = [[60.0, 72.0, 84.0] , [132.0, 162.0, 192.0] , [204.0, 252.0, 300.0]]
        self.assertEqual(m1.times(m2).getArray(), m1m2)
    
    def testTimesWithScaler(self):
        if SKIP: return
        m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertEqual(m1.times(2).getArray(), [[2, 4, 6], [8, 10, 12], [14, 16, 18]])
        
    def testTranspose(self):
        if SKIP: return
        m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertEqual(m1.transpose().getArray(), [[1, 4, 7], [2, 5, 8], [3, 6, 9]]) 
        
#    TODO: Test inverse
#    def testInverse(self):
#        if SKIP: return
#        m1 = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
#        m1inv = Matrix([[  3.15221191e+15, -6.30442381e+15, 3.15221191e+15],
#                    [ -6.30442381e+15, 1.26088476e+16, -6.30442381e+15],
#                    [  3.15221191e+15, -6.30442381e+15, 3.15221191e+15]])
#        assert_2darray_almost_equal(m1.inverse().getArray(), m1inv.getArray(), 1)

    def testIdentity(self):
        if SKIP: return
        m1 = Matrix.identity(3, 3)
        self.assertEqual(m1.getArray(), [[1, 0, 0], [0, 1, 0], [0, 0, 1]]) 

