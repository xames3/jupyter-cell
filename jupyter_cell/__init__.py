"""\
Jupyter Notebook → reStructuredText Cells
=========================================

Author: Akshay Mestry <xa@mes3.dev>
Created on: Sunday, September 15 2024
Last updated on: Sunday, September 15 2024

This module converts a Jupyter notebook into reStructuredText (rST)
format and splits it into smaller snippet files. Each snippet contains
either a code cell or a combination of a code cell with its
corresponding output. This allows you to embed specific cells and outputs
in Sphinx documentation with better control.
"""

from __future__ import annotations

import argparse
import logging
import os
import typing as t

import nbconvert
import nbformat

name: t.Final[str] = "jupyter-cell"
version: str = "2024.09.15"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


class JupyterToCell:
    """Class to handle the conversion of Jupyter notebooks into `.rst`
    reStructuredText (rST) format and splitting the converted `.rst` file
    into smaller snippets.

    The class provides methods to:

        - Convert a notebook from `.ipynb` to `.rst`.
        - Split the rST file into smaller, cell-based snippets.

    :var usage: A usage message for the command-line interface.
    :var description: A brief description of the command for the CLI.
    :var help: Help text for the command's options and arguments.
    """

    usage: str = (
        "%(prog)s [options] --notebook <path> --keep ...\n "
        "%(prog)s [options] --notebook <path> ..."
    )
    description: str = (
        "Converts a Jupyter notebook into an reStructuredText (rST) file, "
        "then splits the reStructuredText (rST) file into smaller snippets, "
        "each representing a cell or a code-output pair."
    )
    help: str = (
        "A utility to convert Jupyter notebooks into reStructuredText (rST) "
        "and split them into smaller files."
    )

    def convert(self, notebook: str) -> None:
        """Convert Jupyter notebook file from `.ipynb` to `.rst`.

        :param notebook: The path to the Jupyter notebook file (.ipynb)
            to be converted.
        :raises FileNotFoundError: If the specified notebook file does not
            exist.
        """
        try:
            self.rst = notebook.replace(".ipynb", ".rst")
            self.file = os.path.basename(self.rst)
            with open(notebook) as fp:
                nb = nbformat.read(fp, as_version=4)  # type: ignore
            with open(self.rst, "w") as rst:
                rst.write(
                    nbconvert.RSTExporter().from_notebook_node(nb)[0]  # type: ignore
                )
            logging.info(
                f"Successfully converted {self.file!r} to reStructuredText"
            )
        except FileNotFoundError:
            logging.error(f"Notebook {self.file!r} not found")
            raise
        except Exception as exc:
            logging.error(f"Failed to convert {self.file!r}: {exc}")
            raise

    def split(self, keep: bool = False, prefix: str = "cell-") -> None:
        """Splits the converted reStructuredText (rST) file into multiple
        smaller reStructuredText (rST) files, each representing either a
        code cell or a code-output pair from the original notebook.

        :param keep: If `True`, keeps the original reStructuredText
            (rST) file after splitting, else deletes the original
            reStructuredText (rST) file after splitting (default: False).
        :param prefix: The prefix for the output snippet files. Each file is
            named as `<prefix><cell_number>.rst`, defaults to `cell-`.
        """
        if not os.path.exists(self.rst):
            logging.error(
                "No reStructuredText (rST) file found. Please convert a "
                "notebook first"
            )
            return
        try:
            with open(self.rst) as rst:
                contents = rst.readlines()
            cell: int = 1
            current: list[str] = []
            self.path = os.path.splitext(self.rst)[0]
            os.makedirs(self.path, exist_ok=True)
            for content in contents:
                if content.startswith(".. code:: ipython3"):
                    if current:
                        self.export(cell, current, prefix)
                        cell += 1
                        current = []
                current.append(content)
            if current:
                self.export(cell, current, prefix)
            if not keep:
                os.remove(self.rst)
        except Exception as exc:
            logging.error(
                f"Failed to split reStructuredText (rST) file {self.file}: "
                f"{exc}"
            )
            raise

    def export(self, cell: int, content: list[str], prefix: str) -> None:
        """Writes a snippet (representing a code cell and optionally its
        output) to a new reStructuredText (rST) file.

        :param cell: The current cell number being processed.
        :param content: The content of the code cell and its output, as
            a list of strings.
        :param prefix: The prefix to be used in the snippet file name.
        :raises IOError: If there is an issue with writing the
            reStructuredText (rST) file.
        """
        _ = os.path.join(self.path, f"{prefix}{cell}.rst")
        try:
            with open(_, "w") as rst:
                rst.write(
                    "".join(content).replace("\n" * 4, "\n").rstrip() + "\n"
                )
        except IOError as err:
            logging.error(f"Error writing to {_}: {err}")
            raise

    def process(
        self, notebook: str, keep: bool = False, prefix: str = "cell-"
    ) -> None:
        """Process the complete conversion and splitting.

        :param notebook: The path to the Jupyter notebook file (.ipynb)
            to be converted.
        :param keep: If `True`, keeps the original reStructuredText
            (rST) file after splitting, else deletes the original
            reStructuredText (rST) file after splitting (default: False).
        :param prefix: The prefix for the output snippet files. Each file is
            named as `<prefix><cell_number>.rst`, defaults to `cell-`.
        """
        self.convert(notebook)
        self.split(keep, prefix)

    @classmethod
    def add_options(
        cls, parser: argparse.ArgumentParser | argparse._ActionsContainer
    ) -> None:
        """Adds command-line options to the argparse parser.

        These options allow the user to specify the notebook file, the
        prefix for output snippet files, and whether to keep the original
        reStructuredText (rST) file after splitting.

        :param parser: The argument parser to which options will be
            added.
        """
        options = parser.add_argument_group("Converting Options")
        options.add_argument(
            "-n",
            "--notebook",
            help=(
                "The path to the Jupyter notebook file (.ipynb) to be "
                "converted into reStructuredText (.rst) format and split."
            ),
            required=True,
            metavar="<path>",
        )
        options.add_argument(
            "--prefix",
            default="cell-",
            help=(
                "A custom prefix for the output snippet files. "
                "(Default: %(default)s)."
            ),
            metavar="<prefix>",
        )
        options.add_argument(
            "--keep",
            action="store_true",
            default=False,
            help=(
                "If set, the original reStructuredText (.rst) file will be "
                "kept after splitting. (Default: %(default)s)."
            ),
        )
