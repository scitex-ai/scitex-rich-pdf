# Contributing to SciTeX Rich PDF

Start a branch from `develop` and target `develop` with your pull request.
The [SciTeX CLA](CLA.md) applies to contributions.

```sh
python -m pip install -e '.[dev,docs]'
python -m playwright install --only-shell chromium
RICH_PDF_BROWSER=1 python -m pytest
sphinx-build -W --keep-going docs/sphinx docs/sphinx/_build/html
```

For viewer changes, include the PDF revision, renderer version, and steps
that demonstrate the behavior. The release workflow publishes qualified tags.
