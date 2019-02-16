import csv
import os
colorFile = os.path.abspath('./apis/annotation/data/color_name.csv')

def getColor():
  colorDict = []
  with open(colorFile, newline='') as csvfile:
    print('OPENED!!!')
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
      print(row.items())
      colorDict.append(row)
    return colorDict