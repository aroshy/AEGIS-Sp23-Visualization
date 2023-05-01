# AEGIS - Distribution System Visualization Software
# Imports, cleans, and reassigns node and branch data
# 9/27/22

from classes import *

def importData_HH(branchfile, nodefile, housefile):
# Imports and cleans node data
    with open(nodefile, 'r') as nodeFile:
        nodeTxtData = nodeFile.readlines()[2:]

    with open(housefile, 'r') as houseFile:
        houseTxtData = houseFile.readlines()[2:]

# Creates a list of node obejcts
    nodeDict = {} # A dictionary of all of the node objects
    houseDict = {}
    nodeIndDict = {} # A dictionary pointing the node indicies to their names
    for line in nodeTxtData:
        line = line.split()
        #Creates dictionary with node names as keys and objects as values
        nodeDict[str(line[1][:-1])] = Node(int(line[0][:-1]), str(line[1][:-1]), str(line[2][:-1]), float(line[3]))
        nodeIndDict[int(line[0][:-1])] = str(line[1][:-1]) #Creates dict with index as key and name as value

    for line in houseTxtData:
        line = line.split()
        #Creates dictionary with node names as keys and objects as values
        houseDict[str(line[1][:-1])] = Load(int(line[0][:-1]), str(line[1][:-1]), int(line[2][:-1]), str(line[3][:-1]), str(line[4]))
    
# Imports and Cleans Branch Data
    with open(branchfile, 'r') as branchFile:
        branchTxtData = branchFile.readlines()[2:]

    # Creates a list of branch obejcts
    branchDict = {}
    for line in branchTxtData:
        line = line.split()

        if line[6] == "N/A":
            line[6] = 0

        branchDict[line[1][:-1]] = Branch(int(line[0][:-1]), line[1][:-1], line[2][:-1], line[3][:-1], nodeIndDict[int(line[4][:-1])], nodeIndDict[int(line[5][:-1])])#, float(str(line[6]).strip('ft')))
        nodeDict[branchDict[line[1][:-1]].fromNode].toBranch.append(branchDict[line[1][:-1]]) #Assigns branch to proper node object
        nodeDict[branchDict[line[1][:-1]].toNode].fromBranch= branchDict[line[1][:-1]] #Assigns branch to proper node object

    return(nodeDict, branchDict, houseDict)