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


print(formatTime("2020-09-20T11:00:00-04:00"))