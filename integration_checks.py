'''
Created on 9 Mar 2017

@author: zrb13439

'''

'''
Integration tests for startup scripts (named so that nosetests will *not* pick
up by default.

This is because these must be run with:

    $ nosetests --with-process-isolation integration_checks.py

This is not a standard nose option. Install it with:

    $ pip install nosepipe

nosepipe is described at https://github.com/dmccombs/nosepipe/
'''

from nose import SkipTest


def test_sixcircle_startup():
    import startup.sixcircle
    startup.sixcircle.ct.pause = False
    startup.sixcircle.demo.all()


def test_fivecircle_startup():
    import startup.fivecircle
    startup.fivecircle.ct.pause = False
    startup.fivecircle.demo.all()


def test_fourcircle_startup():
    import startup.fourcircle
    startup.fourcircle.ct.pause = False
    startup.fourcircle.demo.all()


def test_i13_startup():
    raise SkipTest('Still need to work out to use i13s very tight limits')
    import startup.i13
    startup.i13.ct.pause = False
    startup.i13.demo.all()


def test_i16_startup():
    import startup.i16
    startup.i16.ct.pause = False
    startup.i16.demo.all()


def test_i21_startup_standard():
    import startup.i21
    startup.i21.ct.pause = False
    startup.i21.demo.all()


def test_i21_startup_bespoke():
    import startup.i21
    startup.i21.ct.pause = False
    startup.i21.demo.i21()
    
    
def test_sixcirle_api():
    import startup.api.sixcircle
    startup.api.sixcircle.demo_all()

