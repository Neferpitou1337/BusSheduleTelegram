from datetime import datetime
import RefreshDB
from enum import Enum

class Weekdays(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

def getTime(weekdayTime, weekendTime):
    timeTable = weekendTime if datetime.today().weekday() in (Weekdays.SATURDAY.value, Weekdays.SUNDAY.value) else weekdayTime
    if timeTable == '-':
        return "Сегодня такого маршрута нет"
    # проверка на автобусы с раб + суб
    if weekendTime.find("субб") > 0 and datetime.today().weekday() == Weekdays.SUNDAY.value:
        return "Сегодня такого маршрута нет"

    timeTable= RefreshDB.cutStringToFirstNum(timeTable)

    now = str(datetime.today().time().hour) + ':' + str(datetime.today().time().minute)

    times = timeTable.split(" - ")




    # организовываю цикличность проходя все возможные случаи
    if now>times[-1]:
        if datetime.today().weekday() == Weekdays.FRIDAY.value:
            if weekendTime =='-':
                return "в пн " + times[0]
            we = (RefreshDB.cutStringToFirstNum(weekendTime)).split(" - ")
            return we[0]

        elif datetime.today().weekday() == Weekdays.SATURDAY.value and weekendTime.find("субб")>0:
            return "в пн " + times[0]

        elif datetime.today().weekday() == Weekdays.SUNDAY.value:
            wd = (RefreshDB.cutStringToFirstNum(weekdayTime)).split(" - ")
            return wd[0]
        else:
            return times[0]

    for t in times:
        if t>=now:
            return t