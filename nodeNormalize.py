# AEGIS - Distribution System Visualization Software
# Normalizes the data through one phase of the node

def nodeNormalize(nodeData, name, voltVal):
    baseV = nodeData[name].baseV #finds base voltage:
    if (baseV == 120):
        voltVal = float(voltVal)/ 2/baseV #replaces values with normalized data
    else:
        voltVal = float(voltVal)/ baseV
    return(voltVal)
