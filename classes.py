# AEGIS - Distribution System Visualization Software
# Creates node and branch classes
# Lucas Manalo
# 9/27/22

class Node:
    def __init__(self, index, label, phases, baseV):
        self.index = index
        self.label = label
        self.phases = phases
        self.baseV = baseV
        self.toBranch = []
        self.fromBranch = []
        self.value = [True, True, True] #Initializes the node to be in service (nodes all in service and phases/voltages all checked) 

class Branch:
    def __init__(self, index, label, type, phases, fromNode, toNode):#, length):
        self.index = index
        self.label = label
        self.type = type
        self.phases = phases
        self.fromNode = fromNode
        self.toNode = toNode
        #self.length = length
        self.value = [True, True] #Initializes the branch to be in service (nodes all in service and phases all checked) 

class Load:
    def __init__(self, index, label, node, phases, model):
        self.index= index
        self.label = label
        self.node= node
        self.phases = phases
        self.model = model

