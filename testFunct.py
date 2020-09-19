def formatTime(x):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    days = {"M" : "Mon", "T": "Tue", "W" : "Wed", "Th": "Thu", "F": "Fri", "Sa": "Sat", "Su" : "Sun"}
    date = x[:10].split("-")
    resultDate = days[x[10]] + " " + months[int(date[1])-1] + " " + date[2] + ", " + date[0]
    time = x[11:].split("-")
    resultTime = []
    for t in range(len(time)):
        if time[t][0] == 0:
            resultTime[t] = time[t][:-3] + " AM"
    return resultDate


print(formatTime("2020-09-19T19:00:00-04:00"))