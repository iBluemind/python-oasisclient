from oasisclient.common import cliutils as utils
from oasisclient.common import utils as magnum_utils
from oasisclient import exceptions
from oasisclient.i18n import _

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
import os


@utils.arg('--name',
           metavar='<function>',
           help='Name of the baymodel to create.')
def do_function_list(cs, args):
    """Print a list of functions."""
    functions = cs.function.list()

    columns = ['name', 'user_id', 'project_id']
    columns += utils._get_list_table_columns_and_formatters(
        args.fields, functions,
        exclude_fields=(c.lower() for c in columns))[0]
    # utils.print_list(functions, columns,
    #                  {'versions': magnum_utils.print_list_field('versions')},
    #                  sortby_index=None)

@utils.arg('function',
           metavar='<function>',
           nargs='+',
           help='ID or name of the (function)s to delete.')
def do_function_delete(cs, args):
    """Delete specified function."""
    pass

def do_function_test(cs, args):
    """API Connect Test."""
    cs.function.test()