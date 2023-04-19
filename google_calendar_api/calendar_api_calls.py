from __future__ import print_function

import datetime
import os.path
import json
import pickle
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CACHE_DURATION = 5


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """

    scopes = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../token.json'):
        creds = Credentials.from_authorized_user_file('../token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_today_events():
    """
    Gets all of today's events from the user's primary calendar.

    :return: A list of tuples containing the start time, end time, and summary of each event (the event's name)
    """

    creds = get_credentials()
    event_list = []

    cache_file = "events_cache.pkl"
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            cache_data = pickle.load(f)
            if time.time() - cache_data["timestamp"] < CACHE_DURATION:
                print("Using cached data.")
                return json.dumps(cache_data["event_list"])

    try:
        service = build('calendar', 'v3', credentials=creds)

        calendar = service.calendars().get(calendarId='primary').execute()
        time_zone = calendar.get('timeZone')

        # Use the time zone to get today's events
        today = datetime.datetime.now(datetime.timezone.utc).astimezone()
        start = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        tomorrow = today + datetime.timedelta(days=1)
        end = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        print('Getting today\'s events')
        events_results = service.events().list(calendarId='primary', timeMin=start, timeMax=end, singleEvents=True, orderBy='startTime', timeZone=time_zone).execute()

        events = events_results.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time_obj = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
            local_time = start_time_obj.astimezone()
            start_time = local_time.strftime('%I:%M %p')

            end = event['end'].get('dateTime', event['end'].get('date'))
            end_time_obj = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')
            local_time = end_time_obj.astimezone()
            end_time = local_time.strftime('%I:%M %p')

            event_list.append((start_time, end_time, event['summary']))

        print(event_list)

        cache_data = {
            "timestamp": time.time(),
            "event_list": event_list
        }

        with open(cache_file, "wb") as f:
            pickle.dump(cache_data, f)

    except HttpError as error:
        print('An error occurred: %s' % error)

    return json.dumps(event_list)


if __name__ == '__main__':
    get_today_events()
