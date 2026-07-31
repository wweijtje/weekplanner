from __future__ import print_function
# list_events_oauth.py
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pytz import utc


def get_timestamp_from_google(date_dict):
    if 'date' in date_dict:
        return datetime.datetime.fromisoformat(date_dict["date"]).replace(tzinfo=utc)
    elif 'dateTime' in date_dict:
        return datetime.datetime.fromisoformat(date_dict["dateTime"])


def compact_google_event(raw_event):
    """Keep only fields required for rendering and date parsing."""
    summary = raw_event.get("summary", "Untitled")
    start = raw_event.get("start", {})
    end = raw_event.get("end", {})

    compact_start = {}
    if "dateTime" in start:
        compact_start["dateTime"] = start["dateTime"]
    elif "date" in start:
        compact_start["date"] = start["date"]

    compact_end = {}
    if "dateTime" in end:
        compact_end["dateTime"] = end["dateTime"]
    elif "date" in end:
        compact_end["date"] = end["date"]

    if not compact_start or not compact_end:
        return None

    return {
        "summary": summary,
        "start": compact_start,
        "end": compact_end
    }

def compact_google_events(events):
    compacted_events = []
    for raw_event in events or []:
        compact_event = compact_google_event(raw_event)
        if compact_event is not None:
            compacted_events.append(compact_event)
    return compacted_events


def collect_agenda_data(dt_0, dt_e, config, agenda):

    SCOPES = config['scopes']


    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save token for later
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    calendar_id = os.environ.get(agenda['id']) # Collect from env variable

    if not calendar_id:
        raise ValueError(f'Environmental variable "{calendar_id}" not found.')

    events_result = service.events().list(
        calendarId=calendar_id, timeMin=dt_0.isoformat(), timeMax=dt_e.isoformat(),
        maxResults=20, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        _ = event['start'].get('dateTime', event['start'].get('date'))

    return events
