from datetime import datetime
import RefreshDB


def getTime(weekdayTime, weekendTime):
    timeTable = RefreshDB.cutStringToFirstNum([weekendTime if datetime.today().weekday() in (5, 6) else weekdayTime][0])
    if timeTable == '-':
        return "Сегодня такого маршрута нет"

    now = str(datetime.today().time().hour) + ':' + str(datetime.today().time().minute)

    times = timeTable.split(" - ")

    # организовываю цикличность проходя все возможные случаи
    if now>times[-1]:
        if datetime.today().weekday() == 4:
            if weekendTime =='-':
                return "в пн " + times[0]
            we = (RefreshDB.cutStringToFirstNum(weekendTime)).split(" - ")
            return we[0]

        elif datetime.today().weekday() == 5 and weekendTime.find("субб")>0:
            return "в пн " + times[0]

        elif datetime.today().weekday() == 6:
            wd = (RefreshDB.cutStringToFirstNum(weekdayTime)).split(" - ")
            return wd[0]
        else:
            return times[0]

    for t in times:
        if t>=now:
            return t