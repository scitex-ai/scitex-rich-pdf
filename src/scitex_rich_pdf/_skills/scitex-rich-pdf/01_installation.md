---
description: |
  [TOPIC] Install Rich PDF
  [DETAILS] Locate the wheel's npm assets.
tags: [scitex-rich-pdf-installation]
---

# Installation

Install the published wheel with `pip install scitex-rich-pdf`. Use the
directory printed by the following command as an npm file dependency.

```sh
python -c 'from scitex_rich_pdf import get_frontend_package_dir; print(get_frontend_package_dir())'
```

The browser package uses a compatible `@scitex/sdk` version from the host.
