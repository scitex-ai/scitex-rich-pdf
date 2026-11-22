from importlib.metadata import distribution, version
import os
from json import loads

import pytest
from playwright.sync_api import expect, sync_playwright

from scitex_rich_pdf import get_frontend_package_dir


def test_frontend_exports_match_distribution():
    # Arrange
    package_dir = get_frontend_package_dir()
    # Act
    manifest = loads((package_dir / "package.json").read_text())
    missing_assets = [name for name in manifest["files"] if not (package_dir / name).is_file()]
    # Assert
    assert (manifest["version"], missing_assets) == (version("scitex-rich-pdf"), [])


@pytest.mark.browser
@pytest.mark.skipif(not os.environ.get("RICH_PDF_BROWSER"), reason="requires Chromium")
def test_viewer_feed_lifecycle():
    # Arrange
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
        # Act
        overlay = page.get_by_role("button", name="Region revision-a")
        entry = page.get_by_role("button", name="Entry revision-a")
        overlay.focus()
        overlay.click()
        # Assert
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


def test_scitex_provider_discovery_metadata():
    # Arrange
    dist = distribution("scitex-rich-pdf")
    skill = get_frontend_package_dir().parent / "_skills" / "scitex-rich-pdf" / "SKILL.md"
    # Act
    declarations = {(entry.group, entry.name, entry.value) for entry in dist.entry_points}
    expected = {
        (group, "scitex-rich-pdf", "scitex_rich_pdf")
        for group in ("scitex_dev.docs", "scitex_dev.skills")
    }
    # Assert
    assert (expected <= declarations, "name: scitex-rich-pdf" in skill.read_text()) == (True, True)


def test_installed_sphinx_includes_reader_docs():
    # Arrange
    bundle = get_frontend_package_dir().parent / "_sphinx_html"
    # Act
    page = (bundle / "index.html").read_text(encoding="utf-8")
    # Assert
    assert "SciTeX Rich PDF" in page


@pytest.mark.browser
@pytest.mark.skipif(not os.environ.get("RICH_PDF_BROWSER"), reason="requires Chromium")
def test_preview_supports_highlighter_touch_and_figure_regions():
    script = (get_frontend_package_dir() / "pdf-provider.js").read_text()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(has_touch=True, viewport={"width": 390, "height": 750})
        page.route(
            "https://rich-pdf.test/",
            lambda route: route.fulfill(body='<main id="pdf"></main>', content_type="text/html"),
        )
        page.route(
            "https://rich-pdf.test/pdf-provider.js",
            lambda route: route.fulfill(body=script, content_type="text/javascript"),
        )
        page.goto("https://rich-pdf.test/")
        page.evaluate(
            """async () => {
              const { createRichPdfViewer } = await import("/pdf-provider.js");
              window.viewer = createRichPdfViewer({
                container: document.querySelector('#pdf'),
                createPdfViewer: ({container, hooks}) => ({
                  async load() {
                    const element = document.createElement('div');
                    element.style.cssText = 'position:relative;width:300px;height:180px';
                    container.replaceChildren(element);
                    hooks.onPageRender(1, {}, {element, pdfToViewportRect: box => box});
                  },
                  destroy() { container.replaceChildren(); },
                }),
                ports: {
                  documents: {resolve: id => ({id, src: 'test.pdf'})},
                  overlays: {list: () => [
                    {id: 'value', label: 'Value', page: 1, bbox: [10, 10, 42, 34], appearance: 'highlight'},
                    {id: 'figure', label: 'Figure', page: 1, bbox: [10, 52, 142, 130], appearance: 'region'},
                  ]},
                  preview: {render(panel, overlay, signal) {
                    panel.textContent = 'Graph of ' + overlay.label;
                    signal.addEventListener('abort', () => { window.cancelled = true; });
                  }},
                },
              });
              await viewer.load('first');
            }"""
        )

        value = page.get_by_role("button", name="Value")
        figure = page.get_by_role("button", name="Figure")
        assert (value.get_attribute("data-appearance"), figure.get_attribute("data-appearance")) == (
            "highlight", "region"
        )
        figure.tap()
        dialog = page.get_by_role("dialog", name="Figure")
        expect(dialog).to_have_text("×Graph of Figure")
        page.evaluate("viewer.setComments([])")
        expect(dialog).to_be_visible()
        assert page.evaluate("window.cancelled === undefined")
        page.get_by_role("button", name="Close evidence preview").tap()
        expect(figure).to_be_focused()
        value.tap()
        expect(page.get_by_role("dialog", name="Value")).to_be_visible()
        page.evaluate("viewer.load('second')")
        expect(page.get_by_role("dialog")).to_have_count(0)
        assert page.evaluate("window.cancelled") is True
        browser.close()


@pytest.mark.browser
@pytest.mark.skipif(not os.environ.get("RICH_PDF_BROWSER"), reason="requires Chromium")
def test_navigation_is_ready_before_pages_finish_rendering():
    # Arrange
    script = (get_frontend_package_dir() / "pdf-provider.js").read_text()
    html = (
        '<button id="toggle" aria-controls="navigation">Pages &amp; bookmarks</button>'
        '<nav id="navigation" hidden></nav>'
        '<div id="paper" style="height:80px;overflow:auto"></div>'
    )
    with sync_playwright() as playwright, playwright.chromium.launch() as browser:
        page = browser.new_page()
        page.route("https://rich-pdf.test/", lambda route: route.fulfill(body=html, content_type="text/html"))
        page.route(
            "https://rich-pdf.test/pdf-provider.js",
            lambda route: route.fulfill(body=script, content_type="text/javascript"),
        )
        page.goto("https://rich-pdf.test/")
        page.evaluate("""async () => {
          const {createPdfNavigation} = await import("/pdf-provider.js");
          const pdf = {
            numPages: 2,
            async getOutline() { return [{title: "References", dest: [1, {name: "Fit"}]}]; },
            async getPage() {
              return {
                getViewport: ({scale}) => ({width: 200 * scale, height: 300 * scale}),
                render: ({canvasContext}) => {
                  canvasContext.fillRect(0, 0, 5, 5);
                  return {promise: Promise.resolve()};
                },
              };
            },
          };
          window.pdfNavigation = createPdfNavigation({
            container: document.querySelector("#navigation"),
            toggle: document.querySelector("#toggle"),
            pdfjs: {getDocument: () => ({promise: Promise.resolve(pdf)})},
          });
          pdfNavigation.runtime.getDocument();
        }""")
        # Act
        page.get_by_role("button", name="Pages & bookmarks").click()
        page.get_by_role("button", name="Page 2", exact=True).wait_for()
        page.wait_for_function("""() => document.querySelector("canvas")
          ?.getContext("2d").getImageData(0, 0, 1, 1).data[3] === 255""")
        page.get_by_role("button", name="Bookmarks", exact=True).click()
        page.get_by_role("button", name="References", exact=True).click()
        scroll = page.evaluate("""() => {
          const viewer = document.querySelector("#paper");
          for (const page of [1, 2]) {
            const element = document.createElement("div");
            element.style.height = "200px";
            viewer.append(element);
            pdfNavigation.pageRendered(page, {element});
          }
          pdfNavigation.finishRender();
          return viewer.scrollTop;
        }""")
        page.get_by_role("button", name="Pages & bookmarks").click()
        closed = page.locator("#navigation").is_hidden()
    # Assert
    assert (scroll, closed) == (188, True)
