#!/usr/bin/env python

import json
import csv
from math import *
from pulp import *
import sys

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


csvFile = open("resources/userPreferences.csv")

csvReader = csv.DictReader(csvFile)


#assumptio: the name in the csv and the json are the same
#list of plants that need to be ignored
ignore = {}
minCrops = {}
maxCrops = {}
for row in csvReader:
    ignore[row["name"]] = int(row["ignore"])
    minCrops[row["name"]] = int(row["min"])
    maxCrops[row["name"]] = int(row["max"])


jsonFile = open("resources/stardewConfig.json", "r")
data = json.load(jsonFile)

crops = data.get("crops")

cropList = []
for crop in crops:
    if(ignore[crop.get("name")] != 1):
        x = Crop(crop.get("name"), crop.get("buy"), crop.get("sell"), sum([int(x) for x in crop.get("stages")]))
        if(crop.get("regrow")):
            x.setRegrowTime(crop.get("regrow"))
        x.addSeason(crop.get("seasons"))
        cropList.append(x)
        #print(x)
        #print("\n")

# The followings are the input of the program.
# $N$ : the number of available tiles <br>
# $D$ : number of days available <br>
# $M$ : total amount of money available <br>

if len(sys.argv) !=5:
    print("Not enough arguments. Write starting date and ending date")
    print('"start date" "end date" money tiles')
    quit()

start_date=sys.argv[1]
end_date = sys.argv[2]

dayStart = convertDate(start_date)
dayEnd = convertDate(end_date)




if( dayStart >= dayEnd):
    print("start day after end day, does not make any sense")
    quit()


#assigns the different duration of the seasons
res =assignDays(dayStart, dayEnd)
springDays = res[0]
summerDays = res[1]
autumnDays = res[2]

#number of tiles available
N = int(sys.argv[4])
#number of money available
M = int(sys.argv[3])

#duration of each crops
durations = {}
for crop in cropList:
    duration = 0
    if "spring" in crop.seasons:
        duration = duration + springDays
    if "summer" in crop.seasons:
        duration = duration + summerDays
    if "fall" in crop.seasons:
        duration = duration + autumnDays
    durations[crop.name] = duration

#removing all the crops with duration equal to 0
for crop in cropList:
    print(crop.name, durations[crop.name])

print()
"""select only the crops that can grow and will grow completely in the chosen period """
cropList = [crop for crop in cropList if durations[crop.name]>0 and crop.growthTime<=durations[crop.name]]
for crop in cropList:
    print(crop.name)

#alpha, number of times i will harvest the colture
alpha= {}
for crop in cropList:
    if crop.regrow == -1:
        alpha[crop.name] =1
    else:
        """ho un crop che ci mette 6 giorni a crescere (primo profitto ai 6 giorni) e cresce ogni 2 giorni
            orizzTemp=6   (6-6)/2=0 + 1
            orizzTemp=9   profitto= 6, 8, (9-6)/2= 1 + 1
            """
        alpha[crop.name] = floor((durations[crop.name]-crop.growthTime)/crop.regrow) + 1

variables = {}
for crop in cropList:
    variables[crop.name]= LpVariable(crop.name, 0, cat="Integer")

prob = LpProblem("ProfitMaximization", LpMaximize)

# *maximize* $\pi = \sum_{i \in P}\alpha_{i} r_{i}x_{i} - \sum_{i \in P}c_{i}x_{i}$
prob += lpSum([alpha[x.name]*x.sellCost*variables[x.name] for x in cropList])
-lpSum([x.buyCost*variables[x.name] for x in cropList])


# **tile availablity**
prob += lpSum([variables[x.name] for x in cropList]) <= N

# **time horizon constraint**
#this sould be taken care by previous lines, that excluded all the coluters
# for crop in cropList:
#     if(crop.growthTime > D):
#         prob += variables[crop.name] == 0


# **total cost constraint**
prob += lpSum([x.buyCost*variables[x.name] for x in cropList]) <= M

# diversitifcation constraint
#at least constraint
for x in cropList:
    if(minCrops[x.name] >= 0):
        """ per ogni xi, xi > min(xi)  # devo avere almeno min(xi) della i-esima coltura"""
        prob += variables[x.name] >= minCrops[x.name]
#at most constraint
for x in cropList:
    if(maxCrops[x.name] >=0):
        prob += variables[x.name] <= maxCrops[x.name]

status = prob.solve()

print(prob)

print("Status:", LpStatus[prob.status])
print("spring days =", springDays)
print("summer days =", summerDays)
print("autumn days =", autumnDays)
print("total number of days =", springDays+summerDays+autumnDays)
print("Money =", M, "; Money spent:", sum([x.buyCost*value(variables[x.name])     for x in cropList] ))
print("Tiles =", N)

print("\nSOLUTION")
for v in prob.variables():
    if value(v)> 0:
        print(v.name,"=", value(v))

print("profit =",value(prob.objective))
