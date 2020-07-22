#!/usr/bin/env python
import json
import csv
from math import *
from pulp import *
import sys
from utilities import *

def createCropList(jsonCrops, ignore):
    cropList = []
    for crop in jsonCrops:
        if(ignore[crop.get("name")] != 1):
            x = Crop(crop.get("name"), crop.get("buy"), crop.get("sell"), sum([int(x) for x in crop.get("stages")]))
            if(crop.get("regrow")):
                x.setRegrowTime(crop.get("regrow"))
            x.addSeason(crop.get("seasons"))
            cropList.append(x)
    return cropList

def setDurations(cropList, seasonTuple):
    durations = {}
    """ +1 because the revenue is calculated after 1 day """
    totalDuration = sum(seasonTuple) + 1
    for crop in cropList:
        duration = 0
        if "spring" in crop.seasons:
            duration = duration + springDays
        if "summer" in crop.seasons:
            duration = duration + summerDays
        if "fall" in crop.seasons:
            duration = duration + autumnDays
        durations[crop.name] = duration
    return durations

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

cropList = createCropList(crops, ignore)
# The followings are the input of the program.
# $N$ : the number of available tiles <br>
# $D$ : number of days available <br>
# $M$ : total amount of money available <br>

if len(sys.argv) != 6:
    print("Not enough arguments. Write starting date and ending date")
    print('"start date" "end date" money tiles delta')
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
M = int(sys.argv[3])
#number of money available
N = int(sys.argv[4])
#percentage to keep after obtaining a revenue
delta = float(sys.argv[5])

#duration of each crops
durations = setDurations(cropList, res)
totalDuration = sum(res)+1


#removing all the crops with duration equal to 0
"""select only the crops that can grow and will grow completely in the chosen period """
cropList = [crop for crop in cropList if durations[crop.name]>0 and crop.growthTime<=durations[crop.name]]

"""Need to find the first and last day its active"""
lowerDate = {}
upperDate = {}
for crop in cropList:
    if "spring" in crop.seasons:
        lowerDate[crop.name] = 0
    elif "summer" in crop.seasons:
        lowerDate[crop.name] = springDays
    else:
        lowerDate[crop.name] = springDays + summerDays

    upperDate[crop.name] = lowerDate[crop.name] + durations[crop.name]


"""Now variables"""
"""First of all amounts. check if the number of varibales can be lowered"""
amounts = {}
for crop in cropList:
    for day in range(0, totalDuration):
        amounts[(crop.name, day)] = LpVariable("{}_{:02d}".format(crop.name, day),0, cat="Integer")

"""Costs at every day"""
costs = {}
for day in range(0,totalDuration):
    costs[day] = lpSum([amounts[(crop.name,day)]*crop.buyCost for crop in cropList])

"""auxiliary variable for the daily revenue. It tells how much plants planted at day day
of type crop.name will generate revenue at day k"""

a = {}
for crop in cropList:
    for day in range(0, totalDuration):
        for k in range(0, totalDuration):
            if crop.regrow == -1:
                if k == day + crop.growthTime:
                    a[(crop.name, day, k)] = amounts[(crop.name, day)]
                else:
                    a[(crop.name, day, k)] = 0
            else:
                firstRevenue = day + crop.growthTime
                """the condition >0 is necessary, in this way i set to 0 all the  variables
                before the first firstRevenue. The first condition ensures that i'm considering
                multiples of the regrowth time"""
                if (k - firstRevenue) % crop.regrow == 0 and k > firstRevenue and k in range(lowerDate[crop.name], upperDate[crop.name]):
                    a[(crop.name, day, k)] = amounts[(crop.name, day)]
                else:
                    a[(crop.name, day, k)] = 0;


"""daily revenues, asuumes that the goods are sold today, but the revenue will be
generated the day after (shipping bin functionality)"""
dailyRevenues ={}
for day in range(0, totalDuration):
    if day == 0:
        dailyRevenues[0] = 0
    else:
        dailyRevenues[day] =  lpSum([crop.sellCost*a[(crop.name, j, day-1)]for crop in cropList for j in range(0, day)])



"""Utilizable revenue, since some money could be kept aside"""
utilizableRevenue ={}
for day in range(0, totalDuration):
    utilizableRevenue[day] = (1-delta)*dailyRevenues[day]
"""money is remainig money after all costs and revenues of that day"""
money = {}
for day in range(0, totalDuration):
    if day == 0:
        money[day] = M - costs[day]
    else:
        money[day] = money[day-1]+utilizableRevenue[day]-costs[day]
"""Auxiliary variable used to know how much tiles are available a given day"""
b = {}
for crop in cropList:
    for day in range(0, totalDuration):
        for k in range(0, totalDuration):
            if crop.regrow > 0:
                """per adesso lo faccio così ma non considera che ad una certa le togli
                ste piante, perchè finisce la loro stagione. Problema anche negli altri"""
                if (k >= day and k <= upperDate[crop.name]):
                    b[(crop.name, day, k)] = amounts[(crop.name, day)]
                else:
                    b[(crop.name, day, k)] = 0
            else:
                if(k >= day and k < day+crop.growthTime):
                    b[(crop.name, day, k)] = amounts[(crop.name, day)]
                else:
                    b[(crop.name, day, k)] = 0
"""tiles occupied"""
t = {}
for day in range(0, totalDuration):
    t[day] = lpSum([b[(crop.name, k, day)] for crop in cropList for k in range(0, day+1)])

prob = LpProblem("ProfitMaximization", LpMaximize)

"""Maximization function, maximize profit"""
prob += lpSum([dailyRevenues[day] - costs[day] for day in range(0, totalDuration)])

"""TILE AVAILABILITY"""
for day in range(0, totalDuration):
    prob += t[day] <= N

"""Time horizone constraint already done at the begining of the script. FORSE DEVO FARLO
PER QUELLI CHE POSSONO IN PRIMAVERA MA NON IN ESTATE"""

"""TOTAL COST CONSTRAINT"""
for day in range(0, totalDuration):
    prob += money[day] >= 0

"""LAST DAY CONSTRAINT: the last day is considered only for the profit, there is no revenue"""
for crop in cropList:
    for day in range(0,totalDuration):
        a[(crop.name, day, totalDuration-1)] = 0

"""SEASONALITY CONSTRAINT: a plant can be planted only in its season """
for crop in cropList:
    for day in range(0, totalDuration):
        if( day < lowerDate[crop.name] or day >= upperDate[crop.name]):
            prob += amounts[(crop.name, day)] == 0


status = prob.solve(PULP_CBC_CMD(timeLimit=10))

#print(prob)

print("Status:", LpStatus[prob.status])
print("spring days =", springDays)
print("summer days =", summerDays)
print("autumn days =", autumnDays)
print("total number of days =", springDays+summerDays+autumnDays)
print("Starting Money =", M, "Money Spent =", sum([costs[i].value() for i in costs]) )
print("Tiles = {}".format(N))
print("Profit = {}".format(prob.objective.value()))

vars = [amounts[(crop.name, day)] for crop in cropList for day in range(0, totalDuration)]
print()
for day in range(0, totalDuration):
    if sum([amounts[(crop.name, day)].value() for crop in cropList]) > 0:
        print("{}".format(numberToDate( start_date ,day)))
        for crop in cropList:
            if amounts[(crop.name, day)].value() >0:
                print("{} = {}, harvest at {}".format(crop.name, amounts[(crop.name, day)].value(), numberToDate(numberToDate(start_date, day), crop.growthTime)))
                print(crop.seasons)
        print()

print(numberToDate(start_date,0))
print(numberToDate(start_date,27))
print(convertDate(start_date))
