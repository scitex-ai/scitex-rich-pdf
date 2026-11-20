from importlib.metadata import version
import os
from json import loads

import pytest
from playwright.sync_api import expect, sync_playwright

from scitex_rich_pdf import get_frontend_package_dir


def test_frontend_exports():
    package_dir = get_frontend_package_dir()
    manifest = loads((package_dir / "package.json").read_text())
    assert manifest["version"] == version("scitex-rich-pdf")
    for filename in manifest["files"]:
        assert (package_dir / filename).stat().st_size > 0


@pytest.mark.browser
@pytest.mark.skipif(not os.environ.get("RICH_PDF_BROWSER"), reason="requires Chromium")
def test_viewer_feed_lifecycle():
    script = (get_frontend_package_dir() / "pdf-provider.js").read_text()
    html = '<main><div id="pdf"></div><aside id="feed"></aside></main>'
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.route("https://rich-pdf.test/", lambda route: route.fulfill(body=html, content_type="text/html"))
        page.route(
            "https://rich-pdf.test/pdf-provider.js",
            lambda route: route.fulfill(body=script, content_type="text/javascript"),
        )
        page.goto("https://rich-pdf.test/")
        page.evaluate(
            """async () => {
              const { createRichPdfViewer } = await import("/pdf-provider.js");
              window.events = [];
              window.viewer = createRichPdfViewer({
                container: document.querySelector('#pdf'),
                feedContainer: document.querySelector('#feed'),
                createPdfViewer: ({container, hooks}) => ({
                  async load() {
                    const element = document.createElement('div');
                    element.style.cssText = 'position:relative;width:300px;height:100px';
                    container.replaceChildren(element);
                    hooks.onPageRender(1, {}, { element, pdfToViewportRect: box => box });
                  },
                  destroy() { container.replaceChildren(); },
                }),
                ports: {
                  documents: {resolve: id => ({id, src: 'test.pdf'})},
                  overlays: {list: ({id}) => [{
                    id, label: 'Region ' + id, page: 1, bbox: [10, 10, 80, 50],
                  }]},
                  feed: {
                    list: ({id}) => [
                      {id, overlayId: id, label: 'Entry ' + id},
                      {id: 'unresolved', label: 'Unresolved'},
                    ],
                    renderEntry(entry) {
                      const button = document.createElement('button');
                      button.textContent = 'Action ' + entry.id;
                      button.onclick = () => window.events.push('action');
                      return button;
                    },
                  },
                  events: {emit: event => window.events.push(event.type)},
                },
              });
              await viewer.load('revision-a');
            }"""
        )
        overlay = page.get_by_role("button", name="Region revision-a")
        entry = page.get_by_role("button", name="Entry revision-a")
        overlay.focus()
        overlay.click()
        expect(entry).to_have_attribute("aria-current", "true")
        entry.click()
        expect(overlay).to_have_attribute("aria-current", "true")
        page.get_by_role("button", name="Action revision-a").click()
        page.get_by_role("button", name="Unresolved", exact=True).click()
        expect(overlay).not_to_have_attribute("aria-current", "true")
        assert {"overlay-preview", "overlay-select", "feed-select", "action"} <= set(
            page.evaluate("window.events")
        )
        page.evaluate("viewer.load('revision-b')")
        expect(entry).to_have_count(0)
        expect(page.get_by_role("button", name="Entry revision-b")).to_be_visible()
        page.evaluate("viewer.destroy()")
        expect(page.locator("#feed > *")).to_have_count(0)
        browser.close()
