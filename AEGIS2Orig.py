# AEGIS - Distribution System Visualization Software
# Visual tool for visualizing data
# 9/25/22

# Internal Imports
from deleteData import *
from Data_to_Node import *
from constants import *
from classes import *
import itertools
from deletionAlg import deletionAlg
from AEGIS_select import selectPhase, selectVolt
import pandas as pd
import networkx
from bokeh.models import Range1d, Circle, MultiLine, \
    NodesAndLinkedEdges, HoverTool, Div, Button, LinearColorMapper, ColorBar, TapTool
from bokeh.plotting import figure, curdoc
from bokeh.plotting import from_networkx
from bokeh.models import NodesAndLinkedEdges, CheckboxGroup, CustomJS, AutocompleteInput, Slider, RadioButtonGroup, ColumnDataSource
from importData_HH import importData_HH
from bokeh.layouts import row, column
from ImportCSV import *
from nodeNormalize import *

# Import Constant Data
feederName = "Feeder_1_Solar_5"
nodeData, branchData, loadData = importData_HH(feederName + '_mod_branch_data.txt', feederName + '_mod_node_data.txt', feederName + '_mod_load_data.txt') #puts node information into corresponding class type in dictionary

#gets name of node which load feeds off of
for i in loadData.keys():
    loadData[i].node = data_to_node(nodeData, i)
   
# Import Data over Time, instsa are the estimated voltage at each instance
longNames, insts = csvRead(feederName + '_ResidentialVoltages.csv')
longNodeNames, nodeInsts = csvRead(feederName + '_node_voltage_a.csv')
longNN2, bNodeInsts = csvRead(feederName + '_node_voltage_b.csv')
longNN3, cNodeInsts = csvRead(feederName + '_node_voltage_c.csv')
longTripNames, tripInsts = csvRead(feederName + '_triplex_node.csv')

# Removes blank/uneeded data from names
longNames = longNames[1:]
longNodeNames = longNodeNames[1:]
longTripNames = longTripNames[1:]

times = [] # All times where data is recorded

# Puts times in order and sorts data points by object
for i in range(len(insts)):
    times.append(insts[i][0]) #Creates list of times in order from csv
    insts[i] = insts[i][1:] # Insts is a list of lists, where each inner list is all data recorded for objects at point in time

#Creates list of the measured voltages
nodeMeasVol = []
nodeMeasVolB = []
nodeMeasVolC = []
for i in range(len(nodeInsts)):
    nodeMeasVolList = []
    nodeMeasVolListB = []
    nodeMeasVolListC = []
    nodeInsts[i] = nodeInsts[i][1:]
    bNodeInsts[i] = bNodeInsts[i][1:]
    cNodeInsts[i] = cNodeInsts[i][1:]

    #Finds magnitude of complex voltages
    for j in range(len(nodeInsts[i])):
        nodeInsts[i][j] = complex(nodeInsts[i][j])
        bNodeInsts[i][j] = complex(bNodeInsts[i][j])
        cNodeInsts[i][j] = complex(cNodeInsts[i][j])
        nodeMeasVolList.append(complex(nodeInsts[i][j]))
        nodeMeasVolListB.append(complex(bNodeInsts[i][j]))
        nodeMeasVolListC.append(complex(cNodeInsts[i][j]))
        nodeInsts[i][j] = ((nodeInsts[i][j].real**2 + nodeInsts[i][j].imag**2)**0.5)
        bNodeInsts[i][j] = ((bNodeInsts[i][j].real**2 + bNodeInsts[i][j].imag**2)**0.5)
        cNodeInsts[i][j] = ((cNodeInsts[i][j].real**2 + cNodeInsts[i][j].imag**2)**0.5)
    nodeMeasVol.append(nodeMeasVolList)
    nodeMeasVolB.append(nodeMeasVolListB)
    nodeMeasVolC.append(nodeMeasVolListC)

tripMeasVol = []
for i in range(len(tripInsts)):
    tripMeasVolList = []
    tripInsts[i] = tripInsts[i][1:]
    for j in range(len(tripInsts[i])):
        tripInsts[i][j] = complex(tripInsts[i][j].replace('i', 'j'))
        tripMeasVolList.append(tripInsts[i][j])
        tripInsts[i][j] = ((tripInsts[i][j].real**2 + tripInsts[i][j].imag**2)**0.5)
    tripMeasVol.append(tripMeasVolList)

shName = [] #Initializes for short names
dataDict = {} #empty dictionary for data
aDataDict = {}
bDataDict = {}
cDataDict = {}
unNormData= {}
aUnNorm = {}
bUnNorm = {}
cUnNorm = {}
for i in longNames:
    if data_to_node(nodeData, i):
        shName.append(data_to_node(nodeData, i)) #Makes list of names that match with txt files
for i in longNodeNames:
    if data_to_node(nodeData, i):
        shName.append(data_to_node(nodeData, i))
for i in longTripNames:
    if data_to_node(nodeData, i):
        shName.append(data_to_node(nodeData, i))

for name in set(shName):
    dataDict[name] = [] #Initializes short values as dictionaries with an empty list value
    aDataDict[name] = []
    bDataDict[name] = []
    cDataDict[name] = []
    unNormData[name] = []
    aUnNorm[name] = []
    bUnNorm[name] = []
    cUnNorm[name] = []


for i in range(len(longNames)):
    dataDict[shName[i]].append([data[i] for data in insts]) #Puts in all data for one node as value in dictionary
    unNormData[shName[i]].append([data[i] for data in insts]) #Same thing, to be kept unnormalized

#Same process as above for high voltage nodes, separated by phase
for i in range(len([l for l in longNodeNames if data_to_node(nodeData, l)])):
    dataDict[shName[len(longNames)+i]].append([data[i] for data in nodeInsts])
    aDataDict[shName[len(longNames)+i]].append([data[i] for data in nodeInsts])
    bDataDict[shName[len(longNames)+i]].append([data[i] for data in bNodeInsts])
    cDataDict[shName[len(longNames)+i]].append([data[i] for data in cNodeInsts])
    unNormData[shName[len(longNames)+i]].append([data[i] for data in nodeInsts])
    aUnNorm[shName[len(longNames)+i]].append([data[i] for data in nodeInsts])
    bUnNorm[shName[len(longNames)+i]].append([data[i] for data in bNodeInsts])
    cUnNorm[shName[len(longNames)+i]].append([data[i] for data in bNodeInsts])

#Same as above for triplex data
for i in range(len([l for l in longTripNames if data_to_node(nodeData, l)])):
    dataDict[shName[len(longNames) + len(longNodeNames) +i]].append([data[i] for data in tripInsts])
    unNormData[shName[len(longNames) + len(longNodeNames) +i]].append([data[i] for data in tripInsts])

#Normalizes all data in dictionaries
for key in dataDict.keys():
    for i in range(len(dataDict[key])):
        for j in range(len(dataDict[key][i])):
            dataDict[key][i][j] = nodeNormalize(nodeData, key, dataDict[key][i][j]) 

#Same as above for different phases 
for key in aDataDict.keys():
    for i in range(len(aDataDict[key])):
        for j in range(len(aDataDict[key][i])):
            aDataDict[key][i][j] = nodeNormalize(nodeData, key, aDataDict[key][i][j]) 
            bDataDict[key][i][j] = nodeNormalize(nodeData, key, bDataDict[key][i][j]) 
            cDataDict[key][i][j] = nodeNormalize(nodeData, key, cDataDict[key][i][j]) 

# Main Function
def main():
    print("AEGIS")

    # Create data frame for connecting nodes
    nodeFro = [fBranch.fromNode for fBranch in branchData.values()]
    nodeTo = [tBranch.toNode for tBranch in branchData.values()]
    for load in loadData.keys():
        nodeFro.append(loadData[load].node)
        nodeTo.append(load)
    connection = pd.DataFrame({'from': nodeFro,
                               'to': nodeTo})

    node_highlight_color = 'white'
    edge_highlight_color = 'black'

    # Create dict for node characteristics
    node_color_dict = {}

    #Color map for displaying changes over time
    color_mapper = LinearColorMapper(palette = "Turbo256", low = 0.95, high = 1.05, nan_color= 'lightgrey') 

    #Creates dictionary for branch color
    bColor= {}
    for branch in branchData.values():
        bColor[branch.fromNode, branch.toNode] = 'black'
    for load in loadData.values():
        bColor[load.node, load.label] = 'black'

    #Used to control color of node outline
    outline_dict = dict(zip(itertools.chain([n for n in nodeData.keys()], [l for l in loadData.keys()]), ['black']* (len(nodeData) + len(loadData))))

    #Creates a graph object contining nodes and edges from all connections
    g = networkx.from_pandas_edgelist(connection, 'from', 'to')

    #Creating From node dictionary
    fromNodeDict = {}
    for node in nodeData.values():
        if node.index != 1:
            fromNodeDict[node.label] = node.fromBranch.fromNode
        else:
            fromNodeDict[node.label] = 'N/A'
    for load in loadData.values():
        fromNodeDict[load.label] = load.node

    #Creates dictionary for so normalized values can be displayed with hover function
    valueDictionary = {}
    for node in nodeData.values():
        if node.label in dataDict.keys() and 'A' in node.phases:
            valueDictionary[node.label] = dataDict[node.label][0][0]
        else:
            valueDictionary[node.label] = 'N/A'
    for load in loadData.values():
        valueDictionary[load.label] = valueDictionary[load.node]

    #Sets attributes which will be displayed by hover function
    networkx.set_node_attributes(g, dict(zip(itertools.chain([n.label for n in nodeData.values()], [l for l in loadData.keys()]), itertools.chain([n.baseV for n in nodeData.values()], [nodeData[l.node].baseV for l in loadData.values()]))), 'node_base_v')
    networkx.set_node_attributes(g, dict(zip(itertools.chain([n.label for n in nodeData.values()], [l for l in loadData.keys()]), itertools.chain([n.phases for n in nodeData.values()], [nodeData[l.node].phases for l in loadData.values()]))), 'node_phase')
    networkx.set_node_attributes(g, node_color_dict, 'node_color')
    networkx.set_node_attributes(g, fromNodeDict, 'fromNode')
    networkx.set_node_attributes(g, outline_dict, 'border_color')
    networkx.set_node_attributes(g, valueDictionary, 'sim_vals')
    networkx.set_node_attributes(g, dict(zip(itertools.chain([n.label for n in nodeData.values()], [l for l in loadData.keys()]), itertools.chain([15]*len(nodeData), [10]*len(loadData)))), 'size')
    node_outline= 'border_color'
    lineType = {}
    lineLabel = {}
    fromNode = {}
    linePhases = {}
    toNode = {}

    #This program plots branches by inputting connected nodes, so this makes a dictionary with attributes
    for b in branchData.values():
        [a, c] = b.fromNode, b.toNode
        lineType[a, c] = b.type
        lineLabel[a, c] = b.label
        fromNode[a, c] = a
        toNode[a, c] = c
        linePhases[a, c] = b.phases

    #Associated Branch Attributes with visualization location
    networkx.set_edge_attributes(g, lineType, 'type')
    networkx.set_edge_attributes(g, linePhases, 'phase')
    networkx.set_edge_attributes(g, lineLabel, 'label')
    networkx.set_edge_attributes(g, fromNode, 'from')
    networkx.set_edge_attributes(g, toNode, 'to')
    networkx.set_edge_attributes(g, bColor, 'branch_color')
    edge_cmap= 'branch_color'

    #Creates figure object with some desired widgets
    plot = figure(
                  tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                  x_range=Range1d(-30.1, 30.1), y_range=Range1d(-30.1, 30.1))
    

    #Imports graph from networkx
    network_graph = from_networkx(g, networkx.kamada_kawai_layout, scale=30, center=(0, 0))

    def clickCall1(attr, old, new):
        #Checks that node is being selected, not deselected
        if(network_graph.node_renderer.data_source.selected.indices != []):

            #Finds selected nodes and plots its data over time
            nameClicked = list(itertools.chain(list(nodeData.keys()), list(loadData.keys())))[new[0]]
            if nameClicked in loadData.keys():
                nodeClicked = loadData[nameClicked].node #House voltages are the same as the node that they feed from
            else:
                nodeClicked = nameClicked

            if(nodeClicked in unNormData.keys()):
                if nodeClicked in nodeData.keys() and len(nodeData[nodeClicked].phases) > 2: #Checks if the object clicked has multiple phases
                    # Sets plot attributes
                    p = figure(title = ('Voltage Over Time for ' + nameClicked))
                    p.title.text_font_size = '20pt'
                    p.yaxis.axis_label = 'Voltage (V)'
                    p.xaxis.axis_label = 'Instance'
                    p.yaxis.axis_label_text_font_size = '15pt'
                    p.xaxis.axis_label_text_font_size = '15pt'
                    inds = [x + 1 for x in range(len(times))]
                    p.line(inds, aUnNorm[nodeClicked][0], line_color='red', legend_label= 'A Phase')
                    p.line(inds, bUnNorm[nodeClicked][0], line_color='blue', legend_label = 'B Phase')
                    p.line(inds, cUnNorm[nodeClicked][0], line_color='yellow', legend_label = 'C Phase')
                elif nodeClicked in nodeData.keys() and len(nodeData[nodeClicked].phases) == 2 and 'N' in nodeData[nodeClicked].phases:
                    p = figure(title = ('Voltage Over Time for ' + nameClicked))
                    p.title.text_font_size = '20pt'
                    p.yaxis.axis_label = 'Voltage (V)'
                    p.xaxis.axis_label = 'Time'  
                    p.yaxis.axis_label_text_font_size = '15pt'
                    p.xaxis.axis_label_text_font_size = '15pt'
                    inds = [x + 1 for x in range(len(times))]
                    if nodeData[nodeClicked].phases == 'AN':
                        p.line(inds, aUnNorm[nodeClicked][0])
                    if nodeData[nodeClicked].phases == 'BN':
                        p.line(inds, bUnNorm[nodeClicked][0])
                    if nodeData[nodeClicked].phases == 'CN':
                        p.line(inds, cUnNorm[nodeClicked][0])

                else:
                    source = ColumnDataSource(data=dict(voltage = unNormData[nodeClicked][0], time = times, inds = [x + 1 for x in range(len(times))])) # dates = time, nodes = energy value at that date for the node
                    p = figure(title = ('Voltage Over Time for ' + nameClicked))
                    p.title.text_font_size='20pt'
                    p.line('inds', 'voltage', source=source)
                    p.yaxis.axis_label = 'Voltage (V)'
                    p.xaxis.axis_label = 'Time'
                    p.yaxis.axis_label_text_font_size = '15pt'
                    p.xaxis.axis_label_text_font_size = '15pt'
                    p.add_tools(HoverTool(tooltips=[('Voltage', '@voltage'), ('Time', '@time')]))
    

                #Finds if a plot is present and either replaces, deletes, or puts up plot accordingly
                if (len(r.children[1].children) == 7):
                    r.children[1].children.append(p)
                else:
                    r.children[1].children[7] = p
            else:
                del r.children[1].children[7] #deletes plot of data over time if no node is clicked
        else:
            del r.children[1].children[7] #deletes plot of data over time if no node is clicked
        
    def clickCall2(attr, old, new):
        if(network_graph.edge_renderer.data_source.selected.indices != []):
            branchClicked = list(branchData.keys())[new[0]]
            bColor[branchData[branchClicked].fromNode, branchData[branchClicked].toNode] = 'orange'

    
    #Sets Nodes to be Colored Via color map and simulated values
    network_graph.node_renderer.glyph = Circle(size='size', fill_color={'field' : 'sim_vals', 'transform' : color_mapper}, line_color= node_outline)
    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=1, line_width=0.5, line_color= edge_cmap)

    #Adds tap capability to nodes and branches
    tap1 = TapTool(renderers=[network_graph.node_renderer])
    network_graph.node_renderer.nonselection_glyph = Circle(fill_alpha=0.4, fill_color={'field' : 'sim_vals', 'transform' : color_mapper})
    tap2 = TapTool(renderers=[network_graph.edge_renderer])
    network_graph.edge_renderer.nonselection_glyph = MultiLine(line_alpha=1)

    # Hover function for node portion of inital data
    hover_nodes = HoverTool(
                    tooltips= [("Node", "@index"), ("Base Voltage(V)", "@node_base_v"), ("Phase", "@node_phase"), ("From Node", "@fromNode"), ("Simulated Voltage", "@sim_vals")],
                    renderers= [network_graph.node_renderer]
                    )

    # Hover function for branch portion of initial data
    hover_edges = HoverTool(
				    tooltips=[('Branch', '@label'), ('Type','@type'), ("Phase", "@phase"), ("From", "@from"), ("To", "@to")],#, ("Length", "@length")],
				    renderers=[network_graph.edge_renderer],
                    line_policy= 'interp'
				    )

    plot.add_tools(hover_edges, hover_nodes, tap1, tap2)

    #callback when things are clicked
    network_graph.node_renderer.data_source.selected.on_change('indices',clickCall1)
    network_graph.edge_renderer.data_source.selected.on_change('indices',clickCall2)

    # Set edge highlight colors
    network_graph.edge_renderer.selection_glyph = MultiLine(line_color=node_highlight_color, line_width=2)
    network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    network_graph.selection_policy = NodesAndLinkedEdges()
    network_graph.inspection_policy = NodesAndLinkedEdges()

    # Add network graph to the plot
    plot.renderers.append(network_graph)

    #Makes Rectangle Demonstrating Color Range
    color_bar = ColorBar(color_mapper = color_mapper,
                     label_standoff = 14,
                     location = (0,0),
                     title = 'Plot')
    plot.add_layout(color_bar, 'right')

    #Checkboxes
    def checkCallback(attr, old, new):
        altNodes, altBranches = selectPhase(new, nodeData, branchData) #Finds comps containing selected phases
        if len(new) < len(old): #True if a box has been deselected
            gNodes = []
            gPhaseBranches= []
            for node in nodeData.keys():
                if node not in altNodes: #Finds nodes which are not to be colorful because of phase
                    nodeData[node].value[0] = False #marks this on node
                    gNodes.append(node)
                    
            for branch in branchData.keys():
                if branch not in altBranches and branch not in gPhaseBranches: #Finds branches not included
                    branchData[branch].value[0] = False #marks on branch
                    gPhaseBranches.append(branch)
            gOut(gNodes, gPhaseBranches) #greys other components

        else:
            #Components not inactive due to phase
            for i in altNodes:
                nodeData[i].value[0] = True
            
            for i in altBranches:
                branchData[i].value[0] = True
            restore(altNodes, altBranches)

    def nodeUpdate(index):

        # Changes simulated values to different time instance
        
        phaseFunc(['A', 'B', 'C'][phaseButtons.active], [aDataDict, bDataDict, cDataDict][phaseButtons.active])
        network_graph.node_renderer.data_source.data['sim_vals'] = list(valueDictionary.values())
        #Alters Colors According to New Values
        network_graph.node_renderer.glyph.fill_color = {'field' : 'sim_vals', 'transform' : color_mapper}
                

    def checkVCallback(attr, old, new):   
        if len(old) > len(new): #true if value has been deselected
            for i in old:
                if i not in new:  #Finds deselected voltage
                    greyN = selectVolt(voltages[i], nodeData) #returns nodes of said voltage
                    
                    #marks these values grey via voltage
                    for i in greyN:
                        nodeData[i].value[1] = False
                    gOut(greyN, [])

        else:
            for i in new:
                if i not in old: #values which have been selected
                    colorN = selectVolt(voltages[i], nodeData) #Finds components which should have color
                    
                    #Marks components to nto be grey via voltage
                    for i in colorN:
                        nodeData[i].value[1] = True

                    restore(colorN, []) 

    #Phase Checkbox Widget
    LABELS= ['A Phase', 'B Phase', 'C Phase']
    checkbox_group = CheckboxGroup(labels=LABELS, active=[0,1,2])
    checkbox_group.js_on_event('button_click', CustomJS(code="""
        console.log('checkbox_group: active=' + this.origin.active, this.toString())
    """))
    checkbox_group.on_change('active', checkCallback)

    #Voltage Checkbox Widget
    voltages = list(set([v.baseV for v in nodeData.values()])) #Creates a list of all different voltage values in figure
    voltages.sort() #Sorts values
    VOLTAGES= []
    for v in voltages:
        VOLTAGES.append(str(int(v)) + ' V') #Adds a V after number value
    checkbox_v = CheckboxGroup(labels=VOLTAGES, active=list(range(len(voltages))))
    checkbox_v.js_on_event('button_click', CustomJS(code="""
        console.log('checkbox_group: active=' + this.origin.active, this.toString())
    """))
    checkbox_v.on_change('active', checkVCallback)
    
    def bCallback(attr, old, new): #activated when node is entered
        if new != '': #makes sure this is not the value resetting
            if bColor[branchData[new].fromNode, branchData[new].toNode] == 'lightgrey':
                textVal = div.text[21:] #Reads text of inactive nodes, not including the inactive components: part
                textVal = textVal.split(', ') #splits to get a list of inactive parts
                #Formats new text block
                if new in textVal:
                    textVal.remove(new)
                if len(textVal):
                    textVal[0] = 'Inactive Components: ' + textVal[0]
                    if len(textVal) > 1:
                        textVal = ', '.join(textVal)
                    else:
                        textVal = textVal[0]
                else:
                    textVal = ''

                nBranch, nNode = deletionAlg(nodeData, branchData, branchData[new].toNode)
                nBranch.append(new)

                #Nodes components that theya re no longer greyed for something higher on the system becoming inactive
                for n in nNode:
                    nodeData[n].value[2] = True
                    
                for b in nBranch:
                    branchData[b].value[1] = True
                    
                restore(nNode, nBranch)
            else:
                if not div.text: #sees if there is any text for inactive nodes
                    textVal= 'Inactive Components: '
                else:
                    textVal= div.text

                gBranch, gNode= deletionAlg(nodeData, branchData, branchData[new].toNode) #returns branches and nodes to be greyed out
                gBranch.append(new)

                #Shows where node was greyed in dictionary
                for n in gNode:
                    nodeData[n].value[2] = False
                    
                for b in gBranch:
                    branchData[b].value[1] = False
                    
                deleteData('R2_1247_3_t11_mod_node_data_1.txt', 'node_Output.txt', [n.label for n in nodeData.values() if n.value[2] == False])
                deleteData('R2_1247_3_t11_mod_branch_data_1.txt', 'branch_Output.txt', [b.label for b in branchData.values() if b.value[1] == False])

                gOut(gNode, gBranch) #grey-out function

                if textVal == 'Inactive Components: ': #sees if node is the first node in list
                    textVal = textVal + new
                else:
                    textVal = textVal + ', ' + new
            branch_text_input.update(value='')#empties input box so same value can be put in again

            div.update(text=textVal)

    def callback(attr, old, new): #activated when node is entered
        if new != '': #Makes sure this is not the text box emptying
            if node_color_dict[new] == 'lightgrey':
                textVal = div.text[21:] #Reads text of inactive nodes, not including the inactive components: part
                textVal = textVal.split(', ') #splits to get a list of inactive parts

                if new in textVal: #Checks if the component entered is in the list of inactive parts
                    textVal.remove(new) #Removes component
                #Checks formatting changes needed
                if len(textVal):
                    textVal[0] = 'Inactive Components: ' + textVal[0]
                    if len(textVal) > 1:
                        textVal = ', '.join(textVal)
                    else:
                        textVal = textVal[0]
                else:
                    textVal = ''
                #Finds components feeding off of entered component

                nBranch, nNode = deletionAlg(nodeData, branchData, new)
                #Marks that components are not inactive due to upstream deactivation
                for n in nNode:
                    nodeData[n].value[2] = True
                    
                for b in nBranch:
                    branchData[b].value[1] = True
                    
                restore(nNode, nBranch)
            else:
                if not div.text: #sees if there is any text for inactive nodes
                    textVal= 'Inactive Components: '
                else:
                    textVal= div.text
                if textVal == 'Inactive Components: ': #sees if node is the first node in list
                    textVal = textVal + new
                else:
                    textVal = textVal + ', ' + new
                
                gBranch, gNode= deletionAlg(nodeData, branchData, new) #returns branches and nodes to be greyed out

                #Marks in node and branch objects that they are inactive int this form
                for n in gNode:
                    nodeData[n].value[2] = False
                    
                for b in gBranch:
                    branchData[b].value[1] = False
                    
                deleteData('R2_1247_3_t11_mod_node_data_1.txt', 'node_Output.txt', [n.label for n in nodeData.values() if n.value[2] == False])
                deleteData('R2_1247_3_t11_mod_branch_data_1.txt', 'branch_Output.txt', [b.label for b in branchData.values() if b.value[1] == False])

                gOut(gNode, gBranch)
            text_input.update(value='') #Empties text box
            div.update(text=textVal) #Updates text block of deactivated parts
        
    def gOut(gNode, gBranch):
        #Function when components need to be turned gray            
        for i in gNode:
            if node_color_dict[i] != 'lightgrey': #checks if node is alreasy inactive
                node_color_dict[i] = 'lightgrey' #changes color in color dictionary
                outline_dict[i] = 'lightgrey' #outline color change

        #Assigns light grey to inactive branches
        for branch in gBranch:
            bColor[branchData[branch].fromNode, branchData[branch].toNode] = 'lightgrey'
        update()

    def restore(nodes, edges):
        #Function which changes certain attibutes if parts no longer need to be gray
        for i in nodes:
            if(node_color_dict[i] != 'skyblue' and node_color_dict[i] != 'red' and node_color_dict[i] != 'yellow'): #Checks if node has been deactivated by another source
                #Checks for node color based on color
                if nodeData[i].index == 1:
                    node_color_dict[i] = 'yellow'
                elif nodeData[i].baseV == 7200:
                    node_color_dict[i] = 'red'
                else:
                    node_color_dict[i] = 'skyblue'
                outline_dict[i] = 'black' 


        #Updates branch color in dictionary
        for branch in edges:
            if branchData[branch].value[0] and branchData[branch].value[1]:
                bColor[branchData[branch].fromNode, branchData[branch].toNode] = 'black'
        update()    
        
    def update():        
        network_graph.node_renderer.data_source.data['node_color']=(list(node_color_dict.values()))
        network_graph.node_renderer.data_source.data['border_color']=(list(outline_dict.values()))
        network_graph.edge_renderer.data_source.data['branch_color']=(list(bColor.values()))

        plot.update(renderers = [network_graph])
   
    text_input = AutocompleteInput(title="Enter Node to be Put In or Out of Service:", completions= [n for n in nodeData.keys()], value="") #Autocomplete text box
    text_input.on_change("value", callback) #activates when text is entered
    
    branch_text_input = AutocompleteInput(title= "Enter Branch to be Put In or Out of Service:", completions= [b for b in branchData.keys()], value='')
    branch_text_input.on_change("value", bCallback) #activates when text is entered

    def movieCall():
        #indexes through all times
        for i in range(len(times)):
            slider.update(value= i + 1)
            
    #Adds button to movie functionality
    button = Button(label='Movie')
    button.on_click(movieCall)

    def slideCall(attr, old, new):
        #Callnack when slider value is changes
        slider.update(title = times[new -1]) #Updates slider title to display time
        nodeUpdate(new -1)

    def phaseFunc(phase, phData):
        #Changes which phase that is displayed
        vals = list(valueDictionary.keys())
        for l in vals:
            if l in nodeData.keys():
                if(phase in nodeData[l].phases): #Checks if phase is in node
                    #updates value to phase
                    if aDataDict[l] != []: #checks if node
                        valueDictionary[l] = phData[l][0][slider.value -1]
                    else:
                        valueDictionary[l] = dataDict[l][0][slider.value -1]
                else:
                    valueDictionary[l] = 'N/A' #changes to non-number value

            if l in loadData.keys():
                #Same as above for loads
                if(phase  not in loadData[l].phases):
                        valueDictionary[l] = 'N/A'
                else:
                    valueDictionary[l] = dataDict[loadData[l].node][0][slider.value -1]        

    def nodePhaseCall(attr, old, new):
        #checks phase and sends information to change to correct graph
        if(new==0):
            phaseFunc('A', aDataDict)
        
        if(new==1):
            phaseFunc('B', bDataDict)

        if(new==2):
            phaseFunc('C', cDataDict)

        network_graph.node_renderer.data_source.data['sim_vals'] = list(valueDictionary.values()) #Updates simulated values

        #Alters Colors According to New Values
        network_graph.node_renderer.glyph.fill_color = {'field' : 'sim_vals', 'transform' : color_mapper}

    #Button widgets for phase
    phaseButtons = RadioButtonGroup(labels = ['A Phase', 'B Phase', 'C Phase'], active=0)
    phaseButtons.on_change('active', nodePhaseCall)

    #Slider widget for time
    slider = Slider(start= 1, end = len(times), value = 1, title = times[0])
    slider.on_change('value', slideCall)

    div = Div(text = '') #Creates initial empty widget for text block of deactivated items

    r = row(children= [plot, column(children= [row(children=[checkbox_group, checkbox_v]), text_input, branch_text_input, div, row(children = [button]), phaseButtons, slider])]) #formatting
    curdoc().add_root(r) #adds plot to server

main()
