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
    __IPYTHON__  # @UndefinedVariable
    IPYTHON = True
except NameError:
    IPYTHON = False

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


HELP_STRING = \
"""Quick:  https://github.com/DiamondLightSource/diffcalc/blob/master/README.rst
Manual: http://diffcalc.readthedocs.io/en/latest/youmanual.html
Type:   > help ub
        > help hkl"""


if GDA:
    from gda.configuration.properties import LocalProperties
    var_folder = LocalProperties.get("gda.var")
    diffcalc_persistance_path = os.path.join(var_folder, 'diffcalc')
    if not os.path.exists(diffcalc_persistance_path):
        print "Making diffcalc var folder:'%s'" % diffcalc_persistance_path
        os.makedirs(diffcalc_persistance_path)
    settings.ubcalc_persister = UBCalculationJSONPersister(diffcalc_persistance_path)
# else: should have been set if outside GDA



