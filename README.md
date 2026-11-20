# SciTeX Rich PDF

Rich PDF is an embeddable PDF viewer with region overlays, comments, and a
synchronized feed. The host supplies document access, feed content, and action
handlers. The SciTeX SDK supplies PDF rendering and coordinate transforms.

## Install

Install the Python distribution and locate its browser assets.

```sh
pip install scitex-rich-pdf
python -c 'import scitex_rich_pdf; print(scitex_rich_pdf.get_frontend_package_dir())'
```

Use the printed directory as an npm file dependency alongside a provider-capable
`@scitex/sdk` installation (0.3.25 or later). Both frontend packages can be
resolved from their Python distributions in the host's build. No npm registry
publication is required.

```js
import { createPdfViewer } from "@scitex/sdk/ui/pdf-viewer";
import { createRichPdfViewer } from "@scitex/rich-pdf";
import "@scitex/rich-pdf/pdf-provider.css";

const viewer = createRichPdfViewer({
  container: pdfElement,
  feedContainer: feedElement,
  createPdfViewer,
  ports: {
    documents: { resolve: resolveDocument },
    overlays: { list: listRegions },
    feed: { list: listEntries, renderEntry: renderEntryDetails },
    events: { emit: handleEvent },
  },
});
await viewer.load(documentKey);
```

The host places the PDF and feed containers in its layout. The feed is optional.
Use a document key that describes the current revision, and call `load` again
when the revision changes. Return a document with `id`, `src`, and optional
`revision` and `readonly` fields.

Regions have an `id`, a one-based `page`, and a bounding box
`[x0, y0, x1, y1]` in bottom-left PDF coordinates. Feed entries have an `id`,
`label`, and optional `overlayId` and `data`. An unanchored entry remains
selectable. Clicking a PDF rectangle selects the matching feed entry. Clicking
a feed entry selects and scrolls to its rendered rectangle when available.
The optional `renderEntry` callback returns DOM content for details and host
actions. The host can handle `overlay-preview` events from hover or keyboard
focus, as well as `overlay-select` and `feed-select` events.

The component also accepts comment, pen-input, and mutation-policy ports.
See the bundled TypeScript declarations for the complete interface. Perform
authorization and persistence in the host. Call `destroy` to remove component
UI and dispose of the renderer.

The provider originated in [SciTeX Live Paper](https://github.com/scitex-ai/scitex-live-paper/tree/4790067f113df49618031c5bab1e679cadcd36bf).
