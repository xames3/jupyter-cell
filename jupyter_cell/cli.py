"""\
Jupyter Notebook → reStructuredText Cells CLI
=============================================

Author: Akshay Mestry <xa@mes3.dev>
Created on: Sunday, September 15 2024
Last updated on: Sunday, September 15 2024

...
"""

from __future__ import annotations

import argparse
import shutil
import sys
import textwrap
import typing as t

from . import JupyterToCell
from . import name
from . import version

F = t.TypeVar("F", bound=argparse.ArgumentParser)

# Maximum terminal width which allows hard-wrapping of the command line
# messages and descriptions over a set length. By default, the total
# command line width is used for the messages but for the smaller
# terminal widths, it automatically soft-wraps the messages.
width: int = shutil.get_terminal_size().columns - 2
width = width if width <= 80 else 80


class JupyterToCellArgumentFormatter(argparse.RawTextHelpFormatter):
    """Custom formatter for customizing command layout, usage message
    and wrapping lines.

    This class overrides the default behavior and adds custom usage
    message template. Also it sets a soft limit for wrapping the help
    and description strings.

    .. note::

        Be warned, by accessing names starting with an underscore you
        are venturing into the undocumented private API of the module,
        and your code may break in future updates.

    :param prog: Program name which acts as an entrypoint.
    :param indent_increment: Default indentation for the following
        command line text, defaults to `2`.
    :param max_help_position: Distance between command line arguments
        and its description, defaults to `50`. This default value of 50
        is forced to use instead of 24.
    :param width: Maximum width of the command line messages, defaults
        to `None`.
    """

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 50,
        width: int | None = None,
    ) -> None:
        """Update the `max_help_position` to accomodate metavar."""
        super().__init__(prog, indent_increment, max_help_position, width)

    # See https://stackoverflow.com/a/35848313/14316408 for customizing
    # the usage section when looking for help.
    def add_usage(
        self,
        usage: str | None,
        actions: t.Iterable[argparse.Action],
        groups: t.Iterable[argparse._ArgumentGroup],
        prefix: str | None = None,
    ) -> None:
        """Capitalize the usage text."""
        if prefix is None:
            sys.stdout.write("\n")
            prefix = "Usage:\n "
        return super().add_usage(
            usage, actions, groups, prefix  # type: ignore[arg-type]
        )

    # See https://stackoverflow.com/a/35925919/14316408 for adding the
    # line wrapping logic for the description.
    def _split_lines(self, text: str, _: int) -> list[str]:
        """Unwrap the lines to width of the terminal."""
        text = self._whitespace_matcher.sub(" ", text).strip()
        return textwrap.wrap(text, width)

    # See https://stackoverflow.com/a/13429281/14316408 for hiding the
    # metavar is subcommand listing.
    def _format_action(self, action: argparse.Action) -> str:
        """Hide Metavar in command listing."""
        parts = super()._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.splitlines()[1:])
        return parts

    # See https://stackoverflow.com/a/23941599/14316408 for disabling
    # the metavar for short options.
    def _format_action_invocation(self, action: argparse.Action) -> str:
        """Disable Metavar for short options."""
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        parts: list[str] = []
        if action.nargs == 0:
            parts.extend(action.option_strings)
        else:
            default = action.dest.upper()
            args_string = self._format_args(action, default)
            for option_string in action.option_strings:
                parts.append(f"{option_string}")
            parts[-1] += f" {args_string}"
        return ", ".join(parts)


class TextWrapper(textwrap.TextWrapper):
    """Custom text wrapper to fix the linebreaks in the long texts."""

    # See https://stackoverflow.com/a/45287550/14316408 for help on
    # textwrapping.
    def wrap(self, text: str) -> list[str]:
        """Reformat text wrapping."""
        return [
            line
            for paragraph in text.split("\n")
            for line in textwrap.TextWrapper.wrap(self, paragraph)
        ]


wrapper = TextWrapper(width=width)


def add_general_options(
    parser: argparse.ArgumentParser | argparse._ActionsContainer,
) -> None:
    """Add general options to the parser object.

    :param parser: Parser instance to which the general options are
        supposed to be added to.
    """
    options = parser.add_argument_group("General Options")
    options.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message.",
    )
    options.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help=wrapper.fill("Increase the logging verbosity."),
    )
    # See https://stackoverflow.com/a/8521644/812183 for adding version
    # specific argument to the parser.
    options.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"JupyterToCell v{version}",
        help="Show JupyterToCell's installed version and exit.",
    )


def subcommand(
    instance: JupyterToCell,
    subparsers: argparse._SubParsersAction[F],
    parents: argparse.ArgumentParser,
    command: str,
    callback: F,
) -> None:
    r"""Create subparser or positional argument object.

    This function creates new subcommands in the main argument parser
    instance.

    :param instance: JupyterToCell instance.
    :param subparsers: Subparser instance action which we are going to
        attach to.
    :param parents: Parent argument parser instance. Usually this is
        nothing but another parser instance. Parent parsers, needed to
        ensure tree structure in argparse.
    :param command: Subcommand instruction.
    :param callback: Subcommand callback action.
    """
    parser = subparsers.add_parser(
        command,
        parents=[parents],  # type: ignore[list-item]
        usage=wrapper.fill(instance.usage),
        description=wrapper.fill(instance.description),
        help=wrapper.fill(instance.help),
        add_help=False,
        formatter_class=JupyterToCellArgumentFormatter,
        conflict_handler="resolve",
    )
    instance.add_options(parser)
    parser.set_defaults(callback=callback)


def create_main_parser(instance: JupyterToCell) -> argparse.ArgumentParser:
    """Create and return the main parser object for JupyterToCell's CLI.

    It powers the main argument parser for the JupyterToCell module.

    :param app: JupyterToCell instance.
    :return: ArgumentParser object which stores all the properties of
        the main argument parser.
    """
    parent_parser = argparse.ArgumentParser(
        prog=name,
        usage="%(prog)s <command> [options]",
        formatter_class=JupyterToCellArgumentFormatter,
        conflict_handler="resolve",
        add_help=False,
        description=wrapper.fill(
            "Convert Jupyter notebook to reStructuredText (rST) and split "
            "it into cell snippets."
        ),
        epilog=wrapper.fill(
            'For information about a particular command, run "'
            'jupyter-cell <command> --help". Read complete documentation at: '
            "https://github.com/xames3/jupyter-cell.",
        ),
    )
    parent_parser._positionals.title = "Commands"
    child_parser = argparse.ArgumentParser(add_help=False)
    for parser in (parent_parser, child_parser):
        add_general_options(parser)
    subparsers = parent_parser.add_subparsers(prog=name)
    commands = {"convert": instance.process}
    for command, callback in commands.items():
        subcommand(
            instance, subparsers, child_parser, command, callback
        )  # type: ignore[misc]
    return parent_parser


def main() -> int:
    """..."""
    jupyter = JupyterToCell()
    parser = create_main_parser(jupyter)
    args = parser.parse_args()
    if hasattr(args, "callback"):
        try:
            args.callback(args.notebook, args.keep, args.prefix)
        except UnboundLocalError:
            print("No arguments passed to the command")
            return 1
    else:
        parser.print_help()
    return 0
