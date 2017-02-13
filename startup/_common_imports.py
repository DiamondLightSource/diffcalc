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


from __future__ import absolute_import

import os, sys

from diffcalc.hardware import ScannableHardwareAdapter
import diffcalc.hkl.you.geometry
from diffcalc.ub.persistence import UbCalculationNonPersister, UBCalculationJSONPersister
from diffcalc import settings
import diffcalc.util

   
try:
    from gda.device.scannable.scannablegroup import ScannableGroup
    from gdascripts.scannable.dummy import SingleInputDummy as Dummy
    from diffcmd.diffcmd_utils import alias_commands
    GDA = True  
except ImportError:
    # Not running in gda environment so fall back to minigda emulation
    from diffcalc.gdasupport.minigda.scannable import ScannableGroup
    from diffcalc.gdasupport.minigda.scannable import SingleFieldDummyScannable as Dummy
    GDA = False


if GDA:
    settings.ubcalc_persister = UbCalculationNonPersister()
# else: the diffalc.py program sets this if used outside GDA    

if isinstance(settings.ubcalc_persister, UbCalculationNonPersister):
    print "WARNING: persistence not configured"


