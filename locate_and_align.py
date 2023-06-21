import json, os, sys

path = sys.argv[1]

funcInfo = []	#(filename, lineStart, lineEnd)

f = open(path+'cpg_a.txt')
results = f.read()
f.close()
resultList = json.loads(results)

for item in resultList:
	if '_1' in item.keys() and '_2' in item.keys() \
		and '_3' in item.keys() and '_4' in item.keys():
		i = item['_2'].rfind('/a/')
		funcInfo.append((item['_2'][i:], item['_3'], item['_4']))

f = open(path+'cpg_b.txt')
results = f.read()
f.close()
resultList = json.loads(results)

for item in resultList:
	if '_1' in item.keys() and '_2' in item.keys() \
		and '_3' in item.keys() and '_4' in item.keys():
		i = item['_2'].rfind('/b/')
		funcInfo.append((item['_2'][i:], item['_3'], item['_4']))

os.system('rm '+path+'diff.txt')
os.system('diff -brN -U 0 -p '+path+'a/ '+path+'b/ >> '+path+'diff.txt')

f = open(path+'diff.txt')

hunkInfo = []	#(filename, lineStart, lineEnd)
filename1 = ''
filename2 = ''
while 1:
	line = f.readline()
	if not line:	break
	#print(line)
	if line[:len('diff -brN')] == 'diff -brN':
		filename1 = line.split()[-2]
		filename2 = line.split()[-1]
		filename1 = filename1[filename1.find('/a/'):]
		filename2 = filename2[filename2.find('/b/'):]
	elif line.count('@') == 4:
		i = line.find('@@ ')
		j = line.find(' @@')
		info = line[i+3:j]

		i = info.find(' ')
		info_a = info[:i]
		info_b = info[i+1:]

		i = info_a.find(',')
		if i < 0:
			hunkInfo.append((filename1,int(info_a[1:]),int(info_a[1:])))
		else:
			if int(info_a[i+1:]) > 0:
				hunkInfo.append((filename1,int(info_a[1:i]),int(info_a[1:i])+int(info_a[i+1:])-1))
			else:
				hunkInfo.append((filename1,int(info_a[1:i]),0))
			
		i = info_b.find(',')
		if i < 0:
			hunkInfo.append((filename2,int(info_b[1:]),int(info_b[1:])))
		else:
			if int(info_b[i+1:]) > 0:
				hunkInfo.append((filename2,int(info_b[1:i]),int(info_b[1:i])+int(info_b[i+1:])-1))
			else:
				hunkInfo.append((filename2,int(info_b[1:i]),0))
f.close()

#print(hunkInfo)

locate_flag = [0 for i in range(len(funcInfo))]
align_flag = [0 for i in range(len(hunkInfo))]
for i in range(len(funcInfo)):
	for j in range(len(hunkInfo)):
		if funcInfo[i][0] == hunkInfo[j][0]:
			if (hunkInfo[j][2] != 0 and max(funcInfo[i][1], hunkInfo[j][1]) <= min(funcInfo[i][2], hunkInfo[j][2]))\
				or (hunkInfo[j][2] == 0 and funcInfo[i][1] <= hunkInfo[j][1] and hunkInfo[j][1] <= funcInfo[i][2]):
				locate_flag[i] = 1
				align_flag[j] = 1

filename = []
fileContent = []

files = os.listdir(path+'a/')
for file in files:
	if file in ['.DS_store', '.DS_Store']:	continue
	f = open(path+'a/'+file)
	filename.append('/a/'+file)

	lines = ['']
	while 1:
		line = f.readline()
		if not line:	break
		lines.append(line)
	f.close()

	fileContent.append(lines)

files = os.listdir(path+'b/')
for file in files:
	if file in ['.DS_store', '.DS_Store']:	continue
	f = open(path+'b/'+file)
	filename.append('/b/'+file)

	lines = ['']
	while 1:
		line = f.readline()
		if not line:	break
		lines.append(line)
	f.close()

	fileContent.append(lines)


for i in range(len(locate_flag)):
	if locate_flag[i] == 0:
		idx = filename.index(funcInfo[i][0])
		for j in range(funcInfo[i][1], funcInfo[i][2]+1):
			fileContent[idx][j] = '\n'

for i in range(0, len(hunkInfo), 2):
#	if align_flag[i] == 1 or align_flag[i+1] == 1:
#		print(hunkInfo[i], hunkInfo[i+1])
	if hunkInfo[i][2] == 0:
		if hunkInfo[i][0] not in filename:
			filename.append(hunkInfo[i][0])
			suffix = '\n'*(hunkInfo[i+1][2]-hunkInfo[i+1][1]+1)
			fileContent.append(suffix)
		else:
			idx = filename.index(hunkInfo[i][0])
			suffix = '\n'*(hunkInfo[i+1][2]-hunkInfo[i+1][1]+1)
			fileContent[idx][hunkInfo[i][1]] = fileContent[idx][hunkInfo[i][1]] + suffix
	elif hunkInfo[i+1][2] == 0:
		if hunkInfo[i+1][0] not in filename:
			filename.append(hunkInfo[i+1][0])
			suffix = '\n'*(hunkInfo[i][2]-hunkInfo[i][1]+1)
			fileContent.append(suffix)
		else:
			idx = filename.index(hunkInfo[i+1][0])
			suffix = '\n'*(hunkInfo[i][2]-hunkInfo[i][1]+1)
			fileContent[idx][hunkInfo[i+1][1]] = fileContent[idx][hunkInfo[i+1][1]] + suffix
	else:
		gap = (hunkInfo[i][2]-hunkInfo[i][1]) - (hunkInfo[i+1][2]-hunkInfo[i+1][1])
		#print(gap)
		if gap < 0:
			idx = filename.index(hunkInfo[i][0])
			suffix = '\n'*(-gap)
			fileContent[idx][hunkInfo[i][2]] = fileContent[idx][hunkInfo[i][2]] + suffix
		elif gap > 0:
			idx = filename.index(hunkInfo[i+1][0])
			suffix = '\n'*(gap)
			fileContent[idx][hunkInfo[i+1][2]] = fileContent[idx][hunkInfo[i+1][2]] + suffix

for i in range(len(filename)):
	os.system('rm '+path[:-1]+filename[i])
	f = open(path[:-1]+filename[i], 'a+')
	for line in fileContent[i]:
		f.write(line)
	f.close()
