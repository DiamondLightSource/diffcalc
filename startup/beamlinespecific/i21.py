'''
Created on 19 Feb 2017

@author: zrb13439
'''
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase,\
    ScannableBase
from math import pi

# TP_HELP="""
# Use the Scannables tplab, tplabx, tplaby, tplabz to move the configured tool point in
# the lab frame. For example to move it to the centre of the diffractomter:
# 
#    >>> pos tplab [0 0 0]  # Move the toolpoint 
#     
# use 'settp' to change the configured toolpoint in the phi frame:
# 
#    >>> pos tphi [0 0 1]  # will not move anything
#    
# or use it with no args to make the location in the phi frame currently in
# the centre of the diffracomtter the tool point. i.e. to make the tblab
# report back [0 0 0]
# """
TP_HELP="""

For help with sa, tp_phi and tp_lab see: http://confluence.diamond.ac.uk/x/CBIAB
"""

from diffcalc.hkl.you.geometry import calcETA, calcCHI, calcPHI


try:
    from numpy import matrix
except ImportError:
    from numjy import matrix

TORAD = pi / 180
TODEG = 180 / pi


DEBUG = False

def calc_tp_lab(tp_phi_tuple, eta, chi, phi, xyz_eta=[0, 0, 0]):
    tp_phi = matrix(tp_phi_tuple).T
    ETA = calcETA(eta * TORAD)
    CHI = calcCHI(chi * TORAD)
    PHI = calcPHI(phi * TORAD)
    xyz_eta = matrix(xyz_eta).T
    
    tp_lab = ETA * (xyz_eta + (CHI * PHI * tp_phi))
    return list(tp_lab.T.tolist()[0])


def calc_tp_eta(tp_phi_tuple, chi, phi):
    return calc_tp_lab(tp_phi_tuple, 0, chi, phi, [0, 0, 0])


def move_lab_origin_into_phi(chi, phi, xyz_eta_tuple):
    # the inverse of calc_tp_lab with tp_lab=0:
    CHI = calcCHI(chi * TORAD)
    PHI = calcPHI(phi * TORAD)
    xyz_eta = matrix(xyz_eta_tuple).T
    tp_phi = PHI.I * CHI.I * (-1 * xyz_eta)
    return list(tp_phi.T.tolist()[0])
    

def _format_vector(vector, fmt = '%7.4f'):
    vals = [fmt % e for e in vector]
    return ' '.join(vals)


class I21SampleStage(ScannableMotionWithScannableFieldsBase):
    
    def __init__(self, name, pol_scn, tilt_scn, az_scn, xyz_eta_scn):
        
        self.setName(name)
        self._scn_list = [pol_scn, tilt_scn, az_scn]
        self.xyz_eta_scn = xyz_eta_scn
        
        self.setInputNames([pol_scn.getName(), tilt_scn.getName(), az_scn.getName()])  # note, names copied below
        self.setOutputFormat(['%7.5f'] * 3)
        self.completeInstantiation()
        
        #  tp_phi is the TARGET tool point to end up at the diffractometer centre
        self.tp_phi = [0, 0, 0]
        
        self.tp_phi_scannable = I21SampleStage.TpPhiScannable('tp_phi', self)
    
    def asynchronousMoveTo(self, pos_triple):

        if len(pos_triple) != 3:
            raise ValueError(self.getName() + ' device expects three inputs')
        
        # Move pol, tilt & az (None if not to be moved)
        pol, tilt, az = pos_triple         
        if pol is not None:
            self._scn_list[0].asynchronousMoveTo(pol)
        if tilt is not None:
            self._scn_list[1].asynchronousMoveTo(tilt)
        if az is not None:
            self._scn_list[2].asynchronousMoveTo(az)
            
        _, tilt, az = self.completePosition(pos_triple)
        chi = tilt + 90
        phi = az
        tp_offset_eta = calc_tp_eta(self.tp_phi, chi, phi)
        if DEBUG:
            print ('{Correcting xyz_eta for '
                   'tilt(chi-90)=%.2f & az(phi)=%.2f}' % (tilt, az)).rjust(79)
        xyz = [-1 * e for e in tp_offset_eta]
        self.xyz_eta_scn.asynchronousMoveTo(xyz)
               
    def rawGetPosition(self):
        return [scn.getPosition() for scn in self._scn_list]
    
    def getFieldPosition(self, i):
        return self._scn_list[i].getPosition()
    
    def isBusy(self):
        return (any([scn.isBusy() for scn in self._scn_list])
                or self.xyz_eta_scn.isBusy())
    
    def waitWhileBusy(self):
        for scn in self._scn_list:
            scn.waitWhileBusy()
        self.xyz_eta_scn.waitWhileBusy()
        
    def __repr__(self):
        
        # Sample angle columns
        pos = self.getPosition()
        formatted_values = self.formatPositionFields(pos)
        
        sa_col = []
        sa_col.append('%s:' % self.getName())
        sa_col.append('sapolar:   %s (eta)' % formatted_values[0])
        sa_col.append('satilt:    %s (chi-90)' % formatted_values[1])
        sa_col.append('saazimuth: %s (phi)' % formatted_values[2])
        sa_col_width = len(sa_col[2])
        
        # Toolpoint column
        xyz_eta = list(self.xyz_eta_scn.getPosition())
        eta, chi, phi = self.getEulerPosition()
        tp_lab = calc_tp_lab(self.tp_phi, eta, chi, phi, xyz_eta)
        
        tp_col = []
        tp_col.append('')
        tp_col.append('tp_phi : %s (set)' % _format_vector(self.tp_phi))
        tp_col.append('tp_lab : %s' % _format_vector(tp_lab))
        tp_col.append('xyz_eta: %s' % _format_vector(xyz_eta))
        
        # Combine columns
        lines = []
        while sa_col or tp_col:
            sa_row = sa_col.pop(0) if sa_col else ''
            tp_row = tp_col.pop(0) if tp_col else ''
            lines.append(sa_row.ljust(sa_col_width + 3) + tp_row)
  
        # Add some help
        return '\n'.join(lines) + TP_HELP
    
    def getEulerPosition(self):
        pol, tilt, az = self.getPosition()
        eta, chi, phi = pol,  tilt + 90, az
        return eta, chi, phi

    class TpPhiScannable(ScannableBase):
    
        def __init__(self, name, i21_sample_stage):
            self.name = name
            self.i21_sample_stage = i21_sample_stage
            self.inputNames = [name + 'x', name +'y', name + 'z']
            self.outputFormat = ['% 6.4f'] * 3
            self.level = 3
    
        def isBusy(self):
            return False
    
        def waitWhileBusy(self):
            return
    
        def asynchronousMoveTo(self, new_position):
            if len(new_position) != 3:
                raise TypeError('Expected 3 element target')
            self.i21_sample_stage.tp_phi = list(new_position)
    
        def getPosition(self):
            return list(self.i21_sample_stage.tp_phi)
        
    def zerosample(self):
        """Calculate tp_phi from the currently centred sample location."""
        _, chi, phi = self.getEulerPosition()
        xyz_eta_tuple = self.xyz_eta_scn.getPosition()
        tp_phi = move_lab_origin_into_phi(chi, phi, xyz_eta_tuple)
        self.tp_phi = tp_phi
        print "tp_phi set to: %s" % tp_phi
        
    def centresample(self):
        """Centre the sample. Equivilent to moving sa to its current position."""
        self.asynchronousMoveTo([None, None, None])
        self.waitWhileBusy()
            

class I21DiffractometerStage(ScannableMotionWithScannableFieldsBase):
    
    def __init__(self, name, delta_scn, sample_stage_scn, chi_offset,
                 delta_offset=0):
        """Create diffractomter stage from 3circle sample axes and a
        delta/tth axis.
        
        Both the chi and delta offsets are added to underlying scannable values
        when *reading* the position. iu the same offset is subtracted when
        *setting* the position. 
        """
        
        self.sample_stage_scn = sample_stage_scn
        self.delta_scn = delta_scn
        self.chi_offset = chi_offset
        self.delta_offset = delta_offset
        self.setName(name)
          
        self.setInputNames(['delta', 'eta', 'chi', 'phi'])  # note, names copied below
        self.setOutputFormat(['%7.4f'] * 4)
        self.completeInstantiation()
    
    def asynchronousMoveTo(self, pos_quadruple):
        if len(pos_quadruple) != 4:
            raise ValueError(self.getName() + ' device expects four inputs')
        
        delta, eta, chi, phi = pos_quadruple              
        pol = eta
        tilt = chi - self.chi_offset if (chi is not None) else None
        az = phi
        
        if delta is not None:
            self.delta_scn.asynchronousMoveTo(delta - self.delta_offset)
        
        if (pol is not None) or (tilt is not None) or (az is not None):
            self.sample_stage_scn.asynchronousMoveTo([pol, tilt, az])
               
    def rawGetPosition(self):
        delta = self.delta_scn.getPosition()
        pol, tilt, az = self.sample_stage_scn.getPosition()
        eta, chi, phi = pol, tilt + self.chi_offset, az
        return delta + self.delta_offset, eta, chi, phi
    
    def getFieldPosition(self, i):
        return self.getPosition()[i]
    
    def isBusy(self):
        return self.delta_scn.isBusy() or self.sample_stage_scn.isBusy()
    
    def waitWhileBusy(self):
        self.delta_scn.waitWhileBusy()
        self.sample_stage_scn.waitWhileBusy()
        
    def __repr__(self):
        vals = self.formatPositionFields(self.getPosition())
        lines = []
        for name, val, hint in zip(self.getInputNames(), vals, self.get_hints()):
            lines.append('%-6s : %s%s' % (name, val, hint))
        return '\n'.join(lines)

    def get_hints(self):
        sample_names = self.sample_stage_scn.getInputNames()
        hints = []
        if self.delta_offset != 0:
            sign = '+' if self.delta_offset > 0 else '-'
            hints.append(' (%s %s %s)' % 
                         (self.delta_scn.getName(), sign, abs(self.delta_offset)))                # delta
        else:
            hints.append(' (%s)' % self.delta_scn.getName())                # delta
        hints.append(' (%s)' % sample_names[0])                         # eta
        hints.append(' (%s + %s)' % (sample_names[1], self.chi_offset)) # chi
        hints.append(' (%s)' % sample_names[2])                         # phi
        return hints
 
 
class I21TPLab(ScannableMotionWithScannableFieldsBase):
    
    def __init__(self, name, sample_stage_scn):
        
        self.name = name
        self.sample_stage_scn = sample_stage_scn
          
        self.setInputNames([name + 'x', name + 'y', name + 'z'])  # note, names copied below
        self.setOutputFormat(['%7.4f'] * 3)
        self.completeInstantiation()
        self.setAutoCompletePartialMoveToTargets(True)

    
    def rawAsynchronousMoveTo(self, tp_lab_target):
        if len(tp_lab_target) != 3:
            raise ValueError(self.getName() + ' device expects three inputs')
        
        if None in tp_lab_target:
            raise ValueError('unexpected None in tp_lab_target: ', tp_lab_target)

        eta, chi, phi = self.sample_stage_scn.getEulerPosition()        
        ETA = calcETA(eta * TORAD)

        # Move tp target from lab frame inwards to eta frame
        tp_lab_target = matrix(tp_lab_target).T
        tp_eta_target = ETA.T * tp_lab_target  # ETA.I == ETA.T

        # Move configured tp from phi frame outwards to eta frame
        tp_eta = calc_tp_eta(self.sample_stage_scn.tp_phi, chi, phi)
        
        # Calculate offset required to align the two
        xyz_eta = tp_eta_target - matrix(tp_eta).T
        xyz_eta = xyz_eta.T.tolist()[0]
        
        self.sample_stage_scn.xyz_eta_scn.asynchronousMoveTo(xyz_eta)        
        
    def rawGetPosition(self):
        tp_phi = list(self.sample_stage_scn.tp_phi)
        eta, chi, phi = self.sample_stage_scn.getEulerPosition()
        xyz_eta = self.sample_stage_scn.xyz_eta_scn.getPosition()
        
        tp_lab = calc_tp_lab(tp_phi, eta, chi, phi, xyz_eta)
        return tp_lab
    
    def getFieldPosition(self, i):
        return self.getPosition()[i]
    
    def isBusy(self):
        return self.sample_stage_scn.xyz_eta_scn.isBusy()
    
    def waitWhileBusy(self):
        self.self.sample_stage_scn.xyz_eta_scn.waitWhileBusy()
        