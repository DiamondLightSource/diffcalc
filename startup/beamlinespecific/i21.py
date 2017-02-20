'''
Created on 19 Feb 2017

@author: zrb13439
'''
from diffcalc.gdasupport.minigda.scannable import ScannableMotionWithScannableFieldsBase


class I21SampleStage(ScannableMotionWithScannableFieldsBase):
    
    def __init__(self, name, pol_scn, tilt_scn, az_scn, xyz_eta_scn):
        
        self.setName(name)
        self._scn_list = [pol_scn, tilt_scn, az_scn]
        self._xyz_eta_scn = xyz_eta_scn
        
        self.setInputNames(['sapol', 'satilt', 'saaz'])  # note, names copied below
        self.setOutputFormat(['%7.5f'] * 3)
        self.completeInstantiation()
    
    def asynchronousMoveTo(self, pos_triple):

        if len(pos_triple) != 3:
            raise ValueError(self.getName() + ' device expects three inputs')
        
        # Move pol, tilt & az (None if not to be moved)
        pol, tilt, az = pos_triple         
        xyz_correction_required = False
        if pol is not None:
            self._scn_list[0].asynchronousMoveTo(pol)
        if tilt is not None:
            self._scn_list[1].asynchronousMoveTo(tilt)
            xyz_correction_required = True
        if az is not None:
            self._scn_list[2].asynchronousMoveTo(az)
            xyz_correction_required = True
            
        # Move xyz_eta group if required
        if xyz_correction_required:
            _, tilt, az = self.completePosition(pos_triple)
            print ('{Correcting xyz_eta for '
                   'tilt(chi-90)=%.2f & az(phi)=%.2f}' % (tilt, az)).rjust(79)
               
    def rawGetPosition(self):
        return [scn.getPosition() for scn in self._scn_list]
    
    def getFieldPosition(self, i):
        return self._scn_list[i].getPosition()
    
    def isBusy(self):
        return (any([scn.isBusy() for scn in self._scn_list])
                or self._xyz_eta_scn.isBusy())
    
    def waitWhileBusy(self):
        for scn in self._scn_list:
            scn.waitWhileBusy()
        self._xyz_eta_scn.waitWhileBusy()
        
    def __repr__(self):
        pos = self.getPosition()
        formatted_values = self.formatPositionFields(pos)
        print [self.getName()] + list(formatted_values)
        s = '''%s:
sapol : %s (eta)
satilt : %s (chi-90)
saa : %s (phi)''' 
        return s % ((self.getName(),) + tuple(formatted_values))       


class I21FourAxisHintGenerator:
    def __init__(self, adapter_list):
        self._adapter_list = adapter_list        
    def __call__(self):
        return [a.get_hint() for a in self._adapter_list]