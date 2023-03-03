
import csv
'''
with open("R2_1247_3_t11_ResidentialVoltages_new.csv", 'r') as file:
  csvreader = csv.reader(file)
  row_count = sum(1 for row in csvreader)
  y = []
  for index, row in enumerate(csvreader):
    for x in range(9, row_count):
      if index == x:
        y.append(row[1])
        #print(row[1])

print(row_count)
'''
with open("R2_1247_3_t11_ResidentialVoltages_new.csv", 'r') as file:
  csvreader = csv.reader(file)
  #row_count = sum(1 for row in csvreader)
  #col_count = 
  y = []
  x = []
  n = 0
  for index, row in enumerate(csvreader):
      for n in range(0, 100):
        if index == 8:
          y.append(row[n])
        if index == 9:
          x.append(row[n])
          n = n + 1
  #for index, row in enumerate(csvreader):
print(y[0])
print(x[0])
