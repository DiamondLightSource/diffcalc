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

"""
This file contains an example of how to add Diffcalc to the GDA's Jython path.
It assumes Diffcalc is installed next to the gda's 'plugin' folder.
"""

import sys

from gda.data.PathConstructor import createFromProperty


gda_root = createFromProperty("gda.root")
diffcalc_path = gda_root.split('/plugins')[0] + '/diffcalc'
sys.path.insert(0, diffcalc_path)
print diffcalc_path + ' added to GDA Jython path.'
