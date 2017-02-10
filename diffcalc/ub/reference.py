from math import pi

try:
    from numpy import matrix, hstack
    from numpy.linalg import norm
except ImportError:
    from numjy import matrix, hstack
    from numjy.linalg import norm


from math import pi, sin, cos, tan, acos, atan2, asin, sqrt, atan

from diffcalc.util import DiffcalcException, bound, angle_between_vectors
from diffcalc.util import cross3, z_rotation, x_rotation, dot3





SMALL = 1e-7
TODEG = 180 / pi



class YouReference(object):
    
    def __init__(self, get_UB):
        self.get_UB = get_UB  # callable
        self._n_phi_configured = None
        self._n_hkl_configured = None
        self._set_n_phi_configured(matrix('0; 0; 1'))
    
    def _set_n_phi_configured(self, n_phi):
        self._n_phi_configured = n_phi
        self._n_hkl_configured = None
    
    def _get_n_phi_configured(self):
        return self._n_phi_configured
    
    n_phi_configured = property(_get_n_phi_configured, _set_n_phi_configured)
                    
    def _set_n_hkl_configured(self, n_hkl):
        self._n_phi_configured = None
        self._n_hkl_configured = n_hkl
        
    def _get_n_hkl_configured(self):
        return self._n_hkl_configured
    
    n_hkl_configured = property(_get_n_hkl_configured, _set_n_hkl_configured)
    
    @property
    def n_phi(self):
        n_phi = (self.get_UB() * self._n_hkl_configured if self._n_phi_configured is None 
                 else self._n_phi_configured)
        return n_phi / norm(n_phi)
        
    @property
    def n_hkl(self):
        n_hkl = (self.get_UB().I * self._n_phi_configured if self._n_hkl_configured is None
                  else self._n_hkl_configured) 
        return n_hkl / norm(n_hkl)
    
    def _pretty_vector(self, m):
        return ' '.join([('% 9.5f' % e).rjust(9) for e in m.T.tolist()[0]])
    
    def repr_lines(self, ub_calculated, WIDTH=9):
        SET_LABEL = ' <- set'
        lines = []
        if self._n_phi_configured is not None:
            nphi_label = SET_LABEL
            nhkl_label = ''
        elif self._n_hkl_configured is not None:
            nphi_label = ''
            nhkl_label = SET_LABEL
        else:
            raise AssertionError("Neither a manual n_phi nor n_hkl is configured")
        
        if ub_calculated:
            lines.append("   n_phi:".ljust(WIDTH) + self._pretty_vector(self.n_phi) + nphi_label)
            lines.append("   n_hkl:".ljust(WIDTH) + self._pretty_vector(self.n_hkl) + nhkl_label)
            rotation_axis = cross3(matrix('0; 0; 1'), self.n_phi)
            if abs(norm(rotation_axis)) < SMALL:
                lines.append("   miscut:".ljust(WIDTH) + "  None")
            else:
                rotation_axis = rotation_axis * (1 / norm(rotation_axis))
                cos_rotation_angle = dot3(matrix('0; 0; 1'), self.n_phi)
                rotation_angle = acos(cos_rotation_angle)
                lines.append("   miscut:")
                lines.append("      angle:".ljust(WIDTH) + "% 9.5f" % (rotation_angle * TODEG))
                lines.append("      axis:".ljust(WIDTH) + self._pretty_vector(rotation_axis))
 
        else:  # no ub calculated
            if self._n_phi_configured is not None:
                lines.append("   n_phi:".ljust(WIDTH) + self._pretty_vector(self._n_phi_configured) + SET_LABEL)
            elif self._n_hkl_configured is not None:
                lines.append("   n_hkl:".ljust(WIDTH) + self._pretty_vector(self._n_hkl_configured) + SET_LABEL)

        return lines
    
