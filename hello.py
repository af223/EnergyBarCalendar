from  __future__  import print_function
from flask import Flask, render_template, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from config import Config
import datetime
import pickle
import os.path
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.discovery import build 
from httplib2 import Http
#from oauth2client import file, client, tools
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route("/") # default
def home():
    return  render_template("home.html")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/')
    return render_template('login.html', title='Sign In', form=form)

def formatTime(x):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    days = {"M" : "Mon", "T": "Tue", "W" : "Wed", "Th": "Thu", "F": "Fri", "Sa": "Sat", "Su" : "Sun"}
    date = x[:10].split("-")
    resultDate = days[x[10]] + " " + months[int(date[1])-1] + " " + date[2] + ", " + date[0]
    time = x[11:].split("-")[0]
    if int(time[:2]) < 12:
        resultTime = time[:-3] + " AM"
        if time[:2] == "00":
            resultTime = "12" + resultTime[2:]
    else:
        resultTime = time[:-3] + " PM"
        if time[:2] != "12":
            resultTime = str((int(time[:2]) - 12)) + "" + resultTime[2:]
    return resultDate, resultTime

@app.route("/cal")
def cal():
    creds =  None
    SCOPES  = ['https://www.googleapis.com/auth/calendar.readonly']
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with  open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    """if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            # with open('token.pickle', 'wb') as token: # can't write files in Google App Engine so comment out or delete
            # pickle.dump(creds, token)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() +  'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    # for event in events:
    # start = event['start'].get('dateTime', event['start'].get('date'))
    # print(start, event['summary'])
    event_list = [event["summary"] for event in events]"""

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    tmax = (datetime.datetime.utcnow()+ datetime.timedelta(hours =24)).isoformat() +'Z'
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        timeMax= tmax, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    starts =[]
    ends = []

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        starts.append(formatTime(start))
        ends.append(formatTime(end))
        print(start, end, event['summary'])
    event_list = [(starts[i], ends[i], events[i]["summary"]) for i in range(len(events))]


    
    return  render_template("cal.html", events=event_list)
    
if  __name__  ==  "__main__":
    app.run(debug=True)