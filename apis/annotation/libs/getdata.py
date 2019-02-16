import csv
import os
colorFile = os.path.abspath('./apis/annotation/data/color_name.csv')

def getColor():
  colorDict = []
  with open(colorFile, newline='', encoding='UTF-8-sig') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
      colorDict.append(row)
    return colorDict