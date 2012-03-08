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

try:
    import diffcalc
except ImportError:
    from gda.data.PathConstructor import createFromProperty
    import sys
    gda_root = createFromProperty("gda.root")
    diffcalc_path = gda_root.split('/plugins')[0] + '/diffcalc'
    sys.path = [diffcalc_path] + sys.path
    print diffcalc_path + ' added to GDA Jython path.'
    import diffcalc  # @UnusedImport
from diffcalc.gdasupport.factory import \
    create_objects, add_objects_to_namespace

demoCommands = []
demoCommands.append("newub 'cubic'")
demoCommands.append("setlat 'cubic' 1 1 1 90 90 90")
demoCommands.append("pos wl 1")
demoCommands.append("pos sixc [0 90 0 45 45 0]")
demoCommands.append("addref 1 0 1")
demoCommands.append("pos phi 90")
demoCommands.append("addref 0 1 1")
demoCommands.append("checkub")
demoCommands.append("ub")
demoCommands.append("hklmode")


print "=" * 80
diffcalcObjects = create_objects(
    dummy_axis_names=('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'),
    dummy_energy_name='en',
    geometry='sixc',
    hklverbose_virtual_angles_to_report=('2theta', 'Bin', 'Bout', 'azimuth'),
    demo_commands=demoCommands
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())


print diffcalcObjects['ub'].__doc__
print "***"
print diffcalcObjects['hkl'].__doc__
print "***"
