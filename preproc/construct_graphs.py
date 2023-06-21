'''
    extract graph
'''

import os
import sys
import time
import numpy as np
import pandas as pd

# environment settings.
rootPath = './'
tempPath = './'
dictPath = rootPath + '/dict/'
mdatPath = rootPath + '/data_mid/'
ndatPath = tempPath + '/data_np/'
ndt2Path = tempPath + '/data_np2/'
logsPath = tempPath + '/logs/'

# hyper-parameters.
_EmbedDim_ = 20
# output parameters.
_DEBUG_  = 0
_ERROR_  = 1
_TWINS_  = 1
# global variable.
start_time = time.time() #mark start time

# print setting.
pd.options.display.max_columns = None
pd.options.display.max_rows = None
np.set_printoptions(threshold=np.inf)
# Logger: redirect the stream on screen and to file.
class Logger(object):
    def __init__(self, filename = "log.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass

def RunTime():
    pTime = ' [TIME: ' + str(round((time.time() - start_time), 2)) + ' sec]'
    return pTime

def main():
    cnt = 0
    for root, ds, fs in os.walk(mdatPath):
        for file in fs:
            if '.DS_Store' in file: continue
            # if (cnt >= 10): continue
            # =====================================================
            filename = os.path.join(root, file).replace('\\', '/')
            savename = filename.replace(mdatPath, ndatPath)
            cnt += 1
            # if os.path.exists(savename):
            #     print('[INFO] <main> Have the graph numpy file: [' + str(cnt) + '] ' + savename + RunTime())
            #     print('=====================================================')
            #     continue
            print('[INFO] <main> Process the graph numpy file: [' + str(cnt) + '] ' + filename + RunTime())
            # =====================================================
            nodes, edges, nodes0, edges0, nodes1, edges1, label = ReadFile(filename)
            nodeDict, edgeIndex, edgeAttr = ProcEdges(edges)
            nodeAttr, nodeInvalid = ProcNodes(nodes, nodeDict)
            # -----------------------------------------------------
            np.savez(savename, edgeIndex=edgeIndex, edgeAttr=edgeAttr, nodeAttr=nodeAttr, label=label, nodeDict=nodeDict)
            print('[INFO] <main> save the graph information into numpy file: [' + str(cnt) + '] ' + savename + RunTime())
            print('-----------------------------------------------------')
            # =====================================================
            if _TWINS_:
                savename2 = filename.replace(mdatPath, ndt2Path)
                nodeDict0, edgeIndex0, edgeAttr0 = ProcEdges(edges0)
                nodeAttr0, nodeInvalid0 = ProcNodes(nodes0, nodeDict0)
                nodeDict1, edgeIndex1, edgeAttr1 = ProcEdges(edges1)
                nodeAttr1, nodeInvalid1 = ProcNodes(nodes1, nodeDict1)
                np.savez(savename2, edgeIndex0=edgeIndex0, edgeAttr0=edgeAttr0, nodeAttr0=nodeAttr0,
                         edgeIndex1=edgeIndex1, edgeAttr1=edgeAttr1, nodeAttr1=nodeAttr1, label=label)
                print('[INFO] <main> save the graph information (twins) into numpy file: [' + str(cnt) + '] ' + savename2 + RunTime())
                print('=====================================================')
            # =====================================================

    return

def ReadFile(filename):
    '''
    :param filename:
    :return:
    '''

    graph = np.load(filename, allow_pickle=True)
    nodes = graph['nodes']
    edges = graph['edges']
    nodes0 = graph['nodes0']
    edges0 = graph['edges0']
    nodes1 = graph['nodes1']
    edges1 = graph['edges1']
    label = graph['label']

    return nodes, edges, nodes0, edges0, nodes1, edges1, label

def ProcEdges(edgesData):
    '''
    Mapping the edges to edge embeddings.
    :param edgesData: [['-32', '-51', 'EDGE_TYPE', '0'], ...]
    :return: nodeDict - {'-32': 0, '-51': 1, ...}
             edgeIndex - [[0, 1, ...], [1, 2, ...]]
             edgeAttr - [[1, 0, 0, 0, 1], ...]
    '''

    if 0 == len(edgesData):
        print('[WARNING] <ProcEdges> Find a graph without edges')
        return {}, np.array([[0], [1]]), np.zeros((1, 5)) # one edge, attr: [0 0 0 0 0]

    # get the node set.
    nodesout = [edge[0] for edge in edgesData]
    nodesin = [edge[1] for edge in edgesData]
    nodeset = nodesout + nodesin
    # remove duplicates
    nodeset = {}.fromkeys(nodeset)
    nodeset = list(nodeset.keys())
    # get the dictionary.
    nodeDict = {node: index for index, node in enumerate(nodeset)}
    print('[INFO] <ProcEdges> Find', len(nodeDict), 'nodes connected with', len(edgesData), 'edges.' + RunTime())
    if _DEBUG_: print(nodeDict)

    # get the edge index. [2 * edge_num]
    nodesoutIndex = [nodeDict[node] for node in nodesout]
    nodesinIndex = [nodeDict[node] for node in nodesin]
    edgeIndex = np.array([nodesoutIndex, nodesinIndex])
    print('[INFO] <ProcEdges> Get', len(edgeIndex), '*', len(edgeIndex[0]), 'edge index array.' + RunTime())
    if _DEBUG_: print(edgeIndex)

    # get the dictionary of version and type.
    verDict = {'-1': [1, 0], '0': [1, 1], '1': [0, 1]}
    typeDict = {'CDG': [1, 0, 0], 'DDG': [0, 1, 0], 'AST': [0, 0, 1]}

    # get the edge attributes. [edge_num, num_edge_features]
    typeAttr = np.array([typeDict[edge[2]] for edge in edgesData])
    verAttr = np.array([verDict[edge[3]] for edge in edgesData])
    edgeAttr = np.c_[verAttr, typeAttr]
    print('[INFO] <ProcEdges> Get', len(edgeAttr), '*', len(edgeAttr[0]), 'edge attribute array.' + RunTime())
    if _DEBUG_: print(edgeAttr)

    return nodeDict, edgeIndex, edgeAttr

def GetNodeEmbedding(nodeData):
    '''
    Convert a code segment in a node to node embedding.
    :param codeData: ['-117', '0', 'C', '2', '11646', [2, 4, 2], ['opt', '!=', 'NULL']]
    :return: [ , , , ...]
    '''

    # nodeId = nodeData[0]
    nodeVer = nodeData[1]
    nodeType = nodeData[2]
    nodeDist = nodeData[3]
    # codeLine = nodeData[4]
    tokenTypes = nodeData[-2]
    tokens = nodeData[-1]
    numTokens = len(tokenTypes)

    # generate weights.
    weight0 = 1 if ('-' == nodeType) else 0 if ('D' in nodeType) else 0
    weight1 = 1 / (1 + int(nodeDist))

    # get embeddings of tokens.
    count_char = 0
    count_mem = 0
    count_str = 0
    count_lock = 0
    count_null = 0
    count_API = 0
    for i in range(numTokens):
        count_char += len(tokens[i])
        if (2 == tokenTypes[i]):
            for item in ['alloc', 'free', 'mem', 'sizeof', 'new', 'delete', 'open', 'close', 
            'create', 'release', 'copy', 'remove', 'clear', 'dequene', 'enquene', 'detach', 'attach']:
                if item in tokens[i].lower():
                    count_mem = 1
            for item in ['str']:
                if item in tokens[i].lower():
                    count_str = 1
            for item in ['lock', 'mutex', 'spin']:
                if item in tokens[i].lower():
                    count_lock = 1
            for item in ['null', 'nil', 'none']:
                if item in tokens[i].lower():
                    count_null = 1
            for item in ['put', 'get',  'init', 'register', 'down', 'up', 'disable', 'enable', 
            'sub', 'add', 'dec', 'inc', 'set', 'stop', 'start', 'suspend', 'resume', 'connect', 'map', 'prepare']:
                if item in tokens[i].lower():
                    count_API = 1
            

    # abstract the code.
    for i in range(numTokens):
        if 5 == tokenTypes[i]: # comment
            tokens[i] = 'COMMENT'
        elif 3 == tokenTypes[i]: # literal
            if tokens[i].isdigit():
                tokens[i] = 'NUM'
            else:
                tokens[i] = 'LITERAL'
        elif 2 == tokenTypes[i]: # identifier
            if (i < numTokens - 1):
                if (tokens[i + 1] == '(') and (len(tokens[i]) >= 2):
                    tokens[i] = 'FUNC'
                else:
                    tokens[i] = 'VAR'
            else:
                tokens[i] = 'VAR'
        else: # keywords/punctuation
            pass
    # print(tokens)
    # print(tokenTypes)

    # get embeddings of tokens.
    count_if = 0
    count_loop = 0
    count_jump = 0
    count_func = 0
    count_var = 0
    count_num = 0
    count_literal = 0
    count_op_arith = 0
    count_op_rel = 0
    count_op_log = 0
    count_op_bit = 0
    count_ptr = 0
    count_array = 0
    for i in range(numTokens):
        if (1 == tokenTypes[i]) and (tokens[i] in ['if', 'switch']):
            count_if = 1
        elif (1 == tokenTypes[i]) and (tokens[i] in ['for', 'while']):
            count_loop = 1
        elif (1 == tokenTypes[i]) and (tokens[i] in ['return', 'break', 'continue', 'goto', 'throw', 'assert']):
            count_jump = 1
        elif (2 == tokenTypes[i]) and ('FUNC' == tokens[i]):
            count_func += 1
        elif (2 == tokenTypes[i]) and ('VAR' == tokens[i]):
            count_var += 1
        elif (3 == tokenTypes[i]) and ('NUM' == tokens[i]):
            count_num += 1
        elif (3 == tokenTypes[i]) and ('LITERAL' == tokens[i]):
            count_literal += 1
        elif (4 == tokenTypes[i]) and (tokens[i] in ['++', '--', '=', '+', '-', '/', '%']):
            count_op_arith += 1
        elif (4 == tokenTypes[i]) and ('*' == tokens[i]):
            if (i >= 1) and ('VAR' == tokens[i - 1]):
                count_op_arith += 1
            else:
                count_ptr += 1
        elif (4 == tokenTypes[i]) and (tokens[i] in ['==', '!=', '>=', '<=', '>', '<']):
            count_op_rel += 1
        elif (4 == tokenTypes[i]) and (tokens[i] in ['&&', '||', '!', 'not', 'and', 'or']):
            count_op_log += 1
        elif (4 == tokenTypes[i]) and (tokens[i] in ['<<', '>>', 'bitand', 'bitor', 'xor', '~', '|', '^']):
            count_op_bit += 1
        elif (4 == tokenTypes[i]) and ('&' == tokens[i]):
            if (i >= 1) and ('VAR' == tokens[i - 1]):
                count_op_bit += 1
            else:
                count_ptr += 1
    if ('[' in tokens) and (']' in tokens):
        count_array = 1

    embeds = [count_if, count_loop, count_jump, count_func, count_var, count_num, count_literal, # 7
              count_op_arith, count_op_rel, count_op_log, count_op_bit, # 4
              count_char, count_mem, count_str, count_lock, # 4
              count_ptr, count_array, count_null, count_API] # 3
    embeds = np.array(embeds, dtype=np.float64)

    # add weights to embeds.
    embeds *= weight0 * weight1
    embeds = np.r_[[int(nodeVer)], embeds]
    # print(embeds)

    return embeds

def ProcNodes(nodesData, nodeDict):
    '''
    Mapping the nodes to node embeddings.
    :param nodesData: [['-165', '0', 'C', '2', '11655', list([4, 2, 4, 4, 2, 4, 3, 4, 4, 2]),
                        list(['*', 'ptr', '=', '(', 'delta_base', '<<', '4', ')', '|', 'length_base'])], ...]
    :param nodeDict: {'-32': 0, '-51': 1, ...}
    :return: [[], [], ...]
    '''

    if (0 == len(nodesData)) or (0 == len(nodeDict)):
        print('[WARNING] <ProcNodes> Find a graph without nodes')
        return np.zeros((2, _EmbedDim_)), 1  # 2 void nodes

    # get the list of all nodes.
    nodeList = [node[0] for node in nodesData]
    # print(len(nodeList))

    # check the integrity of the node list.
    for node in nodeDict:
        if node not in nodeList:
            print('[Error] <ProcNodes> Node', node, 'does not in node list.')
            return -1, -1

    # get the node attributes with the order of node dictionary.
    nodeOrder = [nodeList.index(node) for node in nodeDict]
    nodesDataNew = [nodesData[order] for order in nodeOrder]
    # print(nodesDataNew)

    nodeAttr = []
    for nodeData in nodesDataNew:
        # print(nodeData)
        nodeEmbed = GetNodeEmbedding(nodeData)
        # append the node embedding.
        nodeAttr.append(nodeEmbed)
    nodeAttr = np.array(nodeAttr)

    # print(nodeAttr)
    print('[INFO] <ProcNodes> Get', len(nodeAttr), '*', len(nodeAttr[0]), 'node attribute array.' + RunTime())

    return nodeAttr, 0

if __name__ == '__main__':
    # initialize the log file.
    logfile = 'construct_graphs.txt'
    if os.path.exists(os.path.join(logsPath, logfile)):
        os.remove(os.path.join(logsPath, logfile))
    elif not os.path.exists(logsPath):
        os.makedirs(logsPath)
    sys.stdout = Logger(os.path.join(logsPath, logfile))
    # check folders.
    if not os.path.exists(ndatPath + '/negatives/'):
        os.makedirs(ndatPath + '/negatives/')
    if not os.path.exists(ndatPath + '/positives/'):
        os.makedirs(ndatPath + '/positives/')
    if not os.path.exists(ndt2Path + '/negatives/'):
        os.makedirs(ndt2Path + '/negatives/')
    if not os.path.exists(ndt2Path + '/positives/'):
        os.makedirs(ndt2Path + '/positives/')
    # main entrance.
    main()
