import os, operator, sys
from collections import defaultdict 
import copy

# This class represents a directed graph 
# using adjacency list representation 
class Graph: 

	def __init__(self, vertices): 
		# No. of vertices 
		self.V = vertices 
		
		# default dictionary to store graph 
		self.graph = defaultdict(list) 

		self.paths = []

	# function to add an edge to graph 
	def addEdge(self, u, v): 
		self.graph[u].append(v) 

	'''A recursive function to print all paths from 'u' to 'd'. 
	visited[] keeps track of vertices in current path. 
	path[] stores actual vertices and path_index is current 
	index in path[]'''
	def printAllPathsUtil(self, u, d, visited, path): 

		# Mark the current node as visited and store in path 
		visited[u]= True
		path.append(u) 

		# If current vertex is same as destination, then print 
		# current path[] 
		if u == d: 
			#print(path)
			self.paths.append(copy.deepcopy(path)) 
		else: 
			# If current vertex is not destination 
			# Recur for all the vertices adjacent to this vertex 
			for i in self.graph[u]: 
				if visited[i]== False: 
					self.printAllPathsUtil(i, d, visited, path) 
					
		# Remove current vertex from path[] and mark it as unvisited 
		path.pop() 
		visited[u]= False


	# Prints all paths from 's' to 'd' 
	def printAllPaths(self, s, d): 

		# Mark all the vertices as not visited 
		visited =[False]*(self.V) 

		# Create an array to store paths 
		path = [] 

		# Call the recursive helper function to print all paths 
		self.printAllPathsUtil(s, d, visited, path) 

def reduceNoise(nodes, edges, N):
	dictNode = {}
	for i in range(len(nodes)):
		dictNode[nodes[i][0]] = i
	dictNodeInv = {v: k for k, v in dictNode.items()}

	# Create a graph given in the above diagram 
	g = Graph(len(nodes))

	for e in edges:
		if e[2] in ['CDG', 'DDG'] and e[0] in dictNode and e[1] in dictNode:
			g.addEdge(dictNode[e[0]], dictNode[e[1]])
			g.addEdge(dictNode[e[1]], dictNode[e[0]])

	# find all nodes that are patched related nodes (i.e., not context nodes)
	patchedNodes = []
	for n in nodes:
		if n[-1] != 0:
			patchedNodes.append(n)

	sliceNodes = []
	sliceEdges = []

	# check every two patched related nodes
	for i in range(len(patchedNodes)):
		for j in range(i, len(patchedNodes)):
			g.printAllPaths(dictNode[patchedNodes[i][0]], dictNode[patchedNodes[j][0]])
			for p in g.paths:
				for k in range(len(p)-1):
					sliceNodes.append(getNode(dictNodeInv[p[k]], nodes))
					sliceNodes.append(getNode(dictNodeInv[p[k+1]], nodes))
					for e in edges:
						if (dictNodeInv[p[k]] == e[0] and dictNodeInv[p[k+1]] == e[1])\
							or (dictNodeInv[p[k]] == e[1] and dictNodeInv[p[k+1]] == e[0]):
							sliceEdges.append(e)

	# iterate N times for remaining nodes
	for n1 in patchedNodes:
		for e in edges:
			if n1[0] in [e[0], e[1]] and e[2][:3] in ['CDG', 'DDG']:
				for n2 in nodes:
					if n2[0] in [e[0], e[1]]:
						sliceNodes.append(n2)
						nodes.remove(n2)
						sliceEdges.append(e)

	for i in range(N-1):
		for n1 in nodes:
			for e in edges:
				if n1[0] in [e[0], e[1]] and e[2][:3] in ['CDG', 'DDG']:
					for n2 in nodes:
						if n2[0] in [e[0], e[1]]:
							sliceNodes.append(n2)
							nodes.remove(n2)
							sliceEdges.append(e)

	sliceNodes = list(set(sliceNodes+patchedNodes))
	sliceEdges = list(set(sliceEdges))

	return sliceNodes, sliceEdges

def getNode(k, nodes):
	for n in nodes:
		if n[0] == k:
			return n
	return None


def importCPG(path):
	nodesByFunc = {}
	edgesByFunc = {}
	files = os.listdir(path)
	for f in files:
		if f == '.DS_Store': continue
		content = open(path+'/'+f, errors='ignore').read()
		if 'LINE_NUMBER' not in content:	continue
		lines = content[:-1].split('--------\n')
		funcName = lines[0][len('digraph'):-1]
		if len(funcName) == 0:	continue

		nodesByFunc[funcName] = lines[1].split('\n')
		edgesByFunc[funcName] = lines[2].split('\n')

	return nodesByFunc, edgesByFunc

def nodeAttr(node):
	i = node.find(',')
	return node[:i], node[i+1:]

def edgeAttr(edge):
	i = edge.find(',')
	j = edge.rfind(',')
	return edge[:i], edge[i+1:j], edge[j+1:]

'''
(RETURN,...) <--AST-- (PARSER_TYPE_NAME,IfStatement)
(RETURN,...) <--AST-- (PARSER_TYPE_NAME,ElseStatement)
(RETURN,...) <--AST-- (BLOCK,,) <--AST-- (PARSER_TYPE_NAME,IfStatement)
(RETURN,...) <--AST-- (BLOCK,,) <--AST-- (PARSER_TYPE_NAME,ElseStatement)
(PARSER_TYPE_NAME,GotoStatement) ...
... (PARSER_TYPE_NAME,SwitchStatement)
'''
def ifCondJump(node, nodes, edges):
	#print(node[0], node[1])
	if '(PARSER_TYPE_NAME,IfStatement)' in node[1] or \
		'(PARSER_TYPE_NAME,ElseStatement)' in node[1] or \
		'(PARSER_TYPE_NAME,SwitchStatement)' in node[1]:
		for e in edges:
			if e[0] == node[0] and e[2] == 'AST':
				for n in nodes:
					if e[1] == n[0]:
						if '(RETURN,...)' in n[1] or \
						   '(PARSER_TYPE_NAME,GotoStatement)' in n[1]:
						   return True
						elif '(BLOCK,,)' in n[1]:
							for e2 in edges:
								if e2[0] == n[0] and e[2] == 'AST':
									for n2 in nodes:
										if e2[1] == n2[0]:
											if '(RETURN,...)' in n2[1] or \
											   '(PARSER_TYPE_NAME,GotoStatement)' in n2[1]:
												return True
	return False

# check if forward data slicing results are emprty
def ifNoneDataFrwd(node, edges):
	for e in edges:
		if e[0] == node[0] and e[2][:3] == 'DDG':
			return False
	return True

def ifSameLine(n1, n2):
	nodeInfo1 = n1[1]
	nodeInfo2 = n2[1]

	i = nodeInfo1.find('(CODE,')
	j = nodeInfo1[i:].find('),(')
	if i>0 and j>0:
		num1 = nodeInfo1[i+len('(CODE,'):i+j]
	else:
		num1 = '404NotFound'
	i = nodeInfo2.find('(CODE,')
	j = nodeInfo2[i:].find('),(')
	if i>0 and j>0:	
		num2 = nodeInfo2[i+len('(CODE,'):i+j]
	else:
		num2 = '404NotFound'
	if (num1 in num2) or (num2 in num1):
		
		return True
	return False

def slice(Anodes, Aedges, Bnodes, Bedges, path, nodeIDstart):
	tmpEdges = []
	for e in Aedges:
		edgeType = edgeAttr(e)[2]
		if edgeType[:3] in ['AST', 'CDG']:
			tmpEdges.append(e)
		elif edgeType[:3] == 'DDG' and len(edgeType) > 3 and edgeType[3:] != '<RET>' and any(c.isalpha() for c in edgeType[3:]):
			tmpEdges.append(e)
	Aedges = tmpEdges 

	tmpEdges = []
	for e in Bedges:
		edgeType = edgeAttr(e)[2]
		if edgeType[:3] in ['AST', 'CDG']:
			tmpEdges.append(e)
		elif edgeType[:3] == 'DDG' and len(edgeType) > 3 and edgeType[3:] != '<RET>' and any(c.isalpha() for c in edgeType[3:]):
			tmpEdges.append(e)
	Bedges = tmpEdges 

	nodeId = nodeIDstart-1
	dictA = {}
	dictB = {}

	CtxNodes = []
	PreNodes = []
	PstNodes = []

	for Bn in Bnodes:
		for An in Anodes:
			AnodeId, AnodeInfo = nodeAttr(An)
			BnodeId, BnodeInfo = nodeAttr(Bn)
			if AnodeInfo.replace('/a/','/v/').replace('/b/','/v/') == BnodeInfo.replace('/a/','/v/').replace('/b/','/v/') and AnodeInfo and len(AnodeInfo) > 0:
				dictA[AnodeId] = nodeId
				dictB[BnodeId] = nodeId
				CtxNodes.append((nodeId, AnodeInfo.replace('/a/','/v/').replace('/b/','/v/'), 0))
				nodeId -= 1

	for Bn in Bnodes:
		BnodeId, BnodeInfo = nodeAttr(Bn)
		if BnodeId not in dictB.keys() and BnodeInfo and len(BnodeInfo) > 0:
			dictB[BnodeId] = nodeId
			PstNodes.append((nodeId, BnodeInfo.replace('/a/','/v/').replace('/b/','/v/'), 1))
			nodeId -= 1

	for An in Anodes:
		AnodeId, AnodeInfo = nodeAttr(An)
		if AnodeId not in dictA.keys() and AnodeInfo and len(AnodeInfo) > 0:
			dictA[AnodeId] = nodeId
			PreNodes.append((nodeId, AnodeInfo.replace('/a/','/v/').replace('/b/','/v/'), -1))
			nodeId -= 1

	newAedges = []
	newBedges = []

	for Be in Bedges:
		nodeId1, nodeId2, edgeInfo = edgeAttr(Be)
		newBedges.append((dictB[nodeId1], dictB[nodeId2], edgeInfo, 0))

	for Ae in Aedges:
		nodeId1, nodeId2, edgeInfo = edgeAttr(Ae)
		newAedges.append((dictA[nodeId1], dictA[nodeId2], edgeInfo, 0))

	CtxEdges = list(set(newAedges)&set(newBedges))
	PreEdges = []
	PstEdges = []

	newAedges = list(set(newAedges)-set(CtxEdges))
	newBedges = list(set(newBedges)-set(CtxEdges))

	for Be in newBedges:
		PstEdges.append((Be[0], Be[1], Be[2], 1))

	for Ae in newAedges:
		PreEdges.append((Ae[0], Ae[1], Ae[2], -1))

	invDictA = {v: k for k, v in dictA.items()}
	invDictB = {v: k for k, v in dictB.items()}


	CtxEdges1 = CtxEdges[:]
	CtxNodes1 = CtxNodes[:]
	backNodes1 = PreNodes[:] + PstNodes[:] 
	backEdges1 = PreEdges[:] + PstEdges[:]

	it_N = 1
	for i in range(it_N):
		cnt = len(backNodes1) + len(backEdges1)
		for n2 in backNodes1[:]:
			# nodeID = n[0]
			for e in CtxEdges1+backEdges1:
				# nodeId2 = e[1]
				if e[1] == n2[0] and e[2][:3] in ['CDG']:
					for n1 in CtxNodes1[:]:
						if e[0] == n1[0]:
							CtxNodes1.remove(n1)
							backNodes1.append(n1)
							if e in CtxEdges1[:]:
								CtxEdges1.remove(e)
							if e not in backEdges1:
								backEdges1.append(e)
		if cnt == len(backNodes1) + len(backEdges1):
			break


	CtxEdges2 = CtxEdges[:]
	CtxNodes2 = CtxNodes[:]
	backNodes2 = PreNodes[:] + PstNodes[:] 
	backEdges2 = PreEdges[:] + PstEdges[:]

	for i in range(it_N):
		cnt = len(backNodes2) + len(backEdges2)
		for n2 in backNodes2[:]:
			# nodeID = n[0]
			for e in CtxEdges2+backEdges2:
				# nodeId2 = e[1]
				if e[1] == n2[0] and e[2][:3] in ['DDG']:
					for n1 in CtxNodes2[:]:
						if e[0] == n1[0]:
							CtxNodes2.remove(n1)
							backNodes2.append(n1)
							if e in CtxEdges2[:]:
								CtxEdges2.remove(e)
							if e not in backEdges2:
								backEdges2.append(e)
		if cnt == len(backNodes2) + len(backEdges2):
			break

	backNodes = list(set(backNodes1+backNodes2))
	backEdges = list(set(backEdges1+backEdges2))

	CtxEdges2 = CtxEdges[:]
	CtxNodes2 = CtxNodes[:]
	frwdNodes2 = PreNodes[:] + PstNodes[:] 
	frwdEdges2 = PreEdges[:] + PstEdges[:]

	enforceFrwdNodes = []
	for i in range(it_N):
		cnt = len(frwdNodes2) + len(frwdEdges2)
		for n1 in frwdNodes2[:]:
			if ifCondJump(n1, CtxNodes2+frwdNodes2, CtxEdges2+frwdEdges2)\
				and ifNoneDataFrwd(n1, CtxEdges2+frwdEdges2):
				newFrwdNodes = []
				for e in CtxEdges2+frwdEdges2:
					if e[1] == n1[0] and e[2][:3] in ['DDG']:
						for n2 in CtxNodes2[:]:
							if e[0] == n2[0] and n2 not in newFrwdNodes:
								newFrwdNodes.append(n2)
				if len(newFrwdNodes) == 0:
					enforceFrwdNodes.append(n1)
				else:
					for n2 in newFrwdNodes:
						for e in CtxEdges2+frwdEdges2:
							# nodeId2 = e[1]
							if e[0] == n2[0] and e[2][:3] in ['DDG']:
								for n3 in CtxNodes2[:]:
									if e[1] == n3[0]:
										CtxNodes2.remove(n3)
										frwdNodes2.append(n3)
										if e in CtxEdges2[:]:
											CtxEdges2.remove(e)
										if e not in frwdEdges2:
											frwdEdges2.append(e)	
			else:
				for e in CtxEdges2+frwdEdges2:
					# nodeId2 = e[1]
					if e[0] == n1[0] and e[2][:3] in ['DDG']:
						for n2 in CtxNodes2[:]:
							if e[1] == n2[0]:
								CtxNodes2.remove(n2)
								frwdNodes2.append(n2)
								if e in CtxEdges2[:]:
									CtxEdges2.remove(e)
								if e not in frwdEdges2:
									frwdEdges2.append(e)
		if cnt == len(frwdNodes2) + len(frwdEdges2):
			break

	CtxEdges1 = CtxEdges[:]
	CtxNodes1 = CtxNodes[:]
	frwdNodes1 = PreNodes[:] + PstNodes[:] 
	frwdEdges1 = PreEdges[:] + PstEdges[:]

	for i in range(it_N):
		cnt = len(frwdNodes1) + len(frwdEdges1)
		for n1 in frwdNodes1[:]:
			if ifCondJump(n1, CtxNodes1+frwdNodes1, CtxEdges1+frwdEdges1)\
				and ifNoneDataFrwd(n1, CtxEdges1+frwdEdges1)\
				and n1 not in enforceFrwdNodes:
				continue
			else:
				for e in CtxEdges1+frwdEdges1:
					# nodeId2 = e[1]
					if e[0] == n1[0] and e[2][:3] in ['CDG']:
						for n2 in CtxNodes1[:]:
							if e[1] == n2[0]:
								CtxNodes1.remove(n2)
								frwdNodes1.append(n2)
								if e in CtxEdges1[:]:
									CtxEdges1.remove(e)
								if e not in frwdEdges1:
									frwdEdges1.append(e)
		if cnt == len(frwdNodes1) + len(frwdEdges1):
			break

	frwdNodes = list(set(frwdNodes1+frwdNodes2))
	frwdEdges = list(set(frwdEdges1+frwdEdges2))
	#print('forward: ', len(frwdNodes), len(frwdEdges))

	sliceNodes = list(set(backNodes+frwdNodes))
	sliceEdges = list(set(backEdges+frwdEdges))

	CtxEdges = list(set(CtxEdges)-set(sliceEdges))
	CtxNodes = list(set(CtxNodes)-set(sliceNodes))

	# AST slice and makeup
	while 1:
		cnt = len(sliceNodes) + len(sliceEdges)
		for n2 in sliceNodes[:]:
			for e in CtxEdges[:]+sliceEdges[:]:
				if n2[0] in [e[0], e[1]] and e[2][:3] == 'AST':
					for n1 in CtxNodes[:]:
						if n1[0] in [e[0], e[1]] and ifSameLine(n1, n2):
							#print("123321", n1, n2)
							CtxNodes.remove(n1)
							sliceNodes.append(n1)
							if e in CtxEdges:
								CtxEdges.remove(e)
							if e not in sliceEdges:
								sliceEdges.append(e)
		if cnt == len(sliceNodes) + len(sliceEdges):
			break


	sliceNodes = list(set(sliceNodes))
	sliceEdges = list(set(sliceEdges))
	
	# make up nodes since there are some lonely edges
	for e in sliceEdges[:]:
		for n in CtxNodes[:]:
			if n[0] in [e[0], e[1]] and e[2][:3] in ['AST']:
				CtxNodes.remove(n)
				sliceNodes.append(n)


	# first remove (merge) the redundant nodes
	for e in sliceEdges[:]:
		flag_found = 0
		for n in sliceNodes:
			if n[0] == e[0]:
				flag_found += 1
			if n[0] == e[1]:
				flag_found += 1
		if flag_found < 2:
			print('!!!Oops, missing nodes!!!!!', e)

	slimNodes = []
	slimEdges = []

	lineNum_list = []
	nodeID_lineNum = {}
	lineNum_nodeID = {}
	lineNum_code = {}
	lineNum_label = {}
	for n in sliceNodes:
		#print(n)
		i = n[1].find('(CODE,')
		if i == -1:
			continue
		j = n[1][i:].find('),(')
		if j == -1:
			code = n[1][i+len('(CODE,'):-1]
		else:
			code = n[1][i+len('(CODE,'):i+j]

		if len(code) == 0:
			continue

		i = n[1].find('(LINE_NUMBER,')
		if i == -1:
			continue

		if n[-1] == 0:		
			pre = ''
		elif n[-1] == 1:	
			pre = '+'
		else: 
			pre = '-'

		j = n[1][i:].find('),(')
		if j == -1:
			line_num = pre + n[1][i+len('(LINE_NUMBER,'):-1]
		else:
			line_num = pre + n[1][i+len('(LINE_NUMBER,'):i+j]

		nodeID_lineNum[n[0]] = line_num

	
		if line_num not in lineNum_code.keys():
			lineNum_code[line_num] = code
			lineNum_nodeID[line_num] = n[0]
			lineNum_label[line_num] = n[-1]
		else:
			if len(code) >= len(lineNum_code[line_num]):
				lineNum_code[line_num] = code
				lineNum_nodeID[line_num] = n[0]
				lineNum_label[line_num] = n[-1]
	
	lineNum_list = list(lineNum_code.keys())
	lineNum_list.sort()
	#print(lineNum_list)
	oldNum_newNum = {}
	i = 0
	while i < len(lineNum_list):
		line_cnt = lineNum_code[lineNum_list[i]].count('\\n')
		flag_cnt = 0
		oldNum_newNum[lineNum_list[i]] = lineNum_list[i]
		if line_cnt > 0:
			for j in range(1,line_cnt+1):
				if lineNum_list[i].isnumeric():
					if str(int(lineNum_list[i])+j) in lineNum_list and \
						lineNum_code[str(int(lineNum_list[i])+j)] in lineNum_code[lineNum_list[i]]:
						oldNum_newNum[str(int(lineNum_list[i])+j)] = lineNum_list[i]
						flag_cnt += 1
				else:
					if lineNum_list[i][0]+str(int(lineNum_list[i][1:])+j) in lineNum_list and \
						lineNum_code[lineNum_list[i][0]+str(int(lineNum_list[i][1:])+j)] in lineNum_code[lineNum_list[i]]:
						oldNum_newNum[lineNum_list[i][0]+str(int(lineNum_list[i])+j)] = lineNum_list[i]
						flag_cnt += 1
		i += (flag_cnt + 1)

	for line_num in list(set(oldNum_newNum.values())):
		slimNodes.append((lineNum_nodeID[line_num], lineNum_label[line_num], line_num, lineNum_code[line_num]))

	for e in sliceEdges:

		if e[0] in nodeID_lineNum.keys() and e[1] in nodeID_lineNum.keys()\
			and nodeID_lineNum[e[0]] in oldNum_newNum.keys() and nodeID_lineNum[e[1]] in oldNum_newNum.keys()\
			and oldNum_newNum[nodeID_lineNum[e[0]]] in lineNum_nodeID.keys()\
			and oldNum_newNum[nodeID_lineNum[e[1]]] in lineNum_nodeID.keys():

			node_from = lineNum_nodeID[oldNum_newNum[nodeID_lineNum[e[0]]]]
			node_to = lineNum_nodeID[oldNum_newNum[nodeID_lineNum[e[1]]]]

			if node_from != node_to:
				slimEdges.append((node_from,node_to,e[2],e[-1]))

		else:
			continue

	slimNodes = list(set(slimNodes))
	slimEdges = list(set(slimEdges))

	ctxID_lineNum = {}

	for n in slimNodes[:]:
		if '-'+n[2] in lineNum_code.keys() and n[3] in lineNum_code['-'+n[2]]\
			and '+'+n[2] in lineNum_code.keys() and n[3] in lineNum_code['+'+n[2]]:
			ctxID_lineNum[n[0]] = n[2]
			slimNodes.remove(n)
			IDA = lineNum_nodeID['-'+n[2]]
			IDB = lineNum_nodeID['+'+n[2]]
			for e in slimEdges[:]:
				if e[0] == n[0]: 
					if e[-1] == -1:
						slimEdges.remove(e)
						if IDA != e[1]:
							slimEdges.append((IDA,e[1],e[2],e[3]))
					elif e[-1] == 1:
						slimEdges.remove(e)
						if IDB != e[1]:
							slimEdges.append((IDB,e[1],e[2],e[3]))
				if e[1] == n[0]:
					if e[-1] == -1:
						slimEdges.remove(e)
						if e[0] != IDA:
							slimEdges.append((e[0],IDA,e[2],e[3]))
					elif e[-1] == 1:
						slimEdges.remove(e)
						if e[0] != IDB:
							slimEdges.append((e[0],IDB,e[2],e[3]))

	slimEdges = list(set(slimEdges))


	# remove AST 
	usedNodes = []
	for e in slimEdges[:]:
		if e[2] == 'AST':
			slimEdges.remove(e)
		else:
			usedNodes.append(e[0])
			usedNodes.append(e[1])

	# make up missing nodes
	for e in slimEdges[:]:
		flag_found = 0
		for n in slimNodes:
			if n[0] == e[0]:
				flag_found += 1
			if n[0] == e[1]:
				flag_found += 1
		if flag_found < 2:
			slimEdges.remove(e)

	for e in slimEdges[:]:
		flag_found = 0
		for n in slimNodes:
			if n[0] == e[0]:
				flag_found += 1
			if n[0] == e[1]:
				flag_found += 1
		if flag_found < 2:
			print('Oops, missing nodes!!!!!', e)

	# remove floating nodes
	for n in slimNodes[:]:
		if n[0] not in usedNodes and n[1] == 0:
			slimNodes.remove(n)

	node_type = {}
	simple_edge = []
	for e in slimEdges:
		simple_edge.append((e[0], e[1]))
		if e[0] not in node_type.keys():
			node_type[e[0]] = e[2][:1]
		else:
			if e[2][:1] not in node_type.values():
				node_type[e[0]] += e[2][:1]
		if e[1] not in node_type.keys():
			node_type[e[1]] = e[2][:1]
		else:
			if e[2][:1] not in node_type.values():
				node_type[e[1]] += e[2][:1]


	# rank nodes
	reservedNodes = []
	node_lineNum = {}
	for n in slimNodes:
		if '+' in n[2] or '-' in n[2]:
			node_lineNum[n[0]] = int(n[2][1:])

	for n in slimNodes:
		if n[2].isnumeric():
			tmp_dist = 10000
			for nodeID2 in node_lineNum.keys():
				if (n[0],nodeID2) in simple_edge or (nodeID2, n[0]) in simple_edge:
					tmp_dist = min([tmp_dist, abs(int(n[2])-node_lineNum[nodeID2])])
			reservedNodes.append((n[0],n[1],node_type[n[0]],tmp_dist,n[2],n[3]))
		else:
			reservedNodes.append((n[0],n[1],'-',0,n[2],n[3]))

	return slimEdges, reservedNodes, nodeId


def generateLog(path):
	
	AnodesByFunc, AedgesByFunc = importCPG(path+'/outA/')
	BnodesByFunc, BedgesByFunc = importCPG(path+'/outB/')

	ABFunc = [f for f in AnodesByFunc.keys() if f in BnodesByFunc.keys()]
	AFunc = [f for f in AnodesByFunc.keys() if f not in BnodesByFunc.keys()]
	BFunc = [f for f in BnodesByFunc.keys() if f not in AnodesByFunc.keys()]

	nodeIDstart = -1
	allEdges = []
	allNodes = []

	for f in ABFunc:
		Anodes = AnodesByFunc[f]
		Aedges = AedgesByFunc[f]
		Bnodes = BnodesByFunc[f]
		Bedges = BedgesByFunc[f]

		sliceEdges, sliceNodes, nodeID = slice(Anodes, Aedges, Bnodes, Bedges, path, nodeIDstart)
		if len(sliceEdges) > 0 and len(sliceNodes) > 0:
			allEdges += sliceEdges
			allNodes += sliceNodes
			nodeIDstart = nodeID

	for f in AFunc:
		Anodes = AnodesByFunc[f]
		Aedges = AedgesByFunc[f]
		Bnodes = []
		Bedges = []
		sliceEdges, sliceNodes, nodeID = slice(Anodes, Aedges, Bnodes, Bedges, path, nodeIDstart)
		if len(sliceEdges) > 0 and len(sliceNodes) > 0:
			allEdges += sliceEdges
			allNodes += sliceNodes
			nodeIDstart = nodeID

	for f in BFunc:
		Anodes = []
		Aedges = []
		Bnodes = BnodesByFunc[f]
		Bedges = BedgesByFunc[f]
		sliceEdges, sliceNodes, nodeID = slice(Anodes, Aedges, Bnodes, Bedges, path, nodeIDstart)
		if len(sliceEdges) > 0 and len(sliceNodes) > 0:
			allEdges += sliceEdges
			allNodes += sliceNodes
			nodeIDstart = nodeID

	AEdges = []
	ANodes = []
	BEdges = []
	BNodes = []
	for e in allEdges:
		if e[-1] == 0:
			AEdges.append(e)
			BEdges.append(e)
		elif e[-1] == -1:
			AEdges.append(e)
		else:
			BEdges.append(e)
	for n in allNodes:
		if n[1] == 0:
			ANodes.append(n)
			BNodes.append(n)
		elif n[1] == -1:
			ANodes.append(n)
		else:
			BNodes.append(n)

	if len(allEdges) > 0 or len(allNodes) > 0:

		out_path = path.replace('ab_file', 'testdata')
		print(out_path)
		if not os.path.exists(out_path):	
			os.system('mkdir '+out_path)
		f = open(out_path+'/out_slim_ninf_noast_n1_w.log', 'w+')
		f.write('\n'.join(map(str, allEdges)))
		f.write("\n===========================\n")
		f.write('\n'.join(map(str, allNodes))) 
		f.write("\n---------------------------\n")
		f.write('\n'.join(map(str, AEdges)))
		f.write("\n===========================\n")
		f.write('\n'.join(map(str, ANodes))) 
		f.write("\n---------------------------\n")
		f.write('\n'.join(map(str, BEdges)))
		f.write("\n===========================\n")
		f.write('\n'.join(map(str, BNodes))) 
		f.write("\n")
		f.close()
		return 1
	return 0




def getdirsize(path):
	a_files = os.listdir(path+'/a/')
	b_files = os.listdir(path+'/b/')

	size1 = 0
	for a in a_files:
		size1 += os.path.getsize(path+'/a/'+a)
	size2 = 0
	for b in b_files:
		size2 += os.path.getsize(path+'/b/'+b)
	return max(size1, size2)

if not os.path.exists('./testdata/'):
	os.mkdir('./testdata/')

path = "./ab_file/"
commits = os.listdir(path)
files= (os.path.join(path,cmt) for cmt in commits if cmt != '.DS_Store')
commits = sorted(files, key = getdirsize)

i = 0
for cmt in commits:
	print(cmt)
	if os.path.isfile(cmt+'/cpg_a.txt') and os.path.isfile(cmt+'/cpg_b.txt'):
		os.system('cd ./joern; ./joern-parse .'+cmt+'/a; ./joern-export --repr cpg14 --out .'+cmt+'/outA')
		os.system('cd ./joern; ./joern-parse .'+cmt+'/b; ./joern-export --repr cpg14 --out .'+cmt+'/outB')
		lenA = os.listdir(cmt+'/outA')
		lenB = os.listdir(cmt+'/outB')
		if len(lenA)+len(lenB) > 0:
			i += generateLog(cmt)
			print(i, cmt)
		else:
			os.system('rm -r '+cmt+'/outA')
			os.system('rm -r '+cmt+'/outB')
			print('rm', cmt)


