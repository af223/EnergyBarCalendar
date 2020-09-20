from  __future__  import print_function
from flask import Flask, render_template, flash, redirect, url_for, request
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
from flask_sqlalchemy import SQLAlchemy 
import os 

  
file_path = os.path.abspath(os.getcwd())#+"/todo.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db1.db'
app.config['SQLALCHEMY_BINDS'] = {
    'todo': 'sqlite:///todo.db',
    'calen': 'sqlite:///calen.db'
}
db = SQLAlchemy(app)  



@app.route("/") # default
def home():
    return render_template("home.html")

class Tasks(db.Model): 
    __bind_key__ = 'todo'
    id = db.Column(db.Integer, primary_key=True) 
    text = db.Column(db.String(200)) 
    complete = db.Column(db.Boolean) 
    priority = db.Column(db.Boolean)
  
    def __repr__(self): 
        return self.text 

class Calen(db.Model):
    __bind_key__ = 'calen'
    id = db.Column(db.Integer, primary_key=True) 
    text = db.Column(db.String(200))
    eventss = db.Column(db.String(200)) 
  
    def __repr__(self): 
        return self.text 

@app.route('/tasks') 
def tasks(): 
    incomplete = Tasks.query.filter_by(complete=False).all() 
    complete = Tasks.query.filter_by(complete=True).all() 
  
    return render_template('tasks.html', incomplete=incomplete, complete=complete) 
  
  
@app.route('/tasks/add', methods=['POST']) 
def add(): 
    tasks = Tasks(text=request.form['todoitem'], complete=False, priority=('prioritycheck' in request.form)) 
    db.session.add(tasks) 
    db.session.commit() 
  
    return redirect(url_for('tasks')) 
  
  
@app.route('/tasks/complete/<id>') 
def complete(id): 
  
    tasks = Tasks.query.filter_by(id=int(id)).first() 
    tasks.complete = True
    db.session.commit() 
  
    return redirect(url_for('tasks'))

def formatTime(x):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date = x[:10].split("-")
    resultDate = months[int(date[1])-1] + " " + date[2] + ", " + date[0]
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
    if os.path.exists('token.pickle'):
        with  open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in

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
    now = datetime.datetime(2020, 9, 22,8, 0,00).isoformat() + 'Z' #datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    tmax = datetime.datetime(2020, 9, 22, 22, 0,00).isoformat() +'Z'#(datetime.datetime.utcnow()+ datetime.timedelta(hours =24)).isoformat() +'Z'
    print('Getting events from next 24 hours')
    print(now,tmax)
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
    print(event_list)
    for i in range(len(event_list)):
        randomStart = events[i]['start'].get('dateTime', events[i]['start'].get('date'))
        randomEnd = events[i]['end'].get('dateTime', events[i]['end'].get('date'))
        msg = randomStart+";"+randomEnd 
        cale = Calen(text=str(event_list[i][2]),eventss=(msg)) 
        db.session.add(cale) 
        db.session.commit()

    #pull one event only from calendar
    """randomStart = events[1]['start'].get('dateTime', events[1]['start'].get('date'))
    randomEnd = events[1]['end'].get('dateTime', events[1]['end'].get('date'))
    msg = randomStart+";"+randomEnd 
    fout = open('input.txt', 'w')
    fout.write(msg)
    fout.close()"""

    
    return  render_template("cal.html", events=event_list)

@app.route("/makecal")
def makecal():
    import studyBlockAlgorithm
    from studyBlockAlgorithm import msgs
    print(msgs)
    return render_template('makecal.html')

    
if  __name__  ==  "__main__":
    db.create_all()
    app.run(debug=True)