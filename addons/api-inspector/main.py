"""Standalone addon template: no dependency on the harness's Python client."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = Request(os.environ['APP_URL'] + '/api/v1/activities?pagination[size]=100',
                          headers={'Authorization': 'Bearer ' + os.environ['DREEVE_API_KEY']})
        try:
            with build_opener(ProxyHandler({})).open(request, timeout=10) as response:
                data = json.load(response)
            manifest = Path('/runtime/seed-manifest.json')
            value = {'platform': 'dreeve', 'implementation': 'api-inspector',
                     'activity_count': data['pagination']['total'], 'activities': data['activities'],
                     'seed': json.loads(manifest.read_text()) if manifest.exists() else None}
            code = 200
        except OSError:
            value, code = {'error': 'Dreeve API is unavailable'}, 503
        body = json.dumps(value).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
