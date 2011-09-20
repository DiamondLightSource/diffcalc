"""
Based on: Elias Vlieg, "A (2+3)-Type Surface Diffractometer: Mergence of the z-axis
and (2+2)-Type Geometries", J. Appl. Cryst. (1998). 31. 198-203    
"""

from diffcalc.gdasupport.scannable.slave.SlaveScannableDriver import SlaveScannableDriver
from math import  pi, tan, sin, atan

TORAD=pi/180
TODEG=180/pi

class NuDriverForSixCirclePlugin(SlaveScannableDriver):

    def slaveFromTriggerPos(self, triggerPos):
        
        alpha,delta,gamma,_, _, _ = triggerPos
        alpha = alpha*TORAD
        delta = delta*TORAD
        gamma = gamma*TORAD
        
        ### Equation16 RHS ###
        rhs = -1 * tan(gamma - alpha) * sin(delta)
        nu = atan(rhs) # -pi/2 <= nu <= pi/2
        return nu*TODEG