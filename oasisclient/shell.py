
import argparse
import sys
import logging
from oslo_utils import encodeutils
from oslo_utils import importutils
import six
from oasisclient import version
from oasisclient.v1 import shell as shell_v1
from oasisclient.common import cliutils
from oasisclient.common.apiclient import exceptions
from oasisclient.common.apiclient.exceptions import *
from oasisclient import exceptions as exc
from oasisclient.v1 import client as client_v1
from oasisclient.i18n import _

DEFAULT_API_VERSION = '1'
DEFAULT_INTERFACE = 'public'
DEFAULT_SERVICE_TYPE = 'container-infra'

logger = logging.getLogger(__name__)

class OasisClientArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(OasisClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        # FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                     " for more information.\n" %
                     {'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})

class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)

class OasisShell(object):
    def _setup_logging(selfself, debug):
        log_lvl = logging.DEBUG if debug else logging.WARNING
        logging.basicConfig(format="%(levelname)s (%(module)s) %(message)s",
                            level=log_lvl)
        logging.getLogger('iso8601').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    def get_base_parser(self):
        parser = OasisClientArgumentParser(
            prog='oasis',
            description=None,
            epilog='See "oasis help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
        )
        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=version.version_info.version_string())

        parser.add_argument('--oasis-api-version',
                            metavar='<oasis-api-ver>',
                            default=cliutils.env(
                                'OASIS_API_VERSION',
                                default=DEFAULT_API_VERSION),
                            help='Accepts "api", '
                                 'defaults to env[OASIS_API_VERSION].')
        parser.add_argument('--oasis_api_version',
                            help=argparse.SUPPRESS)


        parser.add_argument('--os-auth-url',
                            metavar='<auth-auth-url>',
                            default=cliutils.env('OS_AUTH_URL', default=None),
                            help='Defaults to env[OS_AUTH_URL].')

        parser.add_argument('--os-user-id',
                            metavar='<auth-user-id>',
                            default=cliutils.env('OS_USER_ID', default=None),
                            help='Defaults to env[OS_USER_ID].')

        parser.add_argument('--os-username',
                            metavar='<auth-username>',
                            default=cliutils.env('OS_USERNAME', default=None),
                            help='Defaults to env[OS_USERNAME].')

        parser.add_argument('--os-user-domain-id',
                            metavar='<auth-user-domain-id>',
                            default=cliutils.env('OS_USER_DOMAIN_ID',
                                                 default=None),
                            help='Defaults to env[OS_USER_DOMAIN_ID].')

        parser.add_argument('--os-user-domain-name',
                            metavar='<auth-user-domain-name>',
                            default=cliutils.env('OS_USER_DOMAIN_NAME',
                                                 default=None),
                            help='Defaults to env[OS_USER_DOMAIN_NAME].')

        parser.add_argument('--os-project-id',
                            metavar='<auth-project-id>',
                            default=cliutils.env('OS_PROJECT_ID',
                                                 default=None),
                            help='Defaults to env[OS_PROJECT_ID].')

        parser.add_argument('--os-project-name',
                            metavar='<auth-project-name>',
                            default=cliutils.env('OS_PROJECT_NAME',
                                                 default=None),
                            help='Defaults to env[OS_PROJECT_NAME].')

        parser.add_argument('--os-tenant-id',
                            metavar='<auth-tenant-id>',
                            default=cliutils.env('OS_TENANT_ID',
                                                 default=None),
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-tenant-name',
                            metavar='<auth-tenant-name>',
                            default=cliutils.env('OS_TENANT_NAME',
                                                 default=None),
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-project-domain-id',
                            metavar='<auth-project-domain-id>',
                            default=cliutils.env('OS_PROJECT_DOMAIN_ID',
                                                 default=None),
                            help='Defaults to env[OS_PROJECT_DOMAIN_ID].')

        parser.add_argument('--os-project-domain-name',
                            metavar='<auth-project-domain-name>',
                            default=cliutils.env('OS_PROJECT_DOMAIN_NAME',
                                                 default=None),
                            help='Defaults to env[OS_PROJECT_DOMAIN_NAME].')

        parser.add_argument('--os-token',
                            metavar='<auth-token>',
                            default=cliutils.env('OS_TOKEN', default=None),
                            help='Defaults to env[OS_TOKEN].')

        parser.add_argument('--os-password',
                            metavar='<auth-password>',
                            default=cliutils.env('OS_PASSWORD',
                                                 default=None),
                            help='Defaults to env[OS_PASSWORD].')

        parser.add_argument('--service-type',
                            metavar='<service-type>',
                            help='Defaults to container-infra for all '
                                 'actions.')
        parser.add_argument('--service_type',
                            help=argparse.SUPPRESS)

        parser.add_argument('--endpoint-type',
                            metavar='<endpoint-type>',
                            default=cliutils.env('OS_ENDPOINT_TYPE',
                                                 default=None),
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-endpoint-type',
                            metavar='<os-endpoint-type>',
                            default=cliutils.env('OS_ENDPOINT_TYPE',
                                                 default=None),
                            help='Defaults to env[OS_ENDPOINT_TYPE]')

        parser.add_argument('--os-interface',
                            metavar='<os-interface>',
                            default=cliutils.env(
                                'OS_INTERFACE',
                                default=DEFAULT_INTERFACE),
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-cloud',
                            metavar='<auth-cloud>',
                            default=cliutils.env('OS_CLOUD', default=None),
                            help='Defaults to env[OS_CLOUD].')

        parser.add_argument('--bypass-url',
                            metavar='<bypass-url>',
                            default=cliutils.env('BYPASS_URL', default=None),
                            dest='bypass_url',
                            help=argparse.SUPPRESS)
        parser.add_argument('--bypass_url',
                            help=argparse.SUPPRESS)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = (
            subparsers.add_parser('bash_completion',
                                  add_help=False,
                                  formatter_class=OpenStackHelpFormatter)
        )
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        try:
            actions_modules = {
                '1': shell_v1.COMMAND_MODULES,
            }[version]
        except KeyError:
            actions_modules = shell_v1.COMMAND_MODULES

        for actions_module in actions_modules:
            self._find_actions(subparsers, actions_module)
        self._find_actions(subparsers, self)

        self._add_bash_completion_subparser(subparsers)

        return parser

    def setup_debugging(self, debug):
        if debug:
            streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
            # Set up the root logger to debug so that the submodules can
            # print debug messages
            logging.basicConfig(level=logging.DEBUG,
                                format=streamformat)
        else:
            streamformat = "%(levelname)s %(message)s"
            logging.basicConfig(level=logging.CRITICAL,
                                format=streamformat)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hyphen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            action_help = desc.strip()
            arguments = getattr(callback, 'arguments', [])

            subparser = (
                subparsers.add_parser(command,
                                      help=action_help,
                                      description=desc,
                                      add_help=False,
                                      formatter_class=OpenStackHelpFormatter)
            )
            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS,)
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def main(self, argv):

        # NOTE(Christoph Jansen): With Python 3.4 argv somehow becomes a Map.
        #                         This hack fixes it.
        argv = list(argv)

        # Parse args once to find version and debug settings
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        # self.setup_debugging(options.debug)

        # NOTE(dtroyer): Hackery to handle --endpoint_type due to argparse
        #                thinking usage-list --end is ambiguous; but it
        #                works fine with only --endpoint-type present
        #                Go figure.
        if '--endpoint_type' in argv:
            spot = argv.index('--endpoint_type')
            argv[spot] = '--endpoint-type'

        subcommand_parser = (
            self.get_subcommand_parser(options.oasis_api_version)
        )
        self.parser = subcommand_parser

        if options.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with help right away.
        # NOTE(jamespage): args.func is not guaranteed with python >= 3.4
        if not hasattr(args, 'func') or args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        if not args.service_type:
            args.service_type = DEFAULT_SERVICE_TYPE

        if args.bypass_url:
            args.os_endpoint_override = args.bypass_url

        args.os_project_id = (args.os_project_id or args.os_tenant_id)
        args.os_project_name = (args.os_project_name or args.os_tenant_name)

        if not cliutils.isunauthenticated(args.func):
            if (not (args.os_token and
                     (args.os_auth_url or args.os_endpoint_override)) and
                not args.os_cloud
                ):

                if not (args.os_username or args.os_user_id):
                    raise exc.CommandError(
                        "You must provide a username via either --os-username "
                        "or via env[OS_USERNAME]"
                    )
                if not args.os_password:
                    raise exc.CommandError(
                        "You must provide a password via either "
                        "--os-password, env[OS_PASSWORD], or prompted "
                        "response"
                    )
                if (not args.os_project_name and not args.os_project_id):
                    raise exc.CommandError(
                        "You must provide a project name or project id via "
                        "--os-project-name, --os-project-id, "
                        "env[OS_PROJECT_NAME] or env[OS_PROJECT_ID]"
                    )
                if not args.os_auth_url:
                    raise exc.CommandError(
                        "You must provide an auth url via either "
                        "--os-auth-url or via env[OS_AUTH_URL]"
                    )
        try:
            client = {
                '1': client_v1,
            }[options.oasis_api_version]
        except KeyError:
            client = client_v1

        # print args

        self.cs = client.Client(
            cloud=args.os_cloud,
            user_id=args.os_user_id,
            username=args.os_username,
            password=args.os_password,
            auth_token=args.os_token,
            project_id=args.os_project_id,
            project_name=args.os_project_name,
            user_domain_id=args.os_user_domain_id,
            user_domain_name=args.os_user_domain_name,
            project_domain_id=args.os_project_domain_id,
            project_domain_name=args.os_project_domain_name,
            auth_url=args.os_auth_url,
            service_type=args.service_type,
            # region_name=args.os_region_name,
            # oasis_url=args.os_endpoint_override,
            # interface=args.os_interface,
            # insecure=args.insecure,
        )

        args.func(self.cs, args)

    def do_bash_completion(self, _args):
        """Prints arguments for bash-completion.

        Prints all of the commands and options to stdout so that the
        oasis.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @cliutils.arg('command', metavar='<subcommand>', nargs='?',
                  help='Display help for <subcommand>.')
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        # NOTE(jamespage): args.command is not guaranteed with python >= 3.4
        command = getattr(args, 'command', '')

        if command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


# I'm picky about my shell help.
class OpenStackHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


def main():
    # from oasis.cmd import api
    # api.main()
   # try:
    OasisShell().main(map(encodeutils.safe_decode, sys.argv[1:]))

   # except Exception as e:
   #     logger.debug(e, exc_info=1)
   #     print("ERROR: %s" % encodeutils.safe_encode(six.text_type(e)))
   #     sys.exit(1)

if __name__ == "__main__":

    main()