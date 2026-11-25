"""Exercise the built starter at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")
                page.wait_for_selector('#cards article')
                assert 'Vancouver' in page.locator('#cards').inner_text()
                page.select_option('#left','ottawa')
                assert 'National Capital FreeNet' in page.locator('#cards').inner_text()
                page.select_option('#year','1996')
                assert 'No indexed capture' in page.locator('#cards').inner_text()
                assert 'web.archive.org/web/' in page.locator('#cards a').first.get_attribute('href')
                page.fill('#network-search','Sympatico')
                assert page.locator('#directory article').count()==1
                page.locator('#directory button').click()
                assert page.locator('#left').input_value()=='sympatico'
                assert 'Sympatico' in page.locator('#cards').inner_text()
                page.fill('#host','https://chebucto.ns.ca/a')
                page.click('#other-domain button')
                assert 'domain=chebucto.ns.ca' in page.locator('#custom-result a').first.get_attribute('href')
                page.select_option('#year','2000')
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                browser.close()
            print("Browser checks passed: published data interaction and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
