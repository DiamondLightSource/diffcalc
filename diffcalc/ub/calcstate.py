from diffcalc.ub.crystal import CrystalUnderTest
from diffcalc.ub.reflections import ReflectionList, _Reflection
from math import pi
import datetime  # @UnusedImport For crazy time eval code!
from diffcalc.ub.reference import YouReference
from diffcalc.ub.orientations import _Orientation, OrientationList
from diffcalc.log import logging
from diffcalc import settings
from diffcalc.hkl.you.geometry import YouPosition
try:
    from collection import OrderedDict
except ImportError:
    from simplejson import OrderedDict

try:
    import json
except ImportError:
    import simplejson as json

try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

logger = logging.getLogger("diffcalc.ub.calcstate")

TODEG = 180 / pi


class UBCalcState():
    
    def __init__(self, name=None, crystal=None, reflist=None, orientlist=None, tau=0, sigma=0,
                 manual_U=None, manual_UB=None, or0=None, or1=None, reference=None, surface=None):

        assert reflist is not None
        self.name = name
        self.crystal = crystal
        self.reflist = reflist
        self.orientlist = orientlist
        self.tau = tau  # degrees
        self.sigma = sigma  # degrees
        self.manual_U = manual_U
        self.manual_UB = manual_UB
        self.or0 = or0
        self.or1 = or1
        self.reference = reference
        self.surface = surface
        
    @property
    def is_okay_to_autocalculate_ub(self):
        nothing_set = ((self.manual_U is None) and 
                       (self.manual_UB is None) and 
                       (self.or0 is None) and 
                       (self.or1 is None))
        or0_and_or1_used =  (self.or0 is not None) and (self.or1 is not None)
        return nothing_set or or0_and_or1_used
    

    def configure_calc_type(self,
                            manual_U=None,
                            manual_UB=None,
                            or0=None,
                            or1=None):
        self.manual_U = manual_U
        self.manual_UB = manual_UB
        self.or0 = or0
        self.or1 = or1


class UBCalcStateEncoder(json.JSONEncoder):
    
    def default(self, obj):
        
        if isinstance(obj, UBCalcState):
            d = OrderedDict()
            d['name'] = obj.name
            d['crystal'] = obj.crystal
            d['reflist'] = obj.reflist
            d['orientlist'] = obj.orientlist
            d['tau'] = obj.tau
            d['sigma'] = obj.sigma
            d['reference'] = obj.reference
            d['surface'] = obj.surface
            d['u'] = obj.manual_U
            d['ub'] = obj.manual_UB
            d['or0'] = obj.or0
            d['or1'] = obj.or1
            
            return d
        
        if isinstance(obj, CrystalUnderTest):
            return repr([obj._name, obj._system, obj._a1, obj._a2, obj._a3, obj._alpha1 * TODEG,
                         obj._alpha2 * TODEG, obj._alpha3 * TODEG])
            
        if isinstance(obj, matrix):
            l = [', '.join((repr(e) for e in row)) for row in obj.tolist()]
            return l
        
        if isinstance(obj, ReflectionList):
            d = OrderedDict()
            for n, ref in enumerate(obj._reflist):
                d[str(n+1)] = ref
            return d

        if isinstance(obj, _Reflection):
            d = OrderedDict()
            d['tag'] = obj.tag
            d['hkl'] = repr([obj.h, obj.k, obj.l])
            d['pos'] = repr(list(obj.pos.totuple()))
            d['energy'] = obj.energy
            dt = eval(obj.time)  # e.g. --> datetime.datetime(2013, 8, 5, 15, 47, 7, 962432)
            d['time'] = None if dt is None else dt.isoformat()
            return d
        
        if isinstance(obj, OrientationList):
            d = OrderedDict()
            for n, orient in enumerate(obj._orientlist):
                d[str(n+1)] = orient
            return d

        if isinstance(obj, _Orientation):
            d = OrderedDict()
            d['tag'] = obj.tag
            d['hkl'] = repr([obj.h, obj.k, obj.l])
            d['xyz'] = repr([obj.x, obj.y, obj.z])
            d['pos'] = repr(list(obj.pos.totuple()))
            dt = eval(obj.time)  # e.g. --> datetime.datetime(2013, 8, 5, 15, 47, 7, 962432)
            d['time'] = None if dt is None else dt.isoformat()
            return d
        
        if isinstance(obj, YouReference):
            d = OrderedDict()
            if obj.n_hkl_configured is not None:
                d['n_hkl_configured'] = repr(obj.n_hkl_configured.T.tolist()[0])
            else:
                d['n_hkl_configured'] = None
            if obj.n_phi_configured is not None:
                d['n_phi_configured'] = repr(obj.n_phi_configured.T.tolist()[0])
            else:
                d['n_phi_configured'] = None
            return d
        
        
        return json.JSONEncoder.default(self, obj)

    @staticmethod
    def decode_ubcalcstate(state, geometry, diffractometer_axes_names, multiplier):

        # Backwards compatibility code
        orientlist_=OrientationList(geometry, diffractometer_axes_names, [])
        try:
            orientlist_=decode_orientlist(state['orientlist'], geometry, diffractometer_axes_names)
        except KeyError:
            pass
        try:
            surface_=decode_reference(state['surface'], settings.surface_vector, False)
        except KeyError:
            surface_ = YouReference(None)
            surface_._set_n_phi_configured(settings.surface_vector)
        return UBCalcState(
            name=state['name'],
            crystal=state['crystal'] and CrystalUnderTest(*eval(state['crystal'])),
            reflist=decode_reflist(state['reflist'], geometry, diffractometer_axes_names, multiplier),
            orientlist=orientlist_,
            tau=state['tau'],
            sigma=state['sigma'],
            manual_U=state['u'] and decode_matrix(state['u']),
            manual_UB=state['ub'] and decode_matrix(state['ub']),
            or0=state['or0'],
            or1=state['or1'],
            reference=decode_reference(state.get('reference', None), settings.reference_vector, True),
            surface=surface_
        )


def decode_matrix(rows):
    return matrix([[eval(e) for e in row.split(', ')] for row in rows])


def decode_reflist(reflist_dict, geometry, diffractometer_axes_names, multiplier):
    reflections = []
    try:
        sorted_ref_keys = sorted(reflist_dict.keys(), key=int)
    except ValueError:
        logger.warning("Warning: Invalid index found in the stored list of reflections. "
                       "Please check the reflection list order.")
        sorted_ref_keys = sorted(reflist_dict.keys())
    for key in sorted_ref_keys:
        reflections.append(decode_reflection(reflist_dict[key], geometry))
        
    return ReflectionList(geometry, diffractometer_axes_names, reflections, multiplier)


def decode_orientlist(orientlist_dict, geometry, diffractometer_axes_names):
    orientations = []
    try:
        sorted_orient_keys = sorted(orientlist_dict.keys(), key=int)
    except ValueError:
        logger.exception("Warning: Invalid index found in the stored list of orientations. "
                         "Please check the orientation list order.")
        sorted_orient_keys = sorted(orientlist_dict.keys())
    for key in sorted_orient_keys:
        orientations.append(decode_orientation(orientlist_dict[key], geometry, diffractometer_axes_names))
        
    return OrientationList(geometry, diffractometer_axes_names, orientations)


def decode_reflection(ref_dict, geometry):
    h, k, l = eval(ref_dict['hkl'])
    time = ref_dict['time'] and gt(ref_dict['time'])
    pos_tuple = eval(ref_dict['pos'])
    try:
        position = geometry.create_position(*pos_tuple)
    except AttributeError:
        position = YouPosition(*pos_tuple)
    return _Reflection(h, k, l, position, ref_dict['energy'], str(ref_dict['tag']), repr(time))


def decode_reference(ref_dict, ref_vector, flg):
    reference = YouReference(None)  # TODO: We can't set get_ub method yet (tangles!)
    if ref_dict:   
        nhkl = ref_dict.get('n_hkl_configured', None)
        nphi = ref_dict.get('n_phi_configured', None)
        if nhkl:
            reference._set_n_hkl_configured(matrix([eval(nhkl)]).T)
        elif nphi:
            reference._set_n_phi_configured(matrix([eval(nphi)]).T)
        elif flg:
            reference._set_n_hkl_configured(ref_vector)
        else:
            reference._set_n_phi_configured(ref_vector)
    return reference


def decode_orientation(orient_dict, geometry, diffractometer_axes_names):
    h, k, l = eval(orient_dict['hkl'])
    x, y, z = eval(orient_dict['xyz'])
    time = orient_dict['time'] and gt(orient_dict['time'])
    try:
        pos_tuple = eval(orient_dict['pos'])
        position = geometry.create_position(*pos_tuple)
    except KeyError:
        pos_tuple = (0.,) * len(diffractometer_axes_names)
        position = geometry.physical_angles_to_internal_position(pos_tuple)
    return _Orientation(h, k, l, x, y, z, position, str(orient_dict['tag']), repr(time))


# From: http://stackoverflow.com/questions/127803/how-to-parse-iso-formatted-date-in-python
def gt(dt_str):
    dt, _, us= dt_str.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us= int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)