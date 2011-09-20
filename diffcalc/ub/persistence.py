
class UBCalculationPersister(object):
    """Attempts to the use the gda's database to store ub calculation state
    """
    def __init__(self):
        try:
            from gda.util.persistence import LocalJythonShelfManager
            from gda.util.persistence.LocalDatabase import LocalDatabaseException
            self.shelf = LocalJythonShelfManager.getLocalObjectShelf('diffcalc.ub')
        except ImportError, e:
            print "UBCalculationPersister could not import the gda database code: " + `e`
            self.shelf = None
        except LocalDatabaseException, e:
            print "UBCalculationPersister could not connect to the gda database: " + `e`
            self.shelf = None

    def save(self, state, key):
        if self.shelf is not None:
            self.shelf[key] = state
        else:
            print " no database available to save UB calculation"
        
    def load(self, name):
        if self.shelf is not None:
            return self.shelf[name]
        raise IOError("Could not load UB calculation: no database available")
    
    def list(self):
        if self.shelf is not None:
            names = list(self.shelf.keys())
            names.sort()
            return names
        else:
            return []
    
    def remove(self, name):
        if self.shelf is not None:
            del self.shelf[name]
        raise IOError("Could not remove UB calculation: no database available")
       
       
class UbCalculationNonPersister(UBCalculationPersister):
    """A version of UBCalculationPersister that simply stores to a local dict rather than a database.
    Useful for testing.
    """
    def __init__(self):
        self.shelf = dict()
