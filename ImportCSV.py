# AEGIS - Distribution System Visualization Software
# Imports data from .csv

import csv

def csvRead(f):
  nodesNames = []

  with open(f, 'r') as file: #Opens File
    csvreader = csv.reader(file)
    row_count = 0 
    data = []

    for j, row in enumerate(csvreader): #Indexes through rows of the csv

      #Each row is a time instance across all objects in csv

      row_count = row_count + 1
      if (j == 8): #Where all names are
        nodesNames = row
      if (j >= 9): #Where data is
        data.append(row)

  file.close()
  return(nodesNames, data)


