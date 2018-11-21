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

from diffcalc.hkl.common import getNameFromScannableOrString
from diffcalc.util import command
from diffcalc import settings


from diffcalc.ub import ub
from diffcalc.hkl.vlieg.calc import VliegHklCalculator


__all__ = ['hklmode', 'setpar', 'trackalpha', 'trackgamma', 'trackphi',
           'parameter_manager', 'hklcalc']


hklcalc = VliegHklCalculator(ub.ubcalc)

parameter_manager = hklcalc.parameter_manager

def __str__(self):
    return hklcalc.__str__()

@command
def hklmode(num=None):
    """hklmode {num} -- changes mode or shows current and available modes and all settings""" #@IgnorePep8

    if num is None:
        print hklcalc.__str__()
    else:
        hklcalc.mode_selector.setModeByIndex(int(num))
        pm = hklcalc.parameter_manager
        print (hklcalc.mode_selector.reportCurrentMode() + "\n" +
               pm.reportParametersUsedInCurrentMode())

def _setParameter(name, value):
    hklcalc.parameter_manager.set_constraint(name, value)

def _getParameter(name):
    return hklcalc.parameter_manager.get_constraint(name)

@command
def setpar(scannable_or_string=None, val=None):
    """setpar {parameter_scannable {{val}} -- sets or shows a parameter'
    setpar {parameter_name {val}} -- sets or shows a parameter'
    """

    if scannable_or_string is None:
        #show all
        parameterDict = hklcalc.parameter_manager.getParameterDict()
        names = parameterDict.keys()
        names.sort()
        for name in names:
            print _representParameter(name)
    else:
        name = getNameFromScannableOrString(scannable_or_string)
        if val is None:
            _representParameter(name)
        else:
            oldval = _getParameter(name)
            _setParameter(name, float(val))
            print _representParameter(name, oldval, float(val))

def _representParameter(name, oldval=None, newval=None):
    flags = ''
    if hklcalc.parameter_manager.isParameterTracked(name):
        flags += '(tracking hardware) '
    if settings.geometry.parameter_fixed(name):  # @UndefinedVariable
        flags += '(fixed by geometry) '
    pm = hklcalc.parameter_manager
    if not pm.isParameterUsedInSelectedMode(name):
        flags += '(not relevant in this mode) '
    if oldval is None:
        val = _getParameter(name)
        if val is None:
            val = "---"
        else:
            val = str(val)
        return "%s: %s %s" % (name, val, flags)
    else:
        return "%s: %s --> %f %s" % (name, oldval, newval, flags)

def _checkInputAndSetOrShowParameterTracking(name, b=None):
    """
    for track-parameter commands: If no args displays parameter settings,
    otherwise sets the tracking switch for the given parameter and displays
    settings.
    """
    # set if arg given
    if b is not None:
        hklcalc.parameter_manager.setTrackParameter(name, b)
    # Display:
    lastValue = _getParameter(name)
    if lastValue is None:
        lastValue = "---"
    else:
        lastValue = str(lastValue)
    flags = ''
    if hklcalc.parameter_manager.isParameterTracked(name):
        flags += '(tracking hardware)'
    print "%s: %s %s" % (name, lastValue, flags)

@command
def trackalpha(b=None):
    """trackalpha {boolean} -- determines wether alpha parameter will track alpha axis""" #@IgnorePep8
    _checkInputAndSetOrShowParameterTracking('alpha', b)

@command
def trackgamma(b=None):
    """trackgamma {boolean} -- determines wether gamma parameter will track alpha axis""" #@IgnorePep8
    _checkInputAndSetOrShowParameterTracking('gamma', b)

@command
def trackphi(b=None):
    """trackphi {boolean} -- determines wether phi parameter will track phi axis""" #@IgnorePep8
    _checkInputAndSetOrShowParameterTracking('phi', b)
  
  
commands_for_help = ['Mode',
                     hklmode,
                     setpar,
                     trackalpha,
                     trackgamma,
                     trackphi]
