'''
Created on 8 May 2013

@author: zrb13439
'''

import os
import sys
print sys.path
print 111111
print __file__

diffcalc_path = __file__.split(os.path.sep)[0:-2]
print diffcalc_path

import diffcalc

sixcircle_path = os.path.join(os.path.sep.join(diffcalc_path), 'startup', 'sixcircle.py')
print 'executing: ', sixcircle_path
execfile(sixcircle_path)
ct.pause = False  # @UndefinedVariable
class test_sixcircle_example():

    def test_execfile(self):
        pass
        # the import above will test this

    def test_demo_all_and_scan(self):
        demo_all()  # @UndefinedVariable
        demo_scan()  # @UndefinedVariable