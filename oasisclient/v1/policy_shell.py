from oasisclient.common import cliutils


@cliutils.arg('--policy',
           metavar='<policy>',
           help='VM policy to create.')
def do_policy_delete(cs, args):
    """Create a function."""
    pass



def do_policy_list(cs, args):
    """Print a list of policy."""
    pass

@cliutils.arg('policy',
           metavar='<policy>',
           nargs='+',
           help='ID or name of the (policy)s to delete.')
def do_policy_delete(cs, args):
    """Delete specified policy."""
    pass

