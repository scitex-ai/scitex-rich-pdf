---
name: scitex-rich-pdf
description: |
  [WHAT] Embeds a PDF, region overlays, comments, and a synchronized feed in a browser application.
  [WHEN] Use when adding a neutral PDF viewer or connecting host-supplied feed items to PDF regions.
  [HOW] Install scitex-rich-pdf, locate its browser assets through the Python package, and pass the SciTeX SDK renderer to createRichPdfViewer.
tags: [scitex-rich-pdf]
primary_interface: python
interfaces:
  python: 1
  skills: 1
---

# SciTeX Rich PDF

Install `scitex-rich-pdf` from PyPI. The Python function
`scitex_rich_pdf.get_frontend_package_dir()` returns the directory for the
`@scitex/rich-pdf` npm file dependency. Install the matching SDK browser
package and provide its `createPdfViewer` factory.

- Provide document access, overlays, comments, and feed entries through ports.
- Pass a revision-specific document key to `load` whenever the PDF changes.
- Locations use one-based pages and bottom-left PDF coordinates.
- Supply display content and actions through the feed renderer. Keep
  authorization and data persistence in the host.
- Use Live Paper when the viewer needs claim details, evidence graphs, or
  reproduction actions.

The package README contains an embedding example. The included TypeScript
declarations specify the complete viewer contract.

- [Installation](01_installation.md)
- [Quick start](02_quick-start.md)
