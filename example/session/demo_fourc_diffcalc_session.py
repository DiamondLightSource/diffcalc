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

#@PydevCodeAnalysisIgnore

remove_default counterTimer01
## 0. Jython GDA
# Jython with aliased commands to becomre extended syntax
1+1
print "hello"
pos(phi)
pos phi

## 1. Moving scannales
pos
pos energy
pos energy 10
pos fourc
pos tth 0
pos fourc
pos fourc [0 0 0 0]
scan energy 9.5 10.5 .1
scan energy 9.5 10.5 .1 wl

## 2. Orientation
helpub
ub
newub 'fromDiffcalcItself'
setlat 'xtal' 3.8401 3.8401 5.43072
ub
pos energy 10
pos fourc [22.790 1.552 22.400 14.255]
addref 1 0 1.0628
pos fourc [22.790 4.575 24.275 101.320]
addref 0 1 1.0628
checkub()
# or this can be done interactively
ub

## 3. Driving in hkl	
helphkl
hklmode 1

sim hkl [1 0 0]
pos hkl [1 0 0]
pos fourc
fourc 
sim fourc [17.6881795444401, 8.844089772219766, -14.51748633854629, -1.5841256056732362]

scan h .9 1.1 .02
scan h .9 1.1 .02 fourc
scan h .9 1.1 .02 hklverbose
scan hkl [1 0 1] [1.1 0 1.1] [.01 0 .01]
scan h 1 1.1 .05 k 1 1.1 .05 l

## 4. Modes and parameters
hklmode

helphkl

# Incoming angle fixed 
# surface normal calibration with sigtau)
hklmode 2
setbetain 2
pos hkl [1 0 1]   #??? -ve Bout if 'pos h 1' here ???
hklverbose
scan betain 2 3 .1 hklverbose [1 0 1]

# Phi fixed
hklmode 5
setbetain 5 # warning
setphi 5
pos hkl [1 0 1]
fourc	# ??? Comes out as -175

 

