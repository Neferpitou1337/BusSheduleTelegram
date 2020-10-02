from datetime import datetime
import RefreshDB

def getTime(weekdayTime, weekendTime):
    timeTable = [weekendTime if datetime.today().weekday() in (5, 6) else weekdayTime][0]
    if timeTable == '-':
        return "Today is no given route today"

    now = str(datetime.today().time().hour) + ':' + str(datetime.today().time().minute)

    timeTable = RefreshDB.cutStringToFirstNum(timeTable)
    times = timeTable.split(" - ")

    # организовываю цикличность
    if now>times[-1]:
        return times[0]

    for t in times:
        if t>=now:
            return t
    return "Today is no given route today"