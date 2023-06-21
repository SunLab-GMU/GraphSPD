import os
import sys
import time
import numpy as np
import torch
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from libs.nets.PGCN_noAST import PGCN, PGCNTest

from preproc import extract_graphs, construct_graphs

logsPath = './logs/'
testPath = './testdata/'
mdlsPath = './models/'

# parameters
_CLANG_  = 1
_NETXARCHT_ = 'PGCN'
_BATCHSIZE_ = 128
dim_features = 20
start_time = time.time() #mark start time

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

# extract graphs
def extractgraphs():
    cnt = 0
    for root, ds, fs in os.walk(testPath):
        for file in fs:
            if ('.log' == file[-4:]):
                filename = os.path.join(root, file).replace('\\', '/')
                savename = filename + '_mid.npz'
                cnt += 1
                nodes, edges, nodes0, edges0, nodes1, edges1 = extract_graphs.ReadFile(filename)
                if _CLANG_:
                    nodes = extract_graphs.ProcNodes(nodes, 'PatchCPG')
                    nodes0 = extract_graphs.ProcNodes(nodes0, 'PreCPG')
                    nodes1 = extract_graphs.ProcNodes(nodes1, 'PostCPG')
                label = [0]
                np.savez(savename, nodes=nodes, edges=edges, nodes0=nodes0, edges0=edges0, nodes1=nodes1, edges1=edges1,
                         label=label, dtype=object)
                print(f'[INFO] <main> save the graph information into numpy file: [{str(cnt)}] ' + savename + RunTime())
                print('=====================================================')
    return

# construct graphs
def constructgraphs():
    cnt = 0
    for root, ds, fs in os.walk(testPath):
        for file in fs:
            if ('_mid.npz' == file[-8:]):
                filename = os.path.join(root, file).replace('\\', '/')
                savename = filename.replace('_mid.npz', '_np.npz')
                cnt += 1
                print('[INFO] <main> Process the graph numpy file: [' + str(cnt) + '] ' + filename + RunTime())
                nodes, edges, nodes0, edges0, nodes1, edges1, label = construct_graphs.ReadFile(filename)
                nodeDict, edgeIndex, edgeAttr = construct_graphs.ProcEdges(edges)
                nodeAttr, nodeInvalid = construct_graphs.ProcNodes(nodes, nodeDict)
                np.savez(savename, edgeIndex=edgeIndex, edgeAttr=edgeAttr, nodeAttr=nodeAttr, label=label,
                         nodeDict=nodeDict)
                print(
                    '[INFO] <main> save the graph information into numpy file: [' + str(
                        cnt) + '] ' + savename + RunTime())
                print('-----------------------------------------------------')
    return

# get dataset
def GetDataset(path=None):
    '''
    Get the dataset from numpy data files.
    :param path: the path used to store numpy dataset.
    :return: dataset - list of torch_geometric.data.Data
    '''

    # check.
    if None == path:
        print('[Error] <GetDataset> The method is missing an argument \'path\'!')
        return [], []

    # contruct the dataset.
    dataset = []
    files = []
    for root, _, filelist in os.walk(path):
        for file in filelist:
            if file[-7:] == '_np.npz':
                # read a numpy graph file.
                graph = np.load(os.path.join(root, file), allow_pickle=True)
                files.append(os.path.join(root, file[:-7]))
                # sparse each element.
                edgeIndex = torch.tensor(graph['edgeIndex'], dtype=torch.long)
                nodeAttr = torch.tensor(graph['nodeAttr'], dtype=torch.float)
                edgeAttr = torch.tensor(graph['edgeAttr'], dtype=torch.float)
                label = torch.tensor(graph['label'], dtype=torch.long)
                # construct an instance of torch_geometric.data.Data.
                data = Data(edge_index=edgeIndex, x=nodeAttr, edge_attr=edgeAttr, y=label)
                # append the Data instance to dataset.
                dataset.append(data)

    if (0 == len(dataset)):
        print(f'[ERROR] Fail to load data from {path}')

    return dataset, files

# main
def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = PGCN(num_node_features=dim_features)
    model.load_state_dict(torch.load(mdlsPath + f'/model_{_NETXARCHT_}_{dim_features}_10.pth'))
    dataset, files = GetDataset(path=testPath)
    dataloader = DataLoader(dataset, batch_size=_BATCHSIZE_, shuffle=False)
    testAcc, testPred, testLabel = PGCNTest(model, dataloader)

    filename = logsPath + '/test_results.txt'
    fp = open(filename, 'w')
    fp.write(f'filename,prediction\n')
    for i in range(len(files)):
        fp.write(f'{files[i]},{testPred[i]}\n')
    fp.close()

    return

if __name__ == '__main__':
    logfile = 'test.txt'
    if os.path.exists(os.path.join(logsPath, logfile)):
        os.remove(os.path.join(logsPath, logfile))
    elif not os.path.exists(logsPath):
        os.makedirs(logsPath)
    sys.stdout = Logger(os.path.join(logsPath, logfile))
    # --------------------------------------------------
    extractgraphs()
    # check [mid error]
    constructgraphs()
    # check [np error]
    main()



