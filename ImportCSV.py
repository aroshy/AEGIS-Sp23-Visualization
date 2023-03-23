import csv

def csvRead(f):
  nodesNames = []
  with open(f, 'r') as file:
    csvreader = csv.reader(file)
    row_count = 0 
    data = []
    for j, row in enumerate(csvreader):
      row_count = row_count + 1
      if (j == 8):
        nodesNames = row
      if (j >= 9):
        data.append(row)
  file.close()
  return(nodesNames, data)


