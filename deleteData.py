# AEGIS - Distribution System Visualization Software
# Makes new .txt file based on deleted nodes

from classes import *

def deleteData(filename, nFile, delNameList):
    with open(filename, 'r') as fo:
        currentData= fo.readlines() #Takes in current file data for reference
        fo.close()
    with open(nFile, 'w') as fo:
        #Keeps initial lines
        fo.write(currentData[0])
        fo.write(currentData[1].strip())
        for data in currentData[2:]: #counts up as the function cycles through lines
            vals = data.split() #Splits each line into a list
            if str(vals[1][:-1]) not in delNameList: #sees if name should be removed
                fo.write('\n' + data.strip()) #Writes node
        fo.close()
