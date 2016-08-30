from oasisclient.common import utils


@utils.arg('--name',
           metavar='<function>',
           help='Name of the baymodel to create.')
def do_function_delete(cs, args):
    """Create a baymodel."""
    pass



def do_function_list(cs, args):
    """Print a list of available bays."""
    pass

@utils.arg('function',
           metavar='<function>',
           nargs='+',
           help='ID or name of the (function)s to delete.')
def do_function_delete(cs, args):
    """Delete specified baymodel."""
    pass

