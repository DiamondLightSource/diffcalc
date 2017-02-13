from startup._common_imports import *


### Create dummy scannables ###
print "Diffcalc creating dummy Scannables as _fivec and en were not found"
print "Dummy scannables: _fivec(delta, gam, eta, chi, phi) and en"
delta = Dummy('delta')
gam = Dummy('gam')
eta = Dummy('eta')
chi = Dummy('chi')
phi = Dummy('phi')
_fivec = ScannableGroup('_fivec', (delta, gam, eta, chi, phi))
en = Dummy('en')
en.level = 3


### Configure and import diffcalc objects ###
ESMTGKeV = 1
settings.hardware = ScannableHardwareAdapter(_fivec, en, ESMTGKeV)
settings.geometry = diffcalc.hkl.you.geometry.FiveCircle()
settings.energy_scannable = en
settings.axes_scannable_group = _fivec
settings.energy_scannable_multiplier_to_get_KeV = ESMTGKeV

from diffcalc.gdasupport.you import *  # @UnusedWildImport

if GDA:
    print "Running in GDA --- aliasing commands"
    alias_commands(globals())
    
lastub()  # Load the last ub calculation used

### create demo scenarios for manual ###
try:
    __IPYTHON__  # @UndefinedVariable
    IPYTHON = True
except NameError:
    IPYTHON = False

def demo_all():

    print "ORIENT\n"
    demo_orient()

    print "CONSTRAIN\n"
    demo_constrain()
    
    print "SCAN\n"
    demo_scan()


def echo(cmd):
    print "\n>>> " + str(cmd)
    
if IPYTHON:
    from IPython import get_ipython

    def echorun(magic_cmd):
        echo(magic_cmd)
        get_ipython().magic(magic_cmd)   

def demo_orient():
    if IPYTHON:
        echorun("help ub")
    else:
        echo("help(ub)")
        print ub.__doc__   # @UndefinedVariable

    if IPYTHON:
        echorun("pos wl 1")
    else:
        echo("pos(wl, 1)")
        print pos(wl, 1)  # @UndefinedVariable

    if IPYTHON:
        echorun("newub 'test'")
    else:
        echo("newub('test')")
        print newub('test')  # @UndefinedVariable

    if IPYTHON:
        echorun("setlat 'cubic' 1 1 1 90 90 90")
    else:
        echo("setlat('cubic', 1, 1, 1, 90, 90, 90)")
        setlat('cubic', 1, 1, 1, 90, 90, 90)  # @UndefinedVariable

    if IPYTHON:
        echorun("ub")
    else:
        echo("ub()")
        ub()  # @UndefinedVariable

    # add 1st reflection
    if IPYTHON:
        echorun("c2th [1 0 0]")
    else:
        echo("c2th([1, 0, 0])                            # energy from hardware")
        print c2th([1, 0, 0])  # @UndefinedVariable

    if IPYTHON:
        echorun("pos fivec [60 0 30 0 0]")
    else:
        echo("pos(fivec, [60, 0, 30, 0, 0])")
        pos(fivec, [60, 0, 30, 0, 0])  # @UndefinedVariable

    if IPYTHON:
        echorun("addref [1 0 0]")
    else:
        echo("addref([1, 0, 0])                          # energy from hardware")
        addref([1, 0, 0])  # @UndefinedVariable

    # ad 2nd reflection
    if IPYTHON:
        echorun("c2th [0 1 0]")
    else:
        echo("c2th([0, 1, 0])                            # energy from hardware")
        print c2th([0, 1, 0])  # @UndefinedVariable

    if IPYTHON:
        echorun("pos phi 90")
    else:
        echo("pos(phi, 90)")
        print pos(phi, 90)  # @UndefinedVariable

    if IPYTHON:
        echorun("addref [0 1 0]")
    else:
        echo("addref([0, 1, 0])")
        addref([0, 1, 0])  # @UndefinedVariable

    if IPYTHON:
        echorun("ub")
    else:
        echo("ub()")
        ub()  # @UndefinedVariable

    if IPYTHON:
        echorun("checkub")
    else:
        echo("checkub()")
        checkub()  # @UndefinedVariable


def demo_constrain():
    if IPYTHON:
        echorun("help hkl")
    else:
        echo("help(hkl)")
        print hkl.__doc__  # @UndefinedVariable

    if IPYTHON:
        echorun("con qaz 90")
    else:    
        echo("con('qaz', 90)")
        con('qaz', 90)  # @UndefinedVariable

    if IPYTHON:
        echorun("con a_eq_b")
    else:        
        echo("con('a_eq_b')")
        con('a_eq_b')  # @UndefinedVariable

    if IPYTHON:
        echorun("con")
    else:       
        echo("con()")
        con()  # @UndefinedVariable

    if IPYTHON:
        echorun("setmin delta 0")
    else:       
        echo("setmin(delta, 0)")
        setmin(delta, 0)  # @UndefinedVariable

    if IPYTHON:
        echorun("setmin chi 0")
    else:       
        echo("setmin(chi, 0)")
        setmin(chi, 0)  # @UndefinedVariable


def demo_scan():

    if IPYTHON:
        echorun("pos hkl [1 0 0]")
        echorun("scan delta 40 80 10 hkl ct 1")
    else:        
        echo("pos(hkl, [1, 0, 0])")
        pos(hkl, [1, 0, 0])  # @UndefinedVariable
        echo("scan(delta, 40, 80, 10, hkl, ct, 1)")
        scan(delta, 40, 80, 10, hkl, ct, 1)  # @UndefinedVariable

    if IPYTHON:
        echorun("pos hkl [0 1 0]")
        echorun("scan h 0 1 .2 k l fivec ct 1")
    else:
        echo("pos(hkl, [0, 1, 0])")
        pos(hkl, [0, 1, 0])  # @UndefinedVariable
        echo("can(h, 0, 1, .2, k, l, fivec, ct, 1)")
        scan(h, 0, 1, .2, k, l, fivec, ct, 1)  # @UndefinedVariable

    if IPYTHON:
        echorun("con psi")
        echorun("scan psi 0 90 10 hkl [1 0 1] eta chi phi ct .1")
    else: 
        echo("con(psi)")
        con(psi)  # @UndefinedVariable
        echo("scan(psi, 0, 90, 10, hkl, [1, 0, 1], eta, chi, phi, ct, .1)")
        scan(psi, 0, 90, 10, hkl, [1, 0, 1], eta, chi, phi, ct, .1)  # @UndefinedVariable
