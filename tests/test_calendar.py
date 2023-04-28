import os
import sys
import tempfile
import json

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from google_calendar_api import Event, add_event, get_credentials


@pytest.fixture(scope="module")
def credentials():
    return get_credentials()


@pytest.fixture(scope="module")
def event_data():
    return {
        'summary': 'Test Event',
        'location': '123 Test Street, Test City, TS 12345',
        'description': 'A test event for testing purposes.',
        'start': '2023-06-01T09:00:00-07:00',
        'end': '2023-06-01T12:00:00-07:00',
        'attendees': ['test1@example.com', 'test2@example.com'],
        'timeZone': 'America/Los_Angeles',
    }


def test_event_class(event_data):
    event = Event(**event_data)
    assert event.summary == event_data['summary']
    assert event.location == event_data['location']
    assert event.description == event_data['description']
    assert event.start == event_data['start']
    assert event.end == event_data['end']
    assert event.attendees == event_data['attendees']
    assert event.timeZone == event_data['timeZone']


def test_add_event(event_data, credentials):
    event = Event(**event_data)
    with tempfile.TemporaryDirectory() as temp_dir:
        original_token_path = '../token.json'
        temp_token_path = os.path.join(temp_dir, 'token.json')
        os.rename(original_token_path, temp_token_path)
        try:
            add_event(event)
            assert True
        except Exception as e:
            pytest.fail(f"Adding event failed: {e}")
        finally:
            os.rename(temp_token_path, original_token_path)


if __name__ == '__main__':
    pytest.main([__file__])
