'''
Created on 1 Nov 2018

@author: voo82357
'''
from diffcalc.util import allnum, DiffcalcException, TODEG
from diffcalc.gdasupport.scannable.sim import sim
from diffcalc.util import getInputWithDefault

def setref2(scn, hkl):
    """setref2 scn [h k l] -- setup hkloffset scannable to scan for second reflection [hkl]"""
    
    if not isinstance(hkl, (tuple, list)):
        raise DiffcalcException("Please specify hkl values for a second reference reflection to search.")

    if not allnum(hkl):
        raise DiffcalcException("Please specify numeric values for hkl.")

    try:
        hkl_ref = scn._diffcalc._ub.ubcalc.get_reflection(0)[0]
    except IndexError:
        raise DiffcalcException("Please add one reference reflection into the reflection list.")
    pol, az, sc = scn._diffcalc._ub.ubcalc.calc_offset_for_hkl(hkl, hkl_ref)
    hkl_rot = [sc * val for val in hkl_ref]
    hkl_sc = hkl_rot[:]
    hkl_rot.extend([pol * TODEG, az * TODEG])
    hkl_sc.extend([0, 0])

    print ('\nRescaled hkl reference for second reflection : %9.4f  %.4f  %.4f' % (hkl_sc[0], hkl_sc[1], hkl_sc[2]))
    print ('         polar and azimuthal rotation angles : %9.4f  %.4f\n' % (pol * TODEG, az * TODEG))

    sim(scn, hkl_sc)
    print ('IMPORTANT: Applying subsequent polar and azimuthal rotations might fail. In this case, please manually\n'
           '           find accessible azimuthal rotation range to scan for second reference reflection.')
    reply = getInputWithDefault('Move to rescaled hkl position', 'y')
    if reply in ('y', 'Y', 'yes'):
        scn.asynchronousMoveTo(hkl_sc)
    else:
        print 'Aborting'
        return

    sim(scn, hkl_rot)
    reply = getInputWithDefault('Apply polar and azimuthal rotations', 'y')
    if reply in ('y', 'Y', 'yes'):
        scn.asynchronousMoveTo(hkl_rot)
    else:
        print 'Aborting'
        return