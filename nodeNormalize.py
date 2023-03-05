def nodeNormalize(nodeData, name, voltVal): # Normalized the data through one phase of the node
    baseV = nodeData[name].baseV #finds base voltage:
    voltVal = float(voltVal)/ 2/baseV #replaces values with normalized data
    return(voltVal)
