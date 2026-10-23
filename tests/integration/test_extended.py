import unittest
from client import APIError
from contract import api


class DreeveExtendedTests(unittest.TestCase):
    def test_pagination_has_no_missing_or_repeated_activities(self):
        client = api()
        expected = {a['id'] for a in client.activities()}
        found = []
        pages = client.request('/api/v1/activities?pagination[size]=2')['pagination']['totalPages']
        for page in range(1, pages + 1):
            data = client.request(f'/api/v1/activities?pagination[size]=2&pagination[page]={page}')
            self.assertTrue(0 < len(data['activities']) <= 2)
            found.extend(a['id'] for a in data['activities'])
        self.assertEqual(set(found), expected)
        self.assertEqual(len(found), len(set(found)))

    def test_invalid_pagination_is_rejected(self):
        with self.assertRaises(APIError) as caught:
            api().request('/api/v1/activities?pagination[page]=0')
        self.assertEqual(caught.exception.status, 400)

    def test_unsupported_upload_is_rejected(self):
        with self.assertRaises(APIError) as caught:
            api().upload('unsupported-harness.txt', b'not an activity file')
        self.assertEqual(caught.exception.status, 422)

    def test_activity_details_match_listed_values(self):
        client = api()
        for item in client.activities():
            detail = client.request('/api/v1/activities/' + item['id'])
            for field in ('id', 'name', 'sportType', 'distanceInMeter', 'calories', 'elapsedTimeInSeconds'):
                self.assertEqual(detail[field], item[field])

    def test_invalid_edit_is_rejected_without_changing_activity(self):
        client = api()
        item = client.activities()[0]
        path = '/api/v1/activities/' + item['id']
        with self.assertRaises(APIError) as caught:
            client.request(path, {'sportType': 'NotASport'}, method='PATCH')
        self.assertEqual(caught.exception.status, 400)
        self.assertEqual(client.request(path)['sportType'], item['sportType'])

    def test_summary_fixture_has_no_gpx_route(self):
        client = api()
        item = next(a for a in client.activities() if a['name'] == 'Harness Strength')
        with self.assertRaises(APIError) as caught:
            client.request('/api/v1/activities/' + item['id'] + '/gpx')
        self.assertEqual(caught.exception.status, 404)
