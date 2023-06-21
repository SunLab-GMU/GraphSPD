'''
    extract graph
'''

import os
import re
import sys
import time
import numpy as np
import pandas as pd
import clang.cindex
import clang.enumerations

if sys.platform == 'darwin':
    lib_path = '/Library/Developer/CommandLineTools/usr/lib/'
    clang.cindex.Config.set_library_path(lib_path)

# environment settings.
rootPath = './'
tempPath = './'
dataPath = rootPath + '/data_raw/'
mdatPath = tempPath + '/data_mid/'
logsPath = tempPath + '/logs/'

# output parameters.
_DEBUG_  = 0
_ERROR_  = 1
_CLANG_  = 1
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
    for root, ds, fs in os.walk(dataPath):
        for file in fs:
            # if (cnt >= 1): continue
            if ('.DS_Store' in file): continue
            # =====================================================
            filename = os.path.join(root, file).replace('\\', '/')
            subfolder = '/positives/' if ('positives' in root) else '/negatives/'
            savename = os.path.join(mdatPath + subfolder, file[:-4] + '.npz')
            cnt += 1
            # if os.path.exists(savename):
            #     print('[INFO] <main> Have the graph numpy file: [' + str(cnt) + '] ' + savename + RunTime())
            #     print('=====================================================')
            #     continue
            # =====================================================
            nodes, edges, nodes0, edges0, nodes1, edges1 = ReadFile(filename)
            if _CLANG_:
                nodes = ProcNodes(nodes, 'PatchCPG')
                nodes0 = ProcNodes(nodes0, 'PreCPG')
                nodes1 = ProcNodes(nodes1, 'PostCPG')
            label = [1] if ('positives' in root) else [0]
            # # =====================================================
            np.savez(savename, nodes=nodes, edges=edges, nodes0=nodes0, edges0=edges0, nodes1=nodes1, edges1=edges1, label=label, dtype=object)
            print(f'[INFO] <main> save the graph information into numpy file: [{str(cnt)}] ' + savename + RunTime())
            print('=====================================================')
            # savename = os.path.join(ndat2Path, 'data_{:05d}.npz'.format(cnt-1))
            # np.savez(savename, edgeIndex=edgeIndex, edgeAttr=edgeAttr, nodeAttr=nodeAttr, label=label, nodeDict=nodeDict)
            # =====================================================
    return

def ParseEdge(filename, line):

    if _DEBUG_: print(line, end='')

    if '\n' == line:
        return []

    pattern = r'\(-\d+, -\d+, [\'\"].*[\'\"], -?\d\)'
    contents = re.findall(pattern, line)
    if 0 == len(contents):
        if _ERROR_: print('[ERROR] <ParseEdge> Edge does not match the format, para:', filename, line)
        return []
    content = contents[0]  # get the first match.

    content = content[1:-1].replace(' ', '')  # remove () and SPACE.
    segs = content.split(',')  # split with comma.
    segs[2] = segs[2][1:-1]  # remove ''
    if segs[2].startswith('DDG'):
        segs[2] = 'DDG'
    if not segs[2] in ['CDG', 'DDG']:
        if _ERROR_: print('[ERROR] <ParseEdge> Edgetype Error, para:', filename, line)
        return []

    # [nodeout, nodein, nodetype, version]
    ret = np.array([segs[0], segs[1], segs[2], segs[-1]], dtype=object)

    return ret

def ParseNode(filename, line):

    if _DEBUG_: print(line, end='')

    if '\n' == line:
        return []

    pattern = r'\(-\d+, -?\d, \'[CD-]+\', \d+, \'[-+]?\d+\', [\'\"].*[\'\"]\)'
    contents = re.findall(pattern, line)
    if 0 == len(contents):
        if _ERROR_: print('[ERROR] <ParseNode> Node does not match the format, para:', filename, line)
        return []
    content = contents[0]

    content = content[1:-1]  # remove ()
    segs = content.split(',')  # split with comma.
    segs[0] = segs[0].replace(' ', '')
    segs[1] = segs[1].replace(' ', '')
    segs[2] = segs[2].replace(' ', '')
    segs[2] = segs[2][1:-1]  # remove ''
    segs[3] = segs[3].replace(' ', '')
    segs[4] = segs[4].replace(' ', '')
    segs[4] = segs[4][1:-1]
    attr = ','.join(segs[5:])
    attr = attr[2:-1]

    # [nodeid, version, nodetype, dist, linenum, [tokentype], [tokens]]
    ret = np.array([segs[0], segs[1], segs[2], segs[3], segs[4], [0], [attr]], dtype=object)

    return ret

def ReadFile(filename):
    '''
    :param filename:
    :return:
    '''

    # read lines from the file.
    print('[INFO] <ReadFile> Read data from:', filename)
    fp = open(filename, encoding='utf-8', errors='ignore')
    lines = fp.readlines()
    fp.close()
    if _DEBUG_: print(lines)

    # get the data from edge and node information.
    signGraph = 0
    signEdge = 1
    edgesData = []
    edgesData0 = []
    edgesData1 = []
    nodesData = []
    nodesData0 = []
    nodesData1 = []

    for line in lines:
        # for each line in this file.
        if line.startswith('---'):
            # exchange to the next graph (0:PatchCPG, 1:PreCPG, 2:PostCPG)
            signGraph += 1
            signEdge = 1
        elif line.startswith('==='):
            # exchange to the node parsing of the same graph.
            signEdge = 0
        elif (1 == signEdge):
            # Edge:
            edge = ParseEdge(filename, line)
            if 0 == len(edge):
                continue
            # save edge.
            if 0 == signGraph:
                edgesData.append(edge)
            elif 1 == signGraph:
                edgesData0.append(edge)
            elif 2 == signGraph:
                edgesData1.append(edge)
            else:
                if _ERROR_: print('[ERROR] <ReadFile> Find abnormal additional graphs, para:', filename)
        elif (0 == signEdge):
            # Node:
            node = ParseNode(filename, line)
            if 0 == len(node):
                continue
            # save node.
            if 0 == signGraph:
                nodesData.append(node)
            elif 1 == signGraph:
                nodesData0.append(node)
            elif 2 == signGraph:
                nodesData1.append(node)
            else:
                if _ERROR_: print('[ERROR] <ReadFile> Find abnormal additional graphs, para:', filename)
        else:
            # Error:
            if _ERROR_: print('[ERROR] <ReadFile> Neither an edge or a node, para:', filename, line)

    print(f'[INFO] <ReadFile> Read PatchCPG (#node: {len(nodesData)}, #edge: {len(edgesData)}), ', end='')
    print(f'PreCPG (#node: {len(nodesData0)}, #edge: {len(edgesData0)}), ', end='')
    print(f'PostCPG (#node: {len(nodesData1)}, #edge: {len(edgesData1)}).' + RunTime())
    if _DEBUG_:
        print(nodesData)
        print(edgesData)

    return nodesData, edgesData, nodesData0, edgesData0, nodesData1, edgesData1

def Tokenize(code):
    '''
    Convert a code segment to code tokens.
    :param code: code string
    :return: [ , , , ...]
    '''

    # if the code is void.
    if '' == code:
        return [0], ['']

    # defination.
    tokenClass = [clang.cindex.TokenKind.KEYWORD,  # 1
                  clang.cindex.TokenKind.IDENTIFIER,  # 2
                  clang.cindex.TokenKind.LITERAL,  # 3
                  clang.cindex.TokenKind.PUNCTUATION,  # 4
                  clang.cindex.TokenKind.COMMENT]  # 5
    tokenTypeDict = {cls: index + 1 for index, cls in enumerate(tokenClass)}

    # initialize.
    tokens = []
    tokenTypes = []

    # remove non-ascii.
    code = code.encode("ascii", "ignore").decode()

    # clang sparser.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'], unsaved_files=[('tmp.cpp', code)], options=0)
    for t in tu.get_tokens(extent=tu.cursor.extent):
        # print(t.kind, t.spelling, t.location)
        tokens.append(t.spelling)
        tokenTypes.append(tokenTypeDict[t.kind])

    # print(tokenTypes, tokens)

    return tokenTypes, tokens

def ProcNodes(nodesData, gtype='CPG'):
    '''
    :param nodesData: [['-100', '0', 'C', '5', '348', [0], ['r < 0']], ...]
    :return: [['-100', '0', 'C', '5', '348', [2, 4, 3], ['r', '<', '0']], ...]
    '''

    # print(nodesData)

    ret = []
    for node in nodesData:
        # print(node)
        types, tokens = Tokenize(node[-1][0])
        node_new = [node[0], node[1], node[2], node[3], node[4], types, tokens]
        ret.append(node_new)

    ret = np.array(ret, dtype=object)

    print(f'[INFO] <ProcNodes> Tokenize code for {len(nodesData)} nodes in {gtype}.' + RunTime())

    return ret

if __name__ == '__main__':
    # initialize the log file.
    logfile = 'extract_graphs.txt'
    if os.path.exists(os.path.join(logsPath, logfile)):
        os.remove(os.path.join(logsPath, logfile))
    elif not os.path.exists(logsPath):
        os.makedirs(logsPath)
    sys.stdout = Logger(os.path.join(logsPath, logfile))
    # check folders.
    if not os.path.exists(mdatPath + '/negatives/'):
        os.makedirs(mdatPath + '/negatives/')
    if not os.path.exists(mdatPath + '/positives/'):
        os.makedirs(mdatPath + '/positives/')
    # main entrance.
    main()
