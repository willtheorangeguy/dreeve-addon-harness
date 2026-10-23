"""Small authenticated Dreeve API client, usable by addons without pip dependencies."""

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4


class APIError(RuntimeError):
    def __init__(self, status, path):
        self.status = status
        super().__init__(f'HTTP {status} from {path}')


class API:
    def __init__(self, token=None):
        self.base = os.environ.get('APP_URL', 'http://app:8080').rstrip('/')
        self.token = token if token is not None else os.environ['DREEVE_API_KEY']
        self.opener = build_opener(ProxyHandler({}))

    def request(self, path, data=None, method=None, content_type='application/json', authenticated=True):
        headers = {'Content-Type': content_type}
        if authenticated:
            headers['Authorization'] = 'Bearer ' + self.token
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        request = Request(self.base + path, data=data, headers=headers,
                          method=method or ('POST' if data is not None else 'GET'))
        try:
            with self.opener.open(request, timeout=30) as response:
                body = response.read()
                if not body:
                    return None
                return json.loads(body) if 'json' in response.headers.get('Content-Type', '') else body
        except HTTPError as error:
            error.close()
            raise APIError(error.code, path) from None

    def upload(self, filename, payload):
        boundary = 'harness-' + uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
                f'filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()
        body += payload + f'\r\n--{boundary}--\r\n'.encode()
        return self.request('/api/v1/activity/upload', body,
                            content_type='multipart/form-data; boundary=' + boundary)

    def rows(self, path, key):
        rows = []
        for page in range(1, 101):
            separator = '&' if '?' in path else '?'
            response = self.request(f'{path}{separator}pagination[page]={page}&pagination[size]=100')
            rows.extend(response[key])
            if page >= response['pagination']['totalPages']:
                return rows
        raise RuntimeError('Pagination exceeded the sandbox safety limit')

    def activities(self):
        return self.rows('/api/v1/activities', 'activities')


def wait_for(description, predicate, timeout=370):
    print('Waiting: ' + description, flush=True)
    deadline = time.monotonic() + timeout
    heartbeat = time.monotonic()
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        if time.monotonic() - heartbeat > 30:
            print('Still waiting: ' + description, flush=True)
            heartbeat = time.monotonic()
        time.sleep(2)
    raise AssertionError('Timed out: ' + description)


def snapshot():
    activities = API().activities()
    manifest = Path('/runtime/seed-manifest.json')
    return {'platform': 'dreeve', 'activity_count': len(activities),
            'sports': sorted({a['sportType'] for a in activities}),
            'activities': activities,
            'seed': json.loads(manifest.read_text()) if manifest.exists() else None}
