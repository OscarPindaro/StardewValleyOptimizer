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

    if 28 in range(dayStart, dayEnd):
        endMonth.append(28)
    if 56 in range(dayStart, dayEnd):
        endMonth.append(56)

    if len(endMonth) == 0:
        if dayStart<=28:
            springDays = dayEnd -dayStart+1
        elif dayStart in range(29, 57):
            summerDays =  dayEnd -dayStart+1
        else:
            autumnDays = dayEnd -dayStart+1

    elif 28 in endMonth:
        springDays = 28 - dayStart +1
        if 56 in endMonth:
            summerDays = 28
            autumnDays = dayEnd - 57 + 1
        else:
            summerDays = dayEnd - 29 +1
            autumnDays = 0;
    else:
        springDays=0;
        if 56 in endMonth:
            summerDays = 56 - dayStart +1
            autumnDays = dayEnd - 57 + 1
        else:
            summerDays =  dayEnd -dayStart+1

    return (springDays, summerDays, autumnDays)


def convertDate(date):
    splitted = date.split(" ")
    day = int(splitted[0])
    if "spring"  == splitted[1].lower():
        day = day +0;
    elif "summer" == splitted[1].lower():
        day = day + 28
    else:
        day = day +56
    return day    
