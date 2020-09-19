def formatTime(x):
    months = ["Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec"]
    date = x[:10].split("-")
    result = months[int(date[1])] + " " + date[2] + ", " + date[0]

    return result


print(formatTime("2020-09-19T19:00:00-04:00"))