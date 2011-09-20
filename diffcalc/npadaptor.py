try:
    import numpy
    #import numpy.matrix
except ImportError:
    raise ImportError("Could not find numpy package. If a Jama.jar was not found, this package tries for numpy instead")
except:
    raise Exception("""Problem importing numpy. Package was found, but could not
be started. Most likely you are using Jython, and do not have the Jama.jar on your
path, but do have the Python only numpy on your path.""")

numpy.dtype


class Matrix(object):
    """A minimal subset of the jama.Matrix class supporting only the behaviours used by diffcalc"""

    def identity(m,n):
        if m!=n:
            raise ValueError
        return Matrix(numpy.identity(m))
    identity = staticmethod(identity)
    
    
    def __init__(self, *args):
        """Creates a matrix where m can be a list/tuple or list/tuple of list/tuples"""
        # if two args, they represent the size of the desire 0 matrix
        if len(args)==2:
            if type(args[0])!=int or type(args[1])!=int:
                raise TypeError()
            self.m =  numpy.mat(numpy.zeros( (args[0],args[1]) ), 'float')
        elif len(args)==1:
            m = args[0]
            if isinstance(m, numpy.matrix): #core.defmatrix.matrix:
                self.m=m
            else:
                self.m = numpy.mat(m, 'float')
        else:
            raise TypeError()
    
    def __str__(self):
        return self.m.__str__()
    
    def getArray(self):
        """Returns a list of lists"""
        r = self.m.tolist()
        if type(r[0]) is not list:
            r= [r]
        return r
    
    @property
    def array(self):
        return self.getArray()
    
    
    def get(self, *args):
        return self.m[args[0], args[1]]
    
    def getRowDimension(self):
        return numpy.size(self.m,0)

    def getColumnDimension(self):
        return numpy.size(self.m,1)
        
    def setMatrix(self, rowList, colList, b):
        self.m[numpy.ix_(rowList,colList)]=b.m # Doesn't work: ix_ seems to return a new matrix, not part of the original

    def minus(self, b):
        return Matrix(self.m - b.m)
    
    def plus(self, b):
        return Matrix(self.m + b.m)
    
    def normF(self):
        return numpy.linalg.norm(self.m)
            
    def norm1(self):
        """Returns maximum column sum."""
        return self.m.sum(axis=0).max()
        
    def times(self, b):
###        print type(b)
        if type(b) is Matrix:
            return Matrix(self.m * b.m)
        else: # likely a scaler
            return Matrix( numpy.mat(numpy.array(self.m)*b) )
    
    def transpose(self):
        return Matrix(self.m.transpose())
    
    def inverse(self):
        return Matrix(numpy.linalg.inv(self.m))