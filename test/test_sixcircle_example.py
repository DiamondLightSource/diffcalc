'''
Created on 8 May 2013

@author: zrb13439
'''

import os
import sys
print sys.path

diffcalc_path = os.path.split(os.path.split(__file__)[0])[0]
STARTUP_PATH = os.path.join(diffcalc_path, 'example')
print "prepended to path:", STARTUP_PATH
sys.path.insert(0, STARTUP_PATH)

from sixcircle import *

ct.pause = False  # @UndefinedVariable
class test_sixcircle_example():

    def test_execfile(self):
        pass
        # the import above will test this

    def test_demo_all_and_scan(self):
        demo_all()  # @UndefinedVariable
        demo_scan()  # @UndefinedVariable