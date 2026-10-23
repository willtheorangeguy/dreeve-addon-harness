"""Prepare missing synthetic FIT fixtures or verify them through Dreeve's actual API."""

import argparse
import json
import os
from datetime import UTC, date, datetime
from pathlib import Path

from client import API
from fixtures import seed_fixtures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    manifest_path = Path('/runtime/seed-manifest.json')
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    configured = os.environ.get('SEED_END_DATE', '')
    end_date = date.fromisoformat(configured or (manifest or {}).get('end_date')
                                 or str(datetime.now(UTC).date()))
    if manifest and manifest['end_date'] != str(end_date):
        raise ValueError('Seed date changed; use harness.py reset --yes before selecting a new date')
    fixtures = list(seed_fixtures(end_date))
    manifest = {'end_date': str(end_date), 'fixtures': [metadata for metadata, _ in fixtures]}
    manifest_path.write_text(json.dumps(manifest, indent=2))
    # This convenience file is local sandbox data and is never committed or logged.
    Path('/runtime/credentials.json').write_text(json.dumps({
        'api_key': os.environ['DREEVE_API_KEY'], 'app_url': os.environ['APP_URL'],
        'public_url': os.environ['PUBLIC_URL'], 'end_date': str(end_date),
    }, indent=2))
    actual = {activity['name']: activity for activity in API().activities()}
    if args.verify:
        for metadata, _ in fixtures:
            item = actual.get(metadata['name'])
            assert item is not None, 'Missing seed activity: ' + metadata['name']
            assert item['sportType'] == metadata['sport'], item
            assert item['distanceInMeter'] == metadata['distance'], item
            assert item['elapsedTimeInSeconds'] == metadata['duration'], item
            assert item['calories'] == metadata['calories'], item
        print('Verified all eight seeded workouts through the authenticated Dreeve API.')
    else:
        pending = 0
        for metadata, payload in fixtures:
            if metadata['name'] not in actual:
                path = Path('/watch') / metadata['filename']
                temporary = path.with_suffix('.tmp')
                temporary.write_bytes(payload)
                temporary.replace(path)
                pending += 1
        print(f'Prepared {pending} missing seed workouts; existing fixture dates are preserved.')


if __name__ == '__main__':
    main()
