"""
クロスオリジンリクエストでの cookie の挙動を確かめるサンプルサーバ

- cookie `cnt` の数をリクエストごとに加算して、値をレスポンスのsvgに反映させる
"""

from base64 import b64decode
from datetime import datetime

from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer

PORT = 18001
ALLOWED_ORIGIN = 'http://localhost:8001'

SVG = """\
<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <text x="0" y="10" font-family="Verdana" font-size="10">Count: {}</text>
    <rect width="{}" height="5" x="0" y="20" fill="red" />
</svg>
"""


class RequestHandler(BaseHTTPRequestHandler):
    timeout = 1

    def make_response(self,
                      status,
                      content,
                      content_type='text/plain',
                      additional_headers={}):

        if isinstance(content, str):
            body = content.encode('UTF-8', 'replace')
        else:
            body = content

        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        for key in additional_headers:
            self.send_header(key, additional_headers[key])

        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        if 'favicon.ico' in self.path:
            self.make_response(HTTPStatus.NOT_FOUND, 'Not Found', 'text/plain')
            return

        cookies = SimpleCookie(self.headers.get('Cookie'))
        cnt = int(cookies['cnt'].value) if 'cnt' in cookies else 0
        cnt += 1

        self.make_response(
            HTTPStatus.OK,
            SVG.format(cnt, cnt * 10),
            'image/svg+xml',
            {
                'Set-Cookie': 'cnt={};Max-Age=180'.format(cnt),
                'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
                'Access-Control-Allow-Credentials': 'true',
            },
        )


if __name__ == '__main__':
    with HTTPServer(("", PORT), RequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
