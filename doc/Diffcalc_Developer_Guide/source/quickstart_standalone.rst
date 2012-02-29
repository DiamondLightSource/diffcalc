Quick-Start outside OpenGDA
===========================

This is for those who want to use Diffcalc outside the gda. It might also
help with development.

Setup environment
-----------------

Change directory to the diffcalc project::

   $ cd diffcalc
   $ ls
   BUGS.txt     diffcalc  example      #  RELEASE-NOTES.txt  THANKS.txt
   COPYING.txt  docs      HISTORY.txt  README.txt    test

If using Python make sure numpy and diffcalc can be imported::

   $ PYTHONPATH=$PYTHONPATH:<diffcalc_root>
   $ python   #use python2.4 at Diamond
   Type "help", "copyright", "credits" or "license" for more information.
   >>> import numpy
   >>> import diffcalc

If using Jython make sure Jama and diffcalc can be imported::
   
   $ jython -Dpython.path=<diffcalc_root>:<path_to_Jama>/Jama-1.0.1.jar

   Jython 2.2.1 on java1.5.0_11
   Type "copyright", "credits" or "license" for more information.
   >>> import Jama
   >>> import diffcalc


Start standalone
----------------
If you just want to try Diffcalc out as a user skip to the following section.
To try out the code without using an external framework use the
sixcircle.py example startup script (notice the -i)::

   $ python2.4 -i example/startup/sixcircle.py
   >>> mon
   BaseHarwdareMonitor:
     energy : 12.39842 keV
     wavelength : 1.0 Angstrom
     delta : 0.0 deg
     gamma : 0.0 deg
     omega : 0.0 deg
     chi : 0.0 deg
     phi : 0.0 deg
   >>> dc.newub('demo')
   >>> dc.setlat('xtal', 3.8401, 3.8401, 5.43072)
   >>> mon.setWavelength(1.24)
   >>> mon.setPosition((5.000, 22.790, 0.000, 1.552, 22.400, 14.255))
   >>> dc.addref(1, 0, 1.0628)
   >>> mon.setPosition((5.000, 22.790, 0.000, 4.575, 24.275, 101.320))
   >>> dc.addref(0, 1, 1.0628)
   Calculating UB matrix.

   >>> dc.checkub()
      energy h    k    l     h_comp k_comp l_comp  tag
   1  9.9987 1.00 0.00 1.06  1.0000 0.0000 1.0628
   2  9.9987 0.00 1.00 1.06  -0.0329 1.0114 1.0400
   
   >>> dc._hklToAngles(1,0,1.06) ((0.0, 23.281254709199715, 0.0,
   11.640627354599907, 34.44739540990696, 3.21328587062226), {'Bin':
   6.5535895349220628, 'theta': 70702.991919143591, 'Bout':
   6.5535895349220628, '2theta': 23.281254709199715, 'azimuth':
   4.6282344679186878})
   
   >>> dc._anglesToHkl((0.0, 23.281254709199715, 0.0, 11.640627354599907,
   34.44739540990696, 3.21328587062226)) ((0.99999999999999989,
   -2.0078068981715935e-16, 1.0599999999999994), {'Bin': 1234, 'theta':
   1234, 'Bout': 1234, '2theta': 1234, 'azimuth': 1234})

Start with minigda
------------------
The minigda framework in ``diffcalc/external/minigda`` provides a
class Scannable of objects that can be moved or read in a scan, a
``pos`` command for moving or reading their positions, a ``scan``
command and a translator for mapping easy-to-type commands into method
calls.

To install standalone or within the Minigda framework simply copy the
projects directory somewhere handy. To install into the gda copy (or
link) the diffcalc package (it should contain an ``__init__.py`` file)
from within the main diffcalc project

To start the minigda::

   $ python -t diffcalc/external/minigda/minigda.py
   ============================================================================
   Starting minigda on linux2 at Fri Jan 30 15:52:12 2009 ...
   ============================================================================
   sys.argv:  ['diffcalc/external/minigda/minigda.py']
   ============================================================================
   WARNING: No startup script specified.
   Starting minigda terminal. Type exit or press ctrl-d to return to Python   
    
   gda>>>pos

Typing pos would display the scannables positions if there were
any. Press ctrl-d to exit the translator into regular Python, and then
term.start() to start again::

   gda>>> pos
   gda >>>dir()
   Error: 'dir' is not an aliased command, Scannable, or comment.
   (Hint: unlike the gda system, the minigda does not currently
   support regular Python syntax.)
   gda>>> exit
    
   >>> dir()
   ['Pos', 'STARTUPSCRIPT', 'Scan', 'ScanDataPrinter',
   'TerminalAliasedCommandsOnly', '__builtins__', '__doc__',
   '__file__', '__name__', 'alias', 'main', 'os', 'pos', 'run',
   'scan', 'sys', 'term', 'time', 'usage']
    
   >>> term.start()
   Starting minigda terminal. Type exit or press ctrl-d to return to Python
   gda>>>

To tryout diffcalc within the minigda framework in earnest pass
minigda the argument ``example/startup/sixcircle_with_scannables.py``.
With Jython for example::

    $ jython -Dpython.path=/path_to_workspace/diffcalc/:path_to_workspace/...
          ... gda_trunk_for_diffcalc/jars/Jama-1.0.1.jar...
          ... -i diffcalc/external/minigda/minigda.py example/startup/sixcircle_with_scannables.py
    ================================================================================
    Starting minigda on java1.5.0_11 at Fri Feb 27 11:34:46 2009 ...
    ================================================================================
    sys.version: 2.2.1
    os.getcwd(): /home/zrb13439/synched/workspace/diffcalc
    ================================================================================
    Running startup scipt 'example/startup/sixcircle_with_scannables.py' ...

    WARNING: ExampleSixCircleStartup.py is not running within the GDA: falling back to the (very minimal!) minigda...
    Starting minigda terminal. Type exit or press ctrl-d to return to Python

    gda>>>pos
    alpha:    0.0000
    alpha_par:0.00000
    azimuth:  ---
    betain:   ---
    betaout:  ---
    chi:      0.0000
    cnt:      0.0000
    delta:    0.0000
    en:       12.3984
    gamma:    0.0000
    gamma_par:0.00000
    h:        Error: No UB matrix has been calculated during this ub calculation
    hkl:      Error: No UB matrix has been calculated during this ub calculation
    k:        Error: No UB matrix has been calculated during this ub calculation
    l:        Error: No UB matrix has been calculated during this ub calculation
    omega:    0.0000
    phi:      0.0000
    phi_par:  ---
    sixc:     alpha: 0.0000 delta: 0.0000 gamma: 0.0000 omega: 0.0000 chi: 0.0000 phi: 0.0000
    wl:       1.0000
    gda>>>
