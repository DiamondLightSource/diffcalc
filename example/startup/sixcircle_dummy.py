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

print "=" * 80

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
_demo = []
_demo.append("pos wl 1")
_demo.append("en")
_demo.append("newub 'test'")
_demo.append("setlat 'cubic' 1 1 1 90 90 90")
_demo.append("c2th [1 0 0]")
_demo.append("pos sixc [0 60 0 30 0 0]")
_demo.append("addref 1 0 0 'ref1'")
_demo.append("c2th [0 1 0]")
_demo.append("pos phi 90")
_demo.append("addref 0 1 0 'ref2'")
_demo.append("checkub")

axis_names = ('mu', 'delta', 'nu', 'eta', 'chi', 'phi')
virtual_angles = ('theta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta')
_objects = create_objects(
    engine_name='you',
    geometry='sixc',
    dummy_axis_names=axis_names,
    dummy_energy_name='en',
    hklverbose_virtual_angles_to_report=virtual_angles,
    simulated_crystal_counter_name='ct',
    demo_commands=_demo
    )

#_objects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(_objects, globals())
a_eq_b ='a_eq_b'

# TODO: Tidy these hacks:
en.setLevel(4)
hkl.setLevel(5) #@UndefinedVariable

print '=' * 80

def help_hkl():
    print hkl.__doc__
    
alias('help_hkl')
