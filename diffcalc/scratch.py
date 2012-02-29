
from functools import wraps

D = []


def dec(f):
    D.append(f)

    @wraps(f)
    def wrapper(*args, **kwds):
        print('Calling decorated function')
        return f(*args, **kwds)

    return wrapper


@dec
def p(a, b):
    """p doc"""
    print a, b


class C(object):

    @dec
    def p(self, a, b):
        """C.p doc"""
        print a, b

print "*"
p(1, 2)

print D
print D[0].__doc__

print "*"
c = C()
c.p(1, 2)

print D

print "******************"

DOC = 'abc'


class _Metaclass(type):

    def _get_doc(self):
        return DOC

    __doc__ = property(_get_doc)  # @ReservedAssignment


# Build a callable class to wrap the tool.#
class DM(object):
    pass


class CM(DM):
    
    __metaclass__ = _Metaclass
    
    def _get_doc(self):
        return DOC * 2
    
    __doc__ = property(_get_doc)
   


cm = CM()
print cm.__doc__

DOC = 'def'
print cm.__doc__
