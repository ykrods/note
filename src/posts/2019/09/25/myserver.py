from base64 import b64decode

from http import HTTPStatus
from http.server import (
    HTTPServer,
    ThreadingHTTPServer,
    BaseHTTPRequestHandler,
)

ICON_B64 = 'AAABAAEAEBACAAEAAQCwAAAAFgAAACgAAAAQAAAAIAAAAAEAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB9icsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'

# SERVER_CLASS = ThreadingHTTPServer
SERVER_CLASS = HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    # 区別しやすいように Server ヘッダにサーバのクラス名を入れて返す
    server_version = SERVER_CLASS.__name__

    def make_response(self,
                      content,
                      content_type='text/plain'):
        if isinstance(content, str):
            body = content.encode('UTF-8', 'replace')
        else:
            body = content

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))

        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/favicon.ico':
            content = b64decode(ICON_B64)
            self.make_response(content, 'image/vnd.microsoft.icon')
        else:
            self.make_response('plain text')


PORT = 18000

if __name__ == '__main__':
    with SERVER_CLASS(("", PORT), RequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
