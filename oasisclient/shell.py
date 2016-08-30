
import argparse
import sys
import logging
from oslo_utils import encodeutils
from oslo_utils import importutils
import six
from oasisclient import version
from oasisclient import v1 as shell_v1
from oasisclient.common import utils
from oasisclient.common.apiclient import exceptions
from oasisclient.common.apiclient.exceptions import *
from oasisclient import exceptions as exc
from oasisclient.v1 import client as client_v1
from oasisclient.i18n import _

DEFAULT_API_VERSION = '1'
DEFAULT_INTERFACE = 'public'
DEFAULT_SERVICE_TYPE = 'container-infra'

logger = logging.getLogger(__name__)

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
        parser = argparse.ArgumentParser(
            prog='oasis',
            description=-None,
            epilog='Type "selin help <COMMAND>" for help on a specific' 'command.',
            add_help=False,
            formatter_class=HelpFormatter
        )
        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=version.version_info.version_string())
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


    def main(self, argv):

        # NOTE(Christoph Jansen): With Python 3.4 argv somehow becomes a Map.
        #                         This hack fixes it.
        argv = list(argv)

        # Parse args once to find version and debug settings
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.setup_debugging(options.debug)

        # NOTE(dtroyer): Hackery to handle --endpoint_type due to argparse
        #                thinking usage-list --end is ambiguous; but it
        #                works fine with only --endpoint-type present
        #                Go figure.
        if '--endpoint_type' in argv:
            spot = argv.index('--endpoint_type')
            argv[spot] = '--endpoint-type'

        subcommand_parser = (
            self.get_subcommand_parser(options.magnum_api_version)
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

        if not utils.isunauthenticated(args.func):
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
            }[options.magnum_api_version]
        except KeyError:
            client = client_v1


def main():
    try:
        OasisShell().main(map(encodeutils.safe_decode, sys.argv[1:]))

    except Exception as e:
        logger.debug(e, exc_info=1)
        print("ERROR: %s" % encodeutils.safe_encode(six.text_type(e)))
        sys.exit(1)

if __name__ == "__main__":
    main()