# AEGIS - Distribution System Visualization Software
# Visual tool for visualizing data
# 9/25/22
import networkx

# Internal Imports
from deleteData import *
from Data_to_Node import *
import plotly.graph_objects as go
from constants import *
from classes import *
from deletionAlg import deletionAlg
from AEGIS_select import selectPhase, selectVolt
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import numpy as np
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, \
    NodesAndLinkedEdges, LabelSet, HoverTool, Div, Button, TapTool, LinearColorMapper, ColorBar
from bokeh.plotting import figure, curdoc, show
from bokeh.plotting import from_networkx, gridplot
from bokeh.models import NodesAndLinkedEdges, CheckboxGroup, CustomJS, AutocompleteInput, Slider
from importData_HH import importData_HH
from bokeh.layouts import row, column
from bokeh.events import Tap
from ImportCSV import *
from nodeNormalize import *
from bokeh.transform import transform
import time

# External Imports
nodeData, branchData= importData_HH('R2_1247_3_t11_mod_branch_data.txt', 'R2_1247_3_t11_mod_node_data.txt')
times, insts, longNames = csvRead()

for i in range(len(insts)):
    insts[i][1] = 240*(0.95 + 0.1 * i/len(insts))

for i in range(len(longNames)):
    newDict = {}
longNames = longNames[1:]
shName = []
dataDict = {}
for i in range(len(longNames)):
    shName.append(data_to_node(nodeData, longNames[i]))
for name in set(shName):
    dataDict[name] = []
for i in range(len(longNames)):
    dataDict[shName[i]].append(insts[i])
for key in dataDict.keys():
    for i in range(len(dataDict[key])):
        for j in range(len(dataDict[key][i])):
            dataDict[key][i][j] = nodeNormalize(nodeData, key, dataDict[key][i][j])  

# Main Function
def main():
    print("AEGIS")

    # Create data frame for connecting nodes
    connection = pd.DataFrame({'from': [fBranch.fromNode for fBranch in branchData.values()],
                               'to': [tBranch.toNode for tBranch in branchData.values()]})

    node_highlight_color = 'white'
    edge_highlight_color = 'black'

    # Create dict for node characteristics
    node_color_dict = {}

    color_mapper = LinearColorMapper(palette = "Turbo256", low = 0.95, high = 1.05, nan_color= 'lightgrey')

    #Initializes node color
    for n in nodeData.values():
        if n.index == 1:
            node_color_dict[n.label] = 'yellow'
        elif n.baseV == 7200:
            node_color_dict[n.label] = 'red'
        else:
            node_color_dict[n.label] = 'skyblue'

    bColor= {}
    for branch in branchData.values():
        bColor[branch.fromNode, branch.toNode] = 'black' #Creates dictionary for edge color

    #Used to control color of node outline
    outline_dict = dict(zip([n for n in nodeData.keys()], ['black']* len(nodeData)))

    #Creates a graph object contining nodes and edges from all connections
    g = nx.from_pandas_edgelist(connection, 'from', 'to')

    #Creating From node dictionary
    fromNodeDict = {}
    for node in nodeData.values():
        if node.index != 1:
            fromNodeDict[node.label] = node.fromBranch.fromNode
        else:
            fromNodeDict[node.label] = 'N/A'

    valueDictionary = {}
    for node in nodeData.values():
        if node.label in dataDict.keys():
            valueDictionary[node.label] = dataDict[node.label][0][0]
        else:
            valueDictionary[node.label] = 'N/A'

    #Sets attributes which will be displayed by hover function
    networkx.set_node_attributes(g, dict(zip([n.label for n in nodeData.values()], [n.baseV for n in nodeData.values()])), 'node_base_v')
    networkx.set_node_attributes(g, dict(zip([n.label for n in nodeData.values()], [n.phases for n in nodeData.values()])), 'node_phase')
    networkx.set_node_attributes(g, node_color_dict, 'node_color')
    networkx.set_node_attributes(g, fromNodeDict, 'fromNode')
    networkx.set_node_attributes(g, outline_dict, 'border_color')
    networkx.set_node_attributes(g, valueDictionary, 'sim_vals')
    node_outline= 'border_color'
    color_attribute = 'node_color'
    lineType = {}
    lineLabel = {}
    fromNode = {}
    linePhases = {}
    toNode = {}
    lengthDict = {}

    #This program plots branches by inputting connected nodes, so this makes a dictionary with attributes
    for b in branchData.values():
        [a, c] = b.fromNode, b.toNode
        lineType[a, c] = b.type
        lineLabel[a, c] = b.label
        fromNode[a, c] = a
        toNode[a, c] = c
        lengthDict[a, c] = b.length
        linePhases[a, c] = b.phases
    #Associated Branch Attributes with visualization location
    networkx.set_edge_attributes(g, lineType, 'type')
    networkx.set_edge_attributes(g, linePhases, 'phase')
    networkx.set_edge_attributes(g, lineLabel, 'label')
    networkx.set_edge_attributes(g, fromNode, 'from')
    networkx.set_edge_attributes(g, toNode, 'to')
    networkx.set_edge_attributes(g, lengthDict, 'length')
    networkx.set_edge_attributes(g, bColor, 'branch_color')
    edge_cmap= 'branch_color'

    #Creates figure object with some desired widgets
    plot = figure(
                  tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                  x_range=Range1d(-30.1, 30.1), y_range=Range1d(-30.1, 30.1))

    #Imports graph from networkx
    network_graph = from_networkx(g, nx.kamada_kawai_layout, scale=30, center=(0, 0))

    # Add Labels
    '''x, y = zip(*network_graph.layout_provider.graph_layout.values())
    node_labels = list(g.nodes())
    source = ColumnDataSource({'x': x, 'y': y, 'name': [node_labels[i] for i in range(len(x))]})
    #labels = LabelSet(x='x', y='y', text='name', source=source, background_fill_color='white', text_font_size='10px',
    #                  background_fill_alpha=.7)'''
    #print(network_graph.node_renderer.data_source.data)
    x, y = zip(*network_graph.layout_provider.graph_layout.values())

    network_graph.node_renderer.glyph = Circle(size=15, fill_color={'field' : 'sim_vals', 'transform' : color_mapper}, line_color= node_outline)
    #print(network_graph.layout_provider.graph_layout.values())

    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1, line_color= edge_cmap)


    # Hover function for node portion of inital data
    hover_nodes = HoverTool(
                    tooltips= [("Node", "@index"), ("Base Voltage(V)", "@node_base_v"), ("Phase", "@node_phase"), ("From Node", "@fromNode"), ("Simulated Voltage", "@sim_vals")],
                    renderers= [network_graph.node_renderer]
                    )
    
    #tapEvent = TapTool()


    # Hover function for branch portion of initial data
    hover_edges = HoverTool(
				    tooltips=[('Branch', '@label'), ('Type','@type'), ("Phase", "@phase"), ("From", "@from"), ("To", "@to"), ("Length", "@length")],
				    renderers=[network_graph.edge_renderer],
                    line_policy= 'interp'
				    )

    def call(event):
        print(event.data)

    plot.add_tools(hover_edges, hover_nodes)#, tapEvent)#, TapTool(renderers=[network_graph.node_renderer, network_graph.edge_renderer]))
    #plot.on_event(Tap, call)

    # Set edge highlight colors
    network_graph.edge_renderer.selection_glyph = MultiLine(line_color=node_highlight_color, line_width=2)
    network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
    network_graph.selection_policy = NodesAndLinkedEdges()
    network_graph.inspection_policy = NodesAndLinkedEdges()

    # Add network graph to the plot
    plot.renderers.append(network_graph)
#plot.renderers.append(labels)

    '''color = LinearColorMapper(palette = 'Viridis256',
                          low = -100,
                          high = 40)'''

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
        #print(network_graph.node_renderer.data_source.data)
        for i in dataDict.keys():
            valueDictionary[i] = dataDict[i][0][index]
        network_graph.node_renderer.data_source.data['sim_vals'] = list(valueDictionary.values())
        #print(nodeVoltRange)
        network_graph.node_renderer.glyph.fill_color = {'field' : 'sim_vals', 'transform' : color_mapper}
        #update()
                
    def aPhaseCall():
        nodeUpdate(1)
        
    def bPhaseCall():
        restore([n.label for n in nodeData.values()], [])
    def cPhaseCall():
        print('C')

    def checkVCallback(attr, old, new):   
        if len(old) > len(new): #true if value has been deselected
            for i in old:
                if i not in new:  #Finds deselected voltage
                    greyN = selectVolt(voltages[i], nodeData) #returns nodes of said voltage
                    
                    #marks these values grey via voltage
                    for i in greyN:
                        nodeData[i].value[1] = False
                        #node_value_dict[i][1] = False
                    gOut(greyN, [])

        else:
            for i in new:
                if i not in old: #values which have been selected
                    colorN = selectVolt(voltages[i], nodeData) #Finds components which should have color
                    
                    #Marks components to nto be grey via voltage
                    for i in colorN:
                        nodeData[i].value[1] = True
                        #node_value_dict[i][1] = True
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
        #print('check 1')
        #Function which changes certain attibutes if parts no longer need to be gray
        for i in nodes:
            #print(i)
            #print(node_color_dict[i])
            if(node_color_dict[i] != 'skyblue' and node_color_dict[i] != 'red' and node_color_dict[i] != 'yellow'): #Checks if node has been deactivated by another source
                #print(i)
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
    
        
        #print(network_graph.node_renderer.data_source.data)

        plot.update(renderers = [network_graph])

    #print(network_graph.node_renderer.data_source)     
    text_input = AutocompleteInput(title="Enter Node to be Put In or Out of Service:", completions= [n for n in nodeData.keys()], value="") #Autocomplete text box
    text_input.on_change("value", callback) #activates when text is entered
    
    branch_text_input = AutocompleteInput(title= "Enter Branch to be Put In or Out of Service:", completions= [b for b in branchData.keys()], value='')
    branch_text_input.on_change("value", bCallback) #activates when text is entered

    def movieCall():
        for i in range(len(insts[0])):
            slider.value= i + 1
            #print(slider.value)
            #nodeUpdate(i)
            #time.sleep(1)


    button = Button(label='Movie Thing')
    button.on_click(movieCall)

    def slideCall(attr, old, new):
        nodeUpdate(new -1)


    slider = Slider(start= 1, end = len(insts[0]), value = 1, title = times[0])
    slider.on_change('value', slideCall)

    div = Div(text = '') #Creates initial empty widget for text block of deactivated items

    r = row(children= [plot, column(children= [row(children=[checkbox_group, checkbox_v]), text_input, branch_text_input, div, row(children = [button]), slider])]) #formatting
    curdoc().add_root(r) #adds plot to server

main()
