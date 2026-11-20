---
description: |
  [TOPIC] Mount a viewer
  [DETAILS] Connect the SDK renderer, PDF regions, and feed.
tags: [scitex-rich-pdf-quick-start]
---

# Quick start

Import `createRichPdfViewer` from `@scitex/rich-pdf` and supply the SDK
renderer, a container, and `ports.documents.resolve`. Add `feedContainer`
and `ports.feed.list` to show feed entries. Use `overlayId` to link an
entry to a named PDF region. Call `load` with a document key and
`destroy` when the host removes the viewer.
