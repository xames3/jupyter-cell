.. Author: Akshay Mestry <xa@mes3.dev>
.. Created on: Sunday, September 15 2024
.. Last updated on: Sunday, September 15 2024

===============================================================================
Jupyter Notebook → reStructuredText Cells
===============================================================================

A Python utility for converting Jupyter notebooks into reStructuredText cells
and splitting them into smaller snippets.

-------------------------------------------------------------------------------
What is JupyterCell?
-------------------------------------------------------------------------------

JupyterCell is an open-source tool designed to simplify the process of
embedding Jupyter Notebook cells into Sphinx websites. With JupyterCell, you
can convert your entire notebook into reStructuredText (rST) and automatically
split the converted content into smaller, manageable snippets-each containing
code cells and their outputs.

This project is built for educators, researchers, and developers who need a
more flexible way to include specific code snippets from notebooks in their
documentation projects. JupyterCell handles the tedious work of converting
and splitting, so you can focus on creating insightful content for your
audience.

-------------------------------------------------------------------------------
Getting Started
-------------------------------------------------------------------------------

Prerequisites
===============================================================================

- Python 3.11+
- Jupyter Notebook or Jupyter Lab
- Sphinx (for rST-based documentation)
- Optional: virtual environment (recommended)

To get started with JupyterCell, you'll need to have Python and the required
dependencies installed. Here's how you can set things up:

Installation
===============================================================================

.. code-block:: bash

    python3 -m venv env
    source env/bin/activate    # On Windows, use `env\Scripts\activate`

Now, install the package directly from PyPI:

.. code-block:: bash

    pip install jupyter-cell

-------------------------------------------------------------------------------
Usage
-------------------------------------------------------------------------------

You can use JupyterCell from the command line with the following syntax:

.. code-block:: bash

    jupyter-cell --notebook path/to/notebook.ipynb [--prefix <prefix>] [--keep]

- --notebook (-n) **[Required]**: The path to the Jupyter notebook you want to
  convert.
- --prefix **[Optional]**: Prefix for the generated snippet files (Default:
  `cell-`).
- --keep **[Optional]**: Whether to keep the full RST file after splitting
  into snippets (Default: `False`).

-------------------------------------------------------------------------------
Example
-------------------------------------------------------------------------------

Suppose you have a Jupyter Notebook called `some_notebook.ipynb` in your
current directory. To convert and split it into smaller rST snippets, run the
following command:

.. code-block:: bash

    jupyter-cell --notebook some_notebook.ipynb --prefix snippet- --keep

This will produce:

- A full `some_notebook.rst` file.
- Several smaller files, each named snippet-1.rst, snippet-2.rst, etc.,
  containing individual cells or cell/output pairs.

The `--keep` flag ensures that the original `some_notebook.rst` is preserved.

-------------------------------------------------------------------------------
Contributions
-------------------------------------------------------------------------------

Contributions and/or suggestions are welcome! If you find a bug, have a
feature request, or want to contribute improvements, please open an issue or
submit a pull request on GitHub.

-------------------------------------------------------------------------------
License
-------------------------------------------------------------------------------

JupyterCell is licensed under the MIT License. See the `LICENSE`_ file for
more details.

.. _LICENSE: https://github.com/xames3/jupyter-cell/blob/main/LICENSE
