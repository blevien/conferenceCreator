from __future__ import print_function
import datetime
import pickle
import csv
import json
from datetime import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import googleapiclient.discovery


with open('rosters.csv') as conferenceFile:
    conferences = [{k: v for k, v in row.items()} for row in csv.DictReader(conferenceFile, skipinitialspace=True)]


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'calendarmanager-270200-16f3bbab9389.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


page_token = None


def main():
    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

# Session,Teacher(s),TeacherEmailAddress,Location,Assignment,Parent,Student,Subject
# Start Date,Start Time,End Date,End Time,Description
    
    for conference in conferences:
 
        attendees = []
        attendees.append({'email': conference["TeacherEmailAddress"]})
        attendees.append({'email': conference["ParentEmail"]})
        attendees.append({'email': conference["studentEmail"]})

        event = {}

        #event["summary"] = roster["subject"] + " " + roster["block"]
        event["summary"] = conference["Subject"]

        startTime = datetime.strptime(" ".join([conference["Start Date"], conference["Start Time"]]), '%m/%d/%Y %I:%M:%S %p')
        startTime = startTime.strftime('%Y-%m-%dT%H:%M:%S-10:00')
        event["start"] = {'dateTime': startTime, 'timeZone': 'Pacific/Honolulu'}

        endTime = datetime.strptime(" ".join([conference["End Date"], conference["End Time"]]), '%m/%d/%Y %I:%M:%S %p')
        endTime = endTime.strftime('%Y-%m-%dT%H:%M:%S-10:00')
        event["end"] = {'dateTime': endTime, 'timeZone': 'Pacific/Honolulu'}

        event["attendees"] = attendees

        event["reminders"] = {
                                'useDefault': False,
                                'overrides': [],

                              }
        event["guestsCanInviteOthers"]: False
        event["guestsCanModify"]: False

        #print("{} - {}".format(event["summary"], event['attendees']))

        user = conference["TeacherEmailAddress"]
        delegated_credentials = credentials.with_subject(user)

        calendar = googleapiclient.discovery.build('calendar', 'v3', credentials=delegated_credentials)


        with open("logs.txt", "a") as logs:
            try:
                event = calendar.events().insert(calendarId=user, body=event).execute()
                logs.write('{},{},{},{}\n'.format(conference['Teacher(s)'], conference['Start Date'], conference['Subject'], event.get('id')))
                print('{},{},{} created. ID: {}\n'.format(conference['Teacher(s)'], conference['Start Date'], conference['Subject'], event.get('id')))

            except Exception as e:
                
                error = str(e)

                print(error)
                if "403" in error:
                    
                    logs.write('{} {} {} failed'.format(conference['Start Date'],conference['Teacher(s)'], conference['Subject'], "403" ))
                    print("403: Event Creation Failed")
          


if __name__ == '__main__':
    main()