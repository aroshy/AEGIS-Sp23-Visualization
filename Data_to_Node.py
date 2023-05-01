# AEGIS - Distribution System Visualization Software
# Matches longer names to their shorter counterparts

def data_to_node(nodeData, ext_name):
    for i in nodeData.keys():
        if ext_name.endswith(i):
            return i