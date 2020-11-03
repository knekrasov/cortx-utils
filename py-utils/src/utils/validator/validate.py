#!/bin/env python3

# CORTX-Py-Utils: CORTX Python common library.
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

import sys
import errno
import argparse
import inspect
import traceback

import cortx.utils.validator.commands as commands


class ValidatorCommandFactory:
    """Factory for all kinds of validations."""

    @staticmethod
    def usage(prog):
        """Print usage instructions."""

        usage_string = (f"usage: {prog}\n"
                        "\t[-h]\n"
                        "\t[network connectivity <ip1> <ip2> <...>]\n"
                        "\t[consul service <host> <port>]\n"
                        "\t[elasticsearch service <host> <port>]\n"
                        "\t[bmc accessible <node1> <node2> <...>]\n"
                        "\t[bmc stonith <node> <bmc_ip> <bmc_user> <bmc_passwd>]\n")
        sys.stderr.write(usage_string)

    @staticmethod
    def get_command(description, argv):
        """Return the Command after parsing the command line."""

        parser = argparse.ArgumentParser(description)
        tail = []
        if len(argv) > 2:
            [_, _, *tail] = argv

        subparsers = parser.add_subparsers()
        cmds = inspect.getmembers(commands, inspect.isclass)
        VCommand = commands.VCommand
        for name, cmd in cmds:
            if cmd != VCommand and issubclass(cmd, VCommand):
                instance = cmd(tail)
                instance.add_args(subparsers)
        args = parser.parse_args(argv)
        if not hasattr(args, 'command'):
            return None
        command = args.command
        command.set_parsed_args(args)
        return command


def main(argv):
    try:
        description = "CORTX Validator command"
        prog_name = argv[0]
        command = ValidatorCommandFactory.get_command(description, argv[1:])
        if not command:
            ValidatorCommandFactory.usage(prog_name)
        else:
            command.process()

    except Exception as e:
        sys.stderr.write("error: %s\n\n" % str(e))
        sys.stderr.write("%s\n" % traceback.format_exc())
        ValidatorCommandFactory.usage(prog_name)
        return errno.EINVAL


if __name__ == '__main__':
    sys.exit(main(sys.argv))
