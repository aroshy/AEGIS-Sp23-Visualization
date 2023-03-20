import csv
nodesNames = []
with open("R2_1247_3_t11_ResidentialVoltages_new.csv", 'r') as file:
  csvreader = csv.reader(file)
  row_count = 0 
  data = []
  for j, row in enumerate(csvreader):
    row_count = row_count + 1
    if (j == 8):
      nodesNames = row
    if (j >= 9):
      data.append(row)
    #print(row_count)
print(nodesNames[0:20])
print(data[1][0:20])
