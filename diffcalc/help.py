from diffcalc.utils import DiffcalcException
from functools import wraps
import textwrap

RAISE_EXCEPTIONS_FOR_ALL_ERRORS = False
DEBUG = False


class ExternalCommand(object):
    """Instances found in a command_list by format_command_help will
    result in documentation for a command without there actually being one.
    """
    def __init__(self, docstring):
        """Set the docstring that will be pulled off by format_command_help.
        """
        self.__doc__ = docstring


def format_command_help(command_list):
    lines = []
    for obj in command_list:

        if isinstance(obj, basestring):  # group heading
            lines.extend(['', obj.upper(), ''])

        else:  # individual command
            doc_lines = [s.strip() for s in obj.__doc__.split('\n')]
            for doc_line in doc_lines:
                if doc_line == '':
                    continue
                name, args, desc = _split_doc_line(doc_line)
                desc_lines = textwrap.wrap(desc, 45)
                line = ('   ' + name + ' ' + args).ljust(35)
                if len(line) <= 35:
                    line += (desc_lines.pop(0))  # first line
                lines.append(line)
                for desc_line in desc_lines:
                    lines.append(' ' * 35 + desc_line)
#                lines.append('')
    return '\n'.join(lines)


def _split_doc_line(docLine):
    name, _, right = docLine.partition(' ')
    args, _, desc = right.partition('-- ')
    return name, args, desc


def create_command_decorator(command_list):
    """create a command_decorator

    In the process of decorating a function this command_decorator adds
    the command to command_list. Calls to the decorated function (or method)
    are wrapped by call_command.
    """

    def command_decorator(f):
        command_list.append(f)

        @wraps(f)
        def wrapper(*args, **kwds):
            return call_command(f, args)

        return wrapper

    return command_decorator


def call_command(f, args):

    if DEBUG:
        return f(*args)
    try:
        return f(*args)
    except TypeError, e:
        # NOTE: TypeErrors resulting from bugs in the core code will be
        # erroneously caught here!
        if RAISE_EXCEPTIONS_FOR_ALL_ERRORS:
            print "-" * 80
            print f.__doc__
            print "-" * 80
            raise e
        else:
            print 'TypeError : %s' % e.message
            print 'USAGE:'
            print f.__doc__
    except DiffcalcException, e:
        if RAISE_EXCEPTIONS_FOR_ALL_ERRORS:
            raise e
        else:
            print e.args[0]
