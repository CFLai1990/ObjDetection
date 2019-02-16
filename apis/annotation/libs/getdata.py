import csv
import os
colorFile = os.path.abspath('../data/color_name.csv')

def getColor():
  colorDict = []
  with open(colorFile, newline='') as csvfile:
    print('OPENED!!!')
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
      print(row['l'] + ', '+ row['a'] + ', '+ row['b'] + ': '+ row['name'])
      colorDict.append(row)
    return colorDict