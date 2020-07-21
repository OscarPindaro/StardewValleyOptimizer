#!/usr/bin/env python
import json
import csv
from math import *
from pulp import *
import sys
from utilities import *

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
"""select only the crops that can grow and will grow completely in the chosen period """
cropList = [crop for crop in cropList if durations[crop.name]>0 and crop.growthTime<=durations[crop.name]]
