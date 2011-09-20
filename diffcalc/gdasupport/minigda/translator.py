from StringIO import StringIO
from diffcalc.gdasupport.minigda.scannable.scannable import Scannable
from tokenize import *
print "WARNING: minigda.terminal is not well tested"

class TranslatorException(Exception):
    """Thrown by translator if there is a problem with the command to translate"""
    pass

class Translator(object):
    def __init__(self):
        self.aliases = []
        
    def alias(self, name):
        self.aliases.append(name)


class TranslatorAliasedCommandsOnly(Translator):
    
    def translate(self, line):
        # Tokenize
        line = line.strip()
        if line =='':
            return ''
        g = generate_tokens(StringIO(line).readline)
        
        # Process first token
        toknum, val , _, _, _ = g.next()
        if toknum == COMMENT:
            return val
        elif val not in self.aliases:
            raise TranslatorException("'%s' is not an aliased command, Scannable, or comment.\n   (Hint: unlike the gda system, the minigda does not currently support regular Python syntax.)"%val)
        else:
            result = val + '('
        
        # Process the rest
        withinSquareBrackets = False
        while 1:
            toknum, val , _, _, _ = g.next()
###            print tok_name[toknum],": ",val
            if (toknum in (COMMENT, ENDMARKER)):    # End of arguments
                if withinSquareBrackets:
                    raise TranslatorException("No closing square bracket.")
                if result[-1] == ',':                # Remove trailing ','
                    result = result[:-1]
                if toknum == COMMENT:
                    result += ')'
                    result += val
                    break
                elif toknum == ENDMARKER:
                    result += ')'
                    break
            elif val ==  '[':                        # Begining of vector
                withinSquareBrackets = True
                result += val
            elif val ==  ']':                        # End of vector
                withinSquareBrackets = False
                result += val + ','
            elif val in ('(',')'):
                raise TranslatorException("Unexpected '%s' found.\nHint: unlike the gda system, minigda does not currently support regular Python."%val)
            elif toknum==OP and val =='-':            # assume this is preceding a number
                result += val
            elif toknum==OP:                        # Probably a mathematical operator(although brackets are also OPS)
                if result[-1] == ',':                #    remove trailing ','
                    result = result[:-1]
                result += val
            else:
                if withinSquareBrackets:            # Part of vector
                    result += val
                else:
                    result += val + ','                # Argument
        return result
        
if __name__ == '__main__':
    pass