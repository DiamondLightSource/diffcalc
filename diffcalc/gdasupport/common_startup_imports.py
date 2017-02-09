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


# NOTE: This file must be run, not imported, for the ipython magic to work!

from __future__ import absolute_import

import os, sys


try:
    #  required for "python -i -m example/sixcircle" to work (although
    #  it didn't used to be: depends on where its started. Not good).
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except NameError:  # For use in execfile from ipython notebook
    # GDA run command does not honour the __file__ convention, but diffcalc
    # is put on the path by other means.
    pass

try:
    from gda.device.scannable.scannablegroup import ScannableGroup
    GDA = True
    from gdascripts.scannable.dummy import SingleInputDummy as Dummy  
except ImportError:
    GDA = False
    # Not running in gda environment so fall back to minigda emulation
    from diffcalc.gdasupport.minigda.scannable import ScannableGroup
    from diffcalc.gdasupport.minigda.scannable import SingleFieldDummyScannable as Dummy

from diffcalc.hardware import ScannableHardwareAdapter
import diffcalc.hkl.you.geometry
from diffcalc.ub.persistence import UbCalculationNonPersister
from diffcalc import settings

import diffcmd.ipythonmagic