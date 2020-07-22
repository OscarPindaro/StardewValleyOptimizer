class Crop:

    def __init__(self, name, buyCost, sellCost, growthTime):
        self.name = name
        self.buyCost = buyCost
        self.sellCost=sellCost
        self.growthTime = growthTime
        self.seasons = []
        self.regrow=-1

    def addSeason(self, season):
        self.seasons= self.seasons +(season)

    def setRegrowTime(self, regrow):
        self.regrow = regrow;

    def __str__(self):
        stringa ="Name={}\nBuy={}\nSell={}\ngrothTime={}".format(self.name, self.buyCost, self.sellCost, self.growthTime)
        if(self.regrow != -1):
            stringa= stringa +("\nregrow=" + str(self.regrow))
        stringa = stringa + "\nseasons:" + str(self.seasons)
        return stringa

def assignDays(dayStart, dayEnd):
    endMonth = []
    springDays = 0
    summerDays = 0
    autumnDays =0

    if 27 in range(dayStart, dayEnd):
        endMonth.append(27)
    if 55 in range(dayStart, dayEnd):
        endMonth.append(55)

    if len(endMonth) == 0:
        if dayStart<=27:
            springDays = dayEnd -dayStart+1
        elif dayStart in range(28, 56):
            summerDays =  dayEnd -dayStart+1
        else:
            autumnDays = dayEnd -dayStart+1

    elif 27 in endMonth:
        springDays = 27 - dayStart +1
        if 55 in endMonth:
            summerDays = 28
            autumnDays = dayEnd - 56 + 1
        else:
            summerDays = dayEnd - 28 +1
            autumnDays = 0;
    else:
        springDays=0;
        if 55 in endMonth:
            summerDays = 55 - dayStart +1
            autumnDays = dayEnd - 56 + 1
        else:
            summerDays =  dayEnd -dayStart+1

    return (springDays, summerDays, autumnDays)


def convertDate(date):
    splitted = date.split(" ")
    day = int(splitted[0])
    if "spring"  == splitted[1].lower():
        day = day +0 -1;
    elif "summer" == splitted[1].lower():
        day = day + 28 -1
    else:
        day = day +56 -1
    return day

def numberToDate(start_date, dayNumber):
    startNum = convertDate(start_date)
    today = startNum + dayNumber
    day = int(today%28)
    month = int(today / 28)
    if month == 0:
        return str(day+1) + " Spring"
    elif month == 1:
        return str(day+1) + " Summer"
    elif month >=2:
        return str(day+1) + " Fall"
    else:

        print("Errroreeeee month={}".format(month))
        quit()
