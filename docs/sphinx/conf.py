"""Sphinx settings for the Rich PDF package documentation."""

from importlib.metadata import version as distribution_version

project = "SciTeX Rich PDF"
author = "Yusuke Watanabe"
release = distribution_version("scitex-rich-pdf")
extensions = ["myst_parser", "sphinx.ext.autodoc"]
exclude_patterns = ["_build"]
html_theme = "sphinx_rtd_theme"
