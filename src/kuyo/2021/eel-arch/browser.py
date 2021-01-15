import logging
import pkgutil
import subprocess
import sys

from http import HTTPStatus
from http.server import (
    ThreadingHTTPServer,
    BaseHTTPRequestHandler,
)
from pathlib import Path


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    bundle_dir = Path(sys._MEIPASS)
else:
    bundle_dir = Path(__file__).parent


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = (bundle_dir / "index.html").read_bytes()

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', "text/html")
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


PORT = 18000
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP_URL = f"http://127.0.0.1:{PORT}/index.html"
WIDTH = 500
HEIGHT = 300


def main():
    launching_url = (
        "data:text/html,<html><body><script>"
        f"window.resizeTo({WIDTH},{HEIGHT});"
        f"window.location='{APP_URL}';"
        "</script></body></html>"
    )
    cmd = [CHROME, f"--app={launching_url}"]
    logger.debug(cmd)
    subprocess.Popen(cmd,
                     stdout=subprocess.DEVNULL,
                     stdin=subprocess.DEVNULL)

    with ThreadingHTTPServer(("", PORT), RequestHandler) as httpd:
        logger.debug(f"serving at port: {PORT}")
        httpd.serve_forever()

    logger.debug("finish")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
