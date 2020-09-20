## This algorithm takes in one busy event from a calendar, start and end times of a workday, and the number of tasks needed to be done 

## It returns a list of tuples of studyblocks 

## You can vary start and end times of a workday, and the number of tasks needed to be done. 

## It doesn't work w/ more than one busy event though. (not implemented)

#########################################
#########################################
# Here are the parameters we can change #  

# assume we have schedule start/end times
#2020-09-20T13:00:00-04:00 2020-09-20T14:00:00-04:00 SI
import os
from hello import app
from hello import db
from hello import Tasks
from hello import Calen

fin = Calen.query.all()
busyTimes=[]
for i in fin:
  busyTimes.append(i.eventss)
print(busyTimes)
#busyTimes = fin.readlines()

#tasks variables #add more entries!
tin = Tasks.query.filter_by(complete=False).all()
taskNames = []
#j=0
for i in tin:
  taskNames.append(i.text)
print (taskNames)
print (busyTimes)
#taskNames = ["stem homework", "hum homework"]

#plan to work between these times 
startTime = (8,0)
endTime = (22, 0)
######################################### 
######################################### 

formTimes = [0]*len(busyTimes)
for t in range(len(busyTimes)):
  temp = busyTimes[t].split(";")
  print(temp)
  formTimes[t] = (temp[0][11:16], temp[1][11:16])

#print(formTimes) #EST 

#convert formTimes to floats ?
#assume times are ints
def getIntTimes(startTime):
  hours, minutes = (int(startTime[:2]), int(startTime[-2:]))
  return hours, minutes

for t in range(len(formTimes)):
  formTimes[t] = (getIntTimes(formTimes[t][0]), getIntTimes(formTimes[t][1]))

#print(formTimes)

#tasks variables 
#taskNames = ["stem homework", "hum homework"]

#plan to work between these times 
#startTime = (8,0)
#endTime = (22, 0)
#current = [8, 0]
current = [startTime[0], startTime[1]]
toDo = len(formTimes)
calendarTime = [(startTime, endTime)]

emptyTimes = []

#assume formTimes is in order
#formTimes[0] = (13,0), (14,0)
#formTimes[0][0] = (13,0)
#formTimes[0][1] = (14,0) 
while current[0] < endTime[0]:
  if current[0] == formTimes[len(formTimes)-toDo][0][0]:
    if current[1] == formTimes[len(formTimes)-toDo][0][1]:
      current[0] = formTimes[len(formTimes)-toDo][1][0]
      current[1] = formTimes[len(formTimes)-toDo][1][1]
      toDo -= 1
    else:
      emptyTimes.append(((current[0],current[1]), (current[0], formTimes[len(formTimes)-toDo][0][1])))
      current[1] = formTimes[len(formTimes)-toDo][0][1]
  else:
    emptyTimes.append(((current[0],current[1]), (formTimes[len(formTimes)-toDo][0][0], formTimes[len(formTimes)-toDo][0][1])))
    current[0] = formTimes[len(formTimes)-toDo][0][0]
    current[1] = formTimes[len(formTimes)-toDo][0][1]
  if toDo == 0:
    emptyTimes.append(((current[0], current[1]),(endTime[0], endTime[1])))
    current[0] = endTime[0]
    current[1] = endTime[1]

#print(emptyTimes)

totalEmptyTime = 0
for i in emptyTimes:
  diffHours = int(i[1][0]) - int(i[0][0])
  diffMinutes = (int(i[0][1]) - int(i[1][1]))/60
  totalEmptyTime+= diffHours+diffMinutes

timePerTask = totalEmptyTime / len(taskNames)
#print(totalEmptyTime)
#print(timePerTask)
hourPerTask = int(timePerTask)
minPerTask = int((timePerTask - hourPerTask)*60)

#####################

studyBlocks = []
tasksAppended = 0
emptyTimeIndex = 0
myStart = emptyTimes[emptyTimeIndex][0]
myEnd = emptyTimes[emptyTimeIndex][1]
#print(myStart, myEnd)
leftoverTime = 0
while tasksAppended<len(taskNames):
    #calculating total time for the interval
    hrs = int(myEnd[0]) - int(myStart[0])
    mins = (int(myEnd[1]) - int(myStart[1]))/60
    intervalTime = hrs + mins
    remainingTime = timePerTask - intervalTime - leftoverTime
    #print("interval", emptyTimeIndex,":",intervalTime)
    #print("leftover ",leftoverTime)
    #print("remainingTime ",remainingTime)
    if remainingTime == 0:
      leftoverEndHour = int(leftoverTime)
      leftoverEndMin = (leftoverTime-leftoverEndHour)*60
      leftoverEndTime = (leftoverEndHour, leftoverEndMin)
      studyBlocks.append((myStart, leftoverEndTime))
      studyBlocks.append((leftoverEndTime, myEnd))
      if leftoverTime!=0:
        tasksAppended+=1
      tasksAppended+=1

      if(emptyTimeIndex<len(emptyTimes)):
        emptyTimeIndex+=1
        myStart = emptyTimes[emptyTimeIndex][0]
        myEnd = emptyTimes[emptyTimeIndex][1]
      #print("remainingTime is 0")
      #print(myStart, myEnd)
      leftoverTime = 0
    
    elif remainingTime < 0: #there is some interval left 
      if emptyTimeIndex==0:
        studyEndHours = hourPerTask +myStart[0]
        studyEndMins = minPerTask +myStart[1]
        newEnd = (studyEndHours, studyEndMins)
        studyBlocks.append((myStart, newEnd))
        tasksAppended+=1
        myStart = newEnd
        #print('myStart', myStart)

      else:
        studyEndHours = hourPerTask +myStart[0]
        studyEndMins = minPerTask +myStart[1]

        #make sure the study hours and mins make sense
        while studyEndMins>60:
          studyEndMins-=60
          studyEndHours+=1

        leftoverEndHour = int(leftoverTime)
        leftoverEndMin = int((leftoverTime-leftoverEndHour)*60)

        leftoverEndHour += int(myStart[0])
        leftoverEndMin += int(myStart[1])

        while leftoverEndMin>60:
          leftoverEndMin-=60
          leftoverEndHour+=1
      
        leftoverEndTime = (leftoverEndHour, leftoverEndMin)
        #print("leftoverEndTime", leftoverEndTime)

        studyBlocks.append((myStart, leftoverEndTime))

        studyBlocks.append((leftoverEndTime, myEnd))
      
        if leftoverTime!=0:
          tasksAppended+=1
        tasksAppended+=1

        newEnd = (studyEndHours, studyEndMins)
        myStart = newEnd
        #print('myStart', myStart)
      
        leftoverTime = 0
    
    else: #timePerTask > time interval length 
      studyBlocks.append((myStart, myEnd))
      if(emptyTimeIndex<len(emptyTimes)):
        emptyTimeIndex+=1
        myStart = emptyTimes[emptyTimeIndex][0]
        myEnd = emptyTimes[emptyTimeIndex][1]
      #print("remainingTime > 0")
      #print(myStart, myEnd)
      leftoverTime = remainingTime

#newStudyBlocks = []
#for i in studyBlocks:
#  if i[0]!=i[1]:
#    newStudyBlocks.append(i)
print("here are your study blocks")
print(studyBlocks)
#print('done')

#print(newStudyBlocks) #done! 

###############################################
#  Adjust the studyblock periods              #
# to have 10 minutes in between each one      #
###############################################
''''
adjustedStudyBlocks = []

for i in studyBlocks: #i is the study block period 
  start = i[0] #start time 
  startHours = i[0][0] #start time hours 
  startMinutes = i[0][1] #start time minutes   

  newStartMinutes = int(startMinutes)+5
  newStartHours = int(startHours)

  while newStartMinutes>60:
    newStartMinutes-=60
    newStartHours+=1

  newStart = (newStartHours, newStartMinutes)

  end = i[1] #end time 
  endHours = i[1][0] #end time hours 
  endMinutes = i[1][1] #end time minutes 

  newEndMinutes = int(endMinutes)-5
  newEndHours = int(endHours)

  while newEndMinutes<0:
    newEndMinutes+=60
    newEndHours-=1

  newEnd = (newEndHours, newEndMinutes)

  adjustedStudyBlock = (newStart, newEnd)
  adjustedStudyBlocks.append(adjustedStudyBlock)

#print('here are your adjusted study blocks')
#print(adjustedStudyBlocks)
'''
####################################################
# functions for finding studyblocks w/ breaks
####################################################
# vers. 1 
# break times: 
# breakLength/2 minutes before the end of the day and before calendar events 
# breakLength/2 minutes after the start of the day 
# breakLength minutes in between studyblocks 
def adjustStudyBlocks1(studyBlockList, breakLength):
    adjustedStudyBlocks = []
    for i in studyBlockList: #i is the study block period 
      #start = i[0] #start time 
      startHours = i[0][0] #start time hours 
      startMinutes = i[0][1] #start time minutes   

      newStartMinutes = int(startMinutes)+ int(breakLength/2)
      newStartHours = int(startHours)

      while newStartMinutes>60:
        newStartMinutes-=60
        newStartHours+=1

      newStart = (newStartHours, newStartMinutes)

      #end = i[1] #end time 
      endHours = i[1][0] #end time hours 
      endMinutes = i[1][1] #end time minutes 

      newEndMinutes = int(endMinutes)-int(breakLength/2)
      newEndHours = int(endHours)

      while newEndMinutes<0:
        newEndMinutes+=60
        newEndHours-=1

      newEnd = (newEndHours, newEndMinutes)

      adjustedStudyBlock = (newStart, newEnd)
      adjustedStudyBlocks.append(adjustedStudyBlock)
    return adjustedStudyBlocks  

# vers. 2 
# break times: 
# breakLength minutes after the start of the day and before the end of the day 
# breakLength minutes in between studyblocks and calendar events
def adjustStudyBlocks2(studyBlockList, breakLength):
    adjustedStudyBlocks = []
    firstBlock = studyBlockList[0]
    for i in studyBlockList: #i is the study block period 
      #start = i[0] #start time 
      startHours = i[0][0] #start time hours 
      startMinutes = i[0][1] #start time minutes  

      if i==firstBlock: #break after start of day 
        newStartMinutes = int(startMinutes)+ int(breakLength)
        newStartHours = int(startHours)
      

        while newStartMinutes>60:
          newStartMinutes-=60
          newStartHours+=1

        newStart = (newStartHours, newStartMinutes)
      else:
        newStart = (startHours, startMinutes)

      #end = i[1] #end time 
      endHours = i[1][0] #end time hours 
      endMinutes = i[1][1] #end time minutes 

      newEndMinutes = int(endMinutes)-int(breakLength)
      newEndHours = int(endHours)

      while newEndMinutes<0:
        newEndMinutes+=60
        newEndHours-=1

      newEnd = (newEndHours, newEndMinutes)

      adjustedStudyBlock = (newStart, newEnd)
      adjustedStudyBlocks.append(adjustedStudyBlock)
    return adjustedStudyBlocks  

print("one way to have breaks in between blocks")
print(adjustStudyBlocks1(studyBlocks, 10))

print("another way to have breaks in between blocks")
print(adjustStudyBlocks2(studyBlocks, 10))
msgs = adjustStudyBlocks2(studyBlocks, 10)