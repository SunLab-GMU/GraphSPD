import os
import sys

owner = sys.argv[1]
repo = sys.argv[2]
commit_ID = sys.argv[3]

# create a folder to store pre- and post-patch version files
if not os.path.exists('./ab_file/'):
	os.mkdir('./ab_file/')
if not os.path.exists('./repo/'):
	os.mkdir('./repo/')

if not os.path.exists('./ab_file/'+commit_ID):
	os.system('mkdir ./ab_file/'+commit_ID)

a = []
b = []

# read and parse the raw patch
f = open('./raw_patch/'+commit_ID)
content = f.read()
f.close()

i = content.find("diff --git")
new_content = content[:i]
content = content[i:]

# deal with the code difference one by one
while 'diff --git ' in content:

	i = content.find(' a/')
	j = content.find(' b/')
	k = content.find('\n')

	file_a = content[i+3:]
	i = file_a.find(' ')
	file_a = file_a[:i]
	file_b = content[j+3:k]

	if not os.path.exists('./ab_file/'+commit_ID+'/a'):
		os.system('mkdir ./ab_file/'+commit_ID+'/a')
	if not os.path.exists('./ab_file/'+commit_ID+'/b'):
		os.system('mkdir ./ab_file/'+commit_ID+'/b')

	# retrive and download the pre- and post-patch files
	if file_a not in a:
		a.append(file_a)
	if file_b not in b:
		b.append(file_b)

	i = content.find('\ndiff --git ')
	if i > 0:
		content = content[i+1:]
	else:
		if not os.path.exists('./repo/'+repo):
			os.system('cd ./repo; git clone https://github.com/'+owner+'/'+repo+'.git')
		
		# post-patch files (version b)
		os.system('cd ./repo/'+repo+'; git reset --hard '+commit_ID)
		for f_b in b:
			os.system('cp ./repo/'+repo+'/'+f_b+' ./ab_file/'+commit_ID+'/b/')
		
		# pre-patch files (version a)
		out = os.popen('cd ./repo/'+repo+'; git rev-list --parents -n 1 '+commit_ID).read()
		commit_a = out[out.find(' ')+1:].rstrip()
		os.system('cd ./repo/'+repo+'; git reset --hard '+commit_a)
		for f_a in a:
			os.system('cp ./repo/'+repo+'/'+f_a+' ./ab_file/'+commit_ID+'/a/')
		break



