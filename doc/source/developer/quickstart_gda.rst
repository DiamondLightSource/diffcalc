.. _quickstart-opengda:

Quick-start: OpenGDA
====================

Install
-------

Copy the Diffcalc folder into the gda root folder (i.e. so it sits alongside
plugins, thirdparty etc.)

Start diffcalc
--------------

Diffcalc is started from the command line or it can be started in localStation
automatically. To start a dummy sixcircle installation::

   >>> diffcalc_path = gda.data.PathConstructor.createFromProperty("gda.root").split('/plugins')[0]
       + '/diffcalc'
   >>> execfile(diffcalc_path + '/example/startup/sixcircle_dummy.py')
   
   /scratch/ws/8_4/diffcalc added to GDA Jython path.
   ================================================================================
   Created DummyPD: alpha
   Created DummyPD: delta
   Created DummyPD: gamma
   Created DummyPD: omega
   Created DummyPD: chi
   Created DummyPD: phi
   Created diffractometer scannable: sixc
   Created dummy energy scannable:  en
   Set dummy energy to 1 Angstrom
   Created wavelength scannable: wl
   Created hkl scannable: hkl
   Created hkl component scannables: h, k & l
   Created verbose hkl scannable: hklverbose. Reports virtual angles: 2theta, Bin, Bout, azimuth
   Created parameter scannable: phi_par
   Created parameter scannable: alpha_par
   Created parameter scannable: oopgamma
   Created parameter scannable: betaout
   Created parameter scannable: azimuth
   Created parameter scannable: betain
   Created parameter scannable: blw
   Aliased command: addref
   Aliased command: autosector
   Aliased command: calcub
   Aliased command: checkub
   Aliased command: dcversion
   Aliased command: delref
   Aliased command: editref
   Aliased command: handleInputError
   Aliased command: helphkl
   Aliased command: helpub
   Aliased command: hklmode
   Aliased command: listub
   Aliased command: loadub
   Aliased command: mapper
   Aliased command: newub
   Aliased command: raiseExceptionsForAllErrors
   Aliased command: saveubas
   Aliased command: sector
   Aliased command: setcut
   Aliased command: setlat
   Aliased command: setmax
   Aliased command: setmin
   Aliased command: setpar
   Aliased command: setu
   Aliased command: setub
   Aliased command: showref
   Aliased command: sigtau
   Aliased command: sim
   Aliased command: swapref
   Aliased command: trackalpha
   Aliased command: trackgamma
   Aliased command: trackphi
   Aliased command: transforma
   Aliased command: transformb
   Aliased command: transformc
   Aliased command: ub
   Aliased command: diffcalcdemo
   ================================================================================
   Try the following:
   newub 'cubic'
   setlat 'cubic' 1 1 1 90 90 90
   pos wl 1
   pos sixc [0 90 0 45 45 0]
   addref 1 0 1
   pos phi 90
   addref 0 1 1
   checkub
   ub
   hklmode
   
   Or type 'diffcalcdemo' to run this script (Caution, will move the diffractometer!)
   ================================================================================
   Added objects/methods to namespace: gamma, trackalpha, phi, diffcalc_object, editref,
   transformc, newub, setub, setpar, transforma, setu, off, autosector, dcversion, betaout,
   sector, swapref, showref, setmin, trackgamma, ub, oopgamma, transformb, handleInputError,
   l, listub, chi, manual, helpub, helphkl, azimuth, wl, setlat, sim, trackphi, alpha,
   sigtau, omega, raiseExceptionsForAllErrors, saveubas, delref, hklmode, calcub, blw,
   k, setcut, en, diffcalcdemo, sixc, hklverbose, addref, h, delta, betain, setmax, auto,
   checkub, hkl, mapper, on, loadub, phi_par, alpha_par

Notice that this example script creates dummy scannables for the six axes and energy.

To use preexisting scannables modify::

   diffcalcObjects = createDiffcalcObjects(
       dummyAxisNames = ('alpha', 'delta', 'gamma', 'omega', 'chi', 'phi'),
       dummyEnergyName = 'en',
       geometryPlugin = 'sixc',
       hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth'),
       demoCommands = demoCommands
   )
   
 to::
   
   diffcalcObjects = createDiffcalcObjects(
       axisScannableList = (alpha, delta, gamma, omega, chi, phi),
       energyScannable = en,
       geometryPlugin = 'sixc',
       hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth'),
       demoCommands = demoCommands
   )
 
Check out the user manual doc/user/manual.html . Also type diffcalcdemo to run
the example session displayed above.
