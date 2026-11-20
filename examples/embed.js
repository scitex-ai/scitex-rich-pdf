import { createPdfViewer } from "@scitex/sdk/ui/pdf-viewer";
import { createRichPdfViewer } from "@scitex/rich-pdf";
import "@scitex/rich-pdf/pdf-provider.css";

// Supply a PDF.js instance and the worker URL from the host application.
export async function mountExample({ container, feedContainer, pdfUrl, rendererOptions }) {
  const viewer = createRichPdfViewer({
    container,
    feedContainer,
    createPdfViewer,
    rendererOptions,
    ports: {
      documents: { resolve: (revision) => ({ id: revision, src: pdfUrl }) },
      feed: { list: () => [{ id: "note", label: "Reading note" }] },
    },
  });
  await viewer.load("example-v1");
  return viewer;
}
