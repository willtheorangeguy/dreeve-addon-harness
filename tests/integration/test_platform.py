"""Real Dreeve HTTP and scheduled-import checks; no mocked application services."""

import html
import json
import os
import re
import time
import unittest
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener
from uuid import uuid4

from client import API, APIError, snapshot, wait_for
from fixtures import seed_fixtures


class HarnessTests(unittest.TestCase):
    def test_seed_values_and_sports(self):
        manifest = json.loads(Path('/runtime/seed-manifest.json').read_text())
        actual = {a['name']: a for a in API().activities()}
        for expected in manifest['fixtures']:
            activity = actual[expected['name']]
            self.assertEqual(activity['sportType'], expected['sport'])
            self.assertEqual(activity['distanceInMeter'], expected['distance'])
            self.assertEqual(activity['elapsedTimeInSeconds'], expected['duration'])
            self.assertEqual(activity['calories'], expected['calories'])
            self.assertIn('Synthetic Dreeve addon harness fixture', activity['description'])
        self.assertEqual(len(manifest['fixtures']), 8)
        self.assertGreaterEqual(len({a['sport'] for a in manifest['fixtures']}), 6)

    def test_api_rejects_missing_and_bad_tokens(self):
        for client, authenticated in [(API(), False), (API('invalid-sandbox-key'), True)]:
            with self.assertRaises(APIError) as caught:
                client.request('/api/v1/activities', authenticated=authenticated)
            self.assertEqual(caught.exception.status, 401)

    def test_real_admin_login(self):
        opener = build_opener(ProxyHandler({}), HTTPCookieProcessor(CookieJar()))
        url = os.environ['APP_URL'] + '/admin/login'
        with opener.open(url, timeout=20) as response:
            page = response.read().decode()
        token = html.unescape(re.search(r'name="_csrf_token" value="([^"]+)"', page).group(1))
        data = urlencode({'_username': os.environ['DEMO_USERNAME'],
                          '_password': os.environ['DEMO_PASSWORD'], '_csrf_token': token}).encode()
        with opener.open(Request(url, data=data, headers={
                'Origin': os.environ['APP_URL'], 'Referer': url}), timeout=20) as response:
            self.assertEqual(response.status, 200)
            self.assertNotIn('/admin/login', response.url)
        with opener.open(os.environ['APP_URL'] + '/admin/upload', timeout=20) as response:
            self.assertNotIn('/admin/login', response.url)

    def test_example_addon_reads_real_data(self):
        if os.environ.get('CHECK_EXAMPLE_ADDON', 'true').lower() != 'true':
            self.skipTest('Custom addon configured; use its own assertions in compose.override.yaml')
        opener = build_opener(ProxyHandler({}))
        with opener.open('http://example-addon:8080/', timeout=15) as response:
            value = json.load(response)
        self.assertEqual(value['platform'], 'dreeve')
        self.assertGreaterEqual(value['activity_count'], 8)
        self.assertEqual(len(value['seed']['fixtures']), 8)

    def test_real_sensor_streams(self):
        api = API()
        activities = {a['name']: a for a in api.activities()}
        ride = activities['Harness Long Ride']
        streams = api.request('/api/v1/activities/' + ride['id'] + '/streams')
        self.assertTrue(streams['timeInSeconds'])
        self.assertTrue(streams['heartRate'])
        self.assertTrue(streams['powerInWatts'])
        self.assertTrue(streams['cadence'])
        self.assertFalse(streams['latLng'])
        strength = activities['Harness Strength']
        self.assertIsNone(strength['averageHeartRate'])

    def test_seed_replay_is_idempotent(self):
        # Re-queue every original seed file; the real daemon must skip them.
        from datetime import date
        manifest = json.loads(Path('/runtime/seed-manifest.json').read_text())
        api = API()
        before = {a['id'] for a in api.activities()}
        existing = {row['id'] for row in api.rows('/api/v1/file-imports', 'fileImports')}
        expected_names = set()
        for metadata, payload in seed_fixtures(date.fromisoformat(manifest['end_date'])):
            api.upload(metadata['filename'], payload)
            expected_names.add(metadata['filename'])

        def replayed():
            imports = api.rows('/api/v1/file-imports', 'fileImports')
            rows = [r for r in imports if r['id'] not in existing and r['filename'] in expected_names]
            self.assertFalse(any(r['status'] == 'failed' for r in rows), rows)
            return len(rows) == 8 and all(r['status'] == 'skipped' for r in rows)

        wait_for('daemon skips eight re-uploaded seed files', replayed)
        after = {a['id'] for a in api.activities()}
        self.assertTrue(before.issubset(after))
        fixture_names = {item['name'] for item in manifest['fixtures']}
        self.assertEqual(sum(a['name'] in fixture_names for a in api.activities()), 8)

    def test_watch_and_upload_roundtrip(self):
        # Both intake methods run through the unchanged real daemon, then API edit/delete.
        from fixtures import build_activity
        api = API()
        suffix = uuid4().hex[:12]
        names = ['Roundtrip watch ' + suffix, 'Roundtrip API ' + suffix]
        starts = [datetime.now(UTC) - timedelta(days=1, seconds=i * 900) for i in range(2)]
        payloads = [build_activity(name, start) for name, start in zip(names, starts)]
        temporary = Path('/watch') / (suffix + '.tmp')
        temporary.write_bytes(payloads[0])
        temporary.replace(temporary.with_suffix('.fit'))
        self.assertEqual(api.upload(suffix + '-api.fit', payloads[1])['status'], 'queued')
        imported = []
        try:
            def find_imports():
                found = [a for a in api.activities() if a['name'] in names]
                return found if len(found) == 2 else None

            imported = wait_for('daemon imports watch-folder and HTTP-upload workouts', find_imports)
            for activity in imported:
                path = '/api/v1/activities/' + activity['id']
                self.assertEqual(api.request(path)['distanceInMeter'], 2000)
                edited = api.request(path, {'description': 'Addon roundtrip verified',
                                           'name': activity['name'] + ' edited'}, method='PATCH')
                self.assertEqual(edited['description'], 'Addon roundtrip verified')
                self.assertTrue(edited['name'].endswith(' edited'))
            Path('/reports/roundtrip.json').write_text(json.dumps({'imported': imported}, indent=2))
        finally:
            # Also discover partial successes if a scheduled import assertion failed.
            candidates = [a for a in api.activities()
                          if a['name'] in names or a['name'] in [n + ' edited' for n in names]]
            for activity in candidates:
                path = '/api/v1/activities/' + activity['id']
                api.request(path, method='DELETE')
                with self.assertRaises(APIError) as caught:
                    api.request(path)
                self.assertEqual(caught.exception.status, 404)
