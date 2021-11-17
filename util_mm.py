#!/usr/bin/env python
import yaml

def createModelList(input_lines, modelList, modelListRaw):

	# Model contains True atoms, if missing they are False
	modelListTemp =  input_lines.strip().split(" ")

	# Add "a:" prefix
	for i in range(len(modelListTemp)):
		modelListRaw.append(str(modelListTemp[i]))
		modelList.append("a:" + str(modelListTemp[i]))
		#modelList[i] = "a:" + str(modelList[i])


def readIntervalDict(file_name):

	tempIntervals = {}

	# Read Yaml file with intervals
	with open(file_name, "r") as f:
		yamlDoc = yaml.safe_load(f)

		for key1, val1 in yamlDoc.items():

			tempIvs = {}
			# Move dic to list elements
			for key2, val2 in val1.items():
				# tempIvs.append(val2)
				tempIvs[str(key2)] = val2
			tempIntervals[str(key1)] = tempIvs

	return tempIntervals

# def createIntervalDict(input_lines):
#
# 	intervalList = {}
#
# 	# Strips the newline character
# 	for line in input_lines:
#
# 		lineT = line.strip()
# 		lineArray = lineT.split(': ')
# 		atom = str(lineArray[0])
# 		intervals = lineArray[1].split(' ')
# 		intervalList[atom] = intervals
#
#
# 	return intervalList

def createTempRel():

	tempRels = {}
	tempRels["(b)"] = "before"
	tempRels["(B)"] = "after"
	tempRels["(m)"] = "meets"
	tempRels["(M)"] = "meetBy"
	tempRels["(o)"] = "overlaps"
	tempRels["(O)"] = "overlappedBy"
	tempRels["(s)"] = "starts"
	tempRels["(S)"] = "startedBy"
	tempRels["(f)"] = "finishes"
	tempRels["(F)"] = "finishedBy"
	tempRels["(d)"] = "during"
	tempRels["(D)"] = "contains"
	tempRels["(e)"] = "equal"

	return tempRels


def createClauseList(input_lines, tempRels):

	variabls = 0
	clauses = 0
	clauseList = []
	
	# Strips the newline character
	for line in input_lines:
		
		lineT = line.strip()
		lineArray = lineT.split(' ')
		if(lineArray[0]=='p'):
			# Header
			variabls = int(lineArray[2])
			clauses = int(lineArray[3])
			print("CNF with variables: " + str(variabls) + ", clauses: " + str(clauses))
		elif(lineArray[0]=='c'):
			continue
		else:
			# temporal clause (several temporal relations separated by ;)
			if(';' in lineT):
				lineArray2 = lineT.split(';')
				tempTuple = tuple(lineArray2)

			# Standard clause
			else:
				tempTuple = tuple(lineArray)

			clauseList.append(tempTuple)
			
	return clauseList
	


