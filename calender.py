from __future__ import print_function
import datetime
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Full calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

def google_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Opens browser for login
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def main():
    service = google_calendar_service()

    # Test event (next hour)
    now = datetime.datetime.utcnow()
    start = now + datetime.timedelta(minutes=5)
    end = start + datetime.timedelta(hours=1)

    event = {
        'summary': 'Test Activity Summary',
        'description': 'This is a test event from Python',
        'start': {'dateTime': start.isoformat() + 'Z'},
        'end': {'dateTime': end.isoformat() + 'Z'},
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('✅ Event created:', event.get('htmlLink'))

if __name__ == '__main__':
    main()
