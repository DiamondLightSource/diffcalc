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

import os


# This file must be run with execfile after diffcalc has started
COMMON_STARTUP_MAGIC_OR_ALIAS_FILE = os.path.join(os.path.split(__file__)[0], 'common_startup_magic_or_alias.py')


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
from diffcalc.ub.persistence import UbCalculationNonPersister, UBCalculationJSONPersister
from diffcalc import settings
import diffcalc.util

if GDA:
    ubcalc_persister = UbCalculationNonPersister()
    print "WARNING: persistence not configured properly for GDA use yet"
else:
    diffcalc_var =os.getenv('DIFFCALC_VAR')
    if not os.path.exists(diffcalc_var):
        os.makedirs(diffcalc_var)
    ubcalc_persister = UBCalculationJSONPersister(diffcalc_var)
    
if not GDA:
    diffcalc.util.DEBUG = os.getenv('DIFFCALC_DEBUG', False) == 'True'
    if diffcalc.util.DEBUG:
        print "WARNING: Diffcalc debug mode on. Help for command syntax errors disabled."

