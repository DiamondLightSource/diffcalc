print 1
if True:
    try:
        import not_there
    except ImportError:
        msg = """Error importing numpy: you should not try to import numpy from
        its source directory; please exit the numpy source tree, and relaunch
        your python intepreter from there."""
        raise ImportError(msg)