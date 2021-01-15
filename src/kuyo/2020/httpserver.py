"""
標準(エラー)出力が読めない環境で実行する必要があったのでファイルに書いたが
その後標準出力読めるようになったのでいらんなってなったもの
"""
import logging

from http import HTTPStatus
from http.server import (
    ThreadingHTTPServer,
    BaseHTTPRequestHandler,
)


logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/hello.log'),
    ],
)
logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # super class が sys.stderr.write を使っているので書き換える
        logger.info("%s - - [%s] %s",
                    self.address_string(),
                    self.log_date_time_string(),
                    format % args)

    def do_GET(self):
        body = b"HELLO"

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', "text/plain")
        self.send_header('Content-Length', str(len(body)))

        self.end_headers()
        self.wfile.write(body)


PORT = 18000

def main():
    with ThreadingHTTPServer(("", PORT), RequestHandler) as httpd:
        logger.debug(f"serving at port: {PORT}")
        httpd.serve_forever()

    logger.debug("finish")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except:
        logger.exception("Error")
