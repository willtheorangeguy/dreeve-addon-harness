"""Working read-only addon using the real authenticated Dreeve API."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from client import APIError, snapshot


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            value = snapshot()
            status = 200
        except (APIError, OSError) as error:
            value, status = {'error': str(error)}, 503
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
