#!/usr/bin/env python

import getopt, sys
import optparse
import time
from anytree import Node, NodeMixin, RenderTree
import itertools
import yaml

from util_mm import createClauseList, createTempRel, readIntervalDict

class TableauBase(object): 
	test = 1

class TableauNode(TableauBase, NodeMixin): 

	#nodeId = ""
	negated = False
	branchClosed = False
	isLeaf = False
	truthValues = []
	mode = 0
	tempRelation = ""
	tempAtom1 = ""
	tempIntervalsA1 = []
	tempAssignA1 = ""
	tempAtom2 = ""
	tempeIntervalsA2 = []
	tempAssignA2 = ""
	#overwritten = False

	def __init__(self, name,  parent=None, children=None, mode=0):

		# super(TableauBase, self).__init__()
		super(TableauNode, self).__init__()
		self.name = name

		# Check if it is a temporal clause

		self.truthValues = []
		self.negated = False
		self.mode = mode
		self.isLeaf = False
		self.branchClosed = False
		#self.overwritten = False
		self.tempIntervalsA1 = []
		self.tempIntervalsA2 = []

		if('-' in name):
			self.negated = True
		
		self.parent = parent
		if children:  # set children only if given
			self.children = children


	def getParentAtoms(self, atomList):

		if(self.mode==2):
			# Add only positive literals (since negative miss from the model)
			if (not '-' in self.name):
				tKey = self.name.replace('-','')
				if(not tKey in atomList):
					atomList[tKey] = "" # self.name
		if(self.mode==3 and (not self.name in atomList)):
			atomList[self.name] = self.truthValues
		
		if(not self.parent is None):
			self.parent.getParentAtoms(atomList)

	def assignTemporalInfo(self, tempRelations, tempIntervals):

		hasTempRel = False

		# Check for temporar relations such (b)
		for tempRel in tempRelations:
			if(tempRel in self.name):
				self.tempRelation = tempRel
				hasTempRel = True
				break

		# Assign left/right atom x (b) y
		if(len(self.tempRelation)==0):
			if(self.name in tempIntervals):
				self.tempIntervalsA1 = tempIntervals[self.name]
		else:
			# Find left/right atom
			atoms = self.name.split(self.tempRelation)
			if(len(atoms)==2):
				self.tempAtom1 = atoms[0].strip()
				self.tempAtom2 = atoms[1].strip()

			# Assign interval to atoms
			if(self.tempAtom1 in tempIntervals):
				self.tempIntervalsA1 = tempIntervals[self.tempAtom1]
			if(self.tempAtom2 in tempIntervals):
				self.tempIntervalsA2 = tempIntervals[self.tempAtom2]

		return hasTempRel

	def checkBranchClosing(self, bottomAtom):
		
		# Binary
		if(self.mode==2):
			if len(bottomAtom)>len(self.name): 
				res=bottomAtom.replace(self.name,'')             #get diff
			else: 
				res=self.name.replace(bottomAtom,'')             #get diff
			
			if(res=='-'):
				return True
			else:
				if(not self.parent is None):
					return self.parent.checkBranchClosing(bottomAtom)
				else:
					return False
		
		# 3-valued		
		if(self.mode==3):

			#if(len(self.tempRelation)==0):

			#print("D0 " + str(bottomAtom) + " " + str(self.truthValues))
			collTruthValues = []
			#collTruthValues.extend(self.truthValues)
			if(not self.parent is None):
				self.parent.collectTruthValues(bottomAtom, collTruthValues)

			# Check if more than one truth value
			#print(str(collTruthSet) + " + " + str(self.truthValues))

			uniqueValues = set(collTruthValues)  & set(self.truthValues) # set intersection set(collTruthSet)

			if (len(uniqueValues) == 0 and len(collTruthValues) > 0): # collTruthSet
				print(str(self.name) + " " + "closed: " + str(uniqueValues))
				return True
			else:
				return False


	def checkParentOverlapt(self):

		if (not self.parent is None):

			collParentAtoms = []
			self.parent.collectParentAtoms(collParentAtoms)

			bottomAtoms = [self.tempAtom1, self.tempAtom2]
			parentOverlap = set(collParentAtoms) & set(bottomAtoms)  # set intersection

			if (len(parentOverlap) == 2): # both atoms need to be overlaped mit parents
				return True
			else:
				return False

	def collectParentAtoms(self, collPartenAtoms):

		collPartenAtoms.extend(self.name)

		if (self.parent is None):
			return
		else:
			self.parent.collectParentAtoms(collPartenAtoms)

	def collectTruthValues(self, bottomAtomId, collTruthValues):	
		
		
		if(bottomAtomId==self.name ): # and not self.overwritten
			#print("D1: " + str(bottomAtomId) + " " + str(self.name))
			collTruthValues.extend(self.truthValues)
		
		if(self.parent is None):
			return
		else:
			self.parent.collectTruthValues(bottomAtomId, collTruthValues)

class TableauGenerator:

	clauseList = []
	#atomDict = {}
	mode = 2 # 2 (binary) or 3-valued (el)
	topAtom= ""
	leafAtomsOpen =  []
	atomToIntervalIdDict = {}

	tempRels = {}
	tempIntervals = {}
	isTempMode = False
	
	def __init__(self, clauses, intervals, top, mde, tempMode):

		self.clauseList = clauses
		self.mode = mde
		self.topAtom = top
		self.tempIntervals = intervals

		#if(len(intervals)>0):
		self.isTempMode = tempMode # True
		
	def assignTruthValues(self, treeNode, hasTempRelation, atomToIntervalId={}):
	
		atomId = treeNode.name
		
		negatedWeak = False
		negatedStrong = False
		if('-' in atomId):
			negatedWeak = True
			atomId = atomId.replace('-','')
		if('~' in atomId):
			negatedStrong = True	
			atomId = atomId.replace('~','')			
				
		#print(str(treeNode.name) + " " + str(negatedWeak) + str(negatedStrong))

		if(not hasTempRelation):

			if(not negatedWeak and not negatedStrong):
				treeNode.truthValues.append(2)
			if(negatedWeak and not negatedStrong):
				treeNode.truthValues.extend([-2,0])
			if(not negatedWeak and negatedStrong):
				treeNode.truthValues.append(-2)
			if(negatedWeak and negatedStrong):
				treeNode.truthValues.extend([0,2]) # Need to check that again

		else:

			ivs1 = []
			ivs1 = treeNode.tempIntervalsA1
			ivs2 = []
			ivs2 = treeNode.tempIntervalsA2

			if (len(ivs1) == 0 or len(ivs2) == 0): # Iv intervals are missing truthvalue is 0
				treeNode.truthValues.append(0)
				return
			else:
				firstIv = self.atomToIntervalIdDict[treeNode.tempAtom1]  # next(iter(ivs1))
				iv1 = ivs1[firstIv]  # 0 Take only first interval
				secondIv = self.atomToIntervalIdDict[treeNode.tempAtom2]  # next(iter(ivs2))
				iv2 = ivs2[secondIv] # 0

			# Eval temp relations
			if(treeNode.tempRelation == "(b)"): # Before

				if(iv1[0] < iv1[1] < iv2[0] < iv2[1]):
					treeNode.truthValues.append(2)
				else:
					treeNode.truthValues.append(-2)
			# Eval temp relations
			elif(treeNode.tempRelation == "(B)"): # Before

				if(iv2[0] < iv2[1] < iv1[0] < iv1[1]):
					treeNode.truthValues.append(2)
				else:
					treeNode.truthValues.append(-2)

			elif(treeNode.tempRelation == "(m)"): # Meets

				if(iv1[0] < iv1[1] == iv2[0] < iv2[1]):
					treeNode.truthValues.append(2)
				else:
					treeNode.truthValues.append(-2)

			elif(treeNode.tempRelation == "(M)"): # Meets

				if(iv2[0] < iv2[1] == iv1[0] < iv1[1]):
					treeNode.truthValues.append(2)
				else:
					treeNode.truthValues.append(-2)

			else:
				print("Temp. relation unkown: " + treeNode.tempRelation)


		treeNode.name = atomId
	

	def createModels(self):
			
		modelListTVs = []
		modelListIntervals =  []
		trackDuplicates = {}

		#print("D2: " + str(len(self.leafAtomsOpen)))

		for leafNode in self.leafAtomsOpen:
			
			trueAtoms = {}
			atomList = []

			leafNode.getParentAtoms(trueAtoms)

			if(self.mode==2):
				atomList = list(trueAtoms.keys())
				
			if(self.mode==3):

				# Create model with trueAtoms
				for key, tValues in trueAtoms.items():
					#keyVal = str(key) + ": "  + str(tValues) # + "("  + ")"
					tVal = int(tValues[0]) # Default
					if(len(tValues) > 2):
						print("More than 2 truth values. Exit...")
						exit
					if (len(tValues) == 2):
						print("Select smaller (regarding model size) value (i.e., 0) ")
						if(tValues[0] < tValues[1] and tValues[0]==0):
							tVal = 0
						if(tValues[0] < tValues[1] and tValues[1]==0):
							tVal = 0

					if(tVal==2):
						keyVal =  str(key)
					if(tVal==0):
						keyVal = '-' + str(key)

					if(tVal==-2):
						keyVal = '~' + str(key)

					# Ignore 0 (weak neg) in model representation
					if(tVal==-2 or tVal==2):
						atomList.append(keyVal)

				# Create model with undefined atoms (atom not in tableau branch) -> assign weak neg(-a)
				tempKeys = []
				ivList  = []
				for key in trueAtoms.keys():
					tAtom = key.replace('-','').replace('~','')
					tempKeys.append(tAtom)

					if (self.isTempMode):
						if(tAtom in self.tempIntervals):
							ivsForAtom = self.tempIntervals[tAtom]
							firstIv = self.atomToIntervalIdDict[tAtom]  # next(iter(ivsForAtom))
							tempTxt = str(key) + ": " + str(ivsForAtom[firstIv]) #  0
							ivList.append(tempTxt)

				# Ignore unassigned Atoms (0) in model representation
				#unassignedAtoms = set(self.atomDict.keys()) - set(tempKeys)
				#if(len(unassignedAtoms)>0):
				#	for uaAtom in unassignedAtoms:
				#		atomList.append('-' + str(uaAtom))

			atomList.sort()
			dupKey = str(atomList)
			if(not dupKey in trackDuplicates):
				modelListTVs.append(atomList)
				if (self.isTempMode):
					modelListIntervals.append(ivList)

				trackDuplicates[dupKey] = ""

			
		return (modelListTVs, modelListIntervals)
				

	def printTree(self, topNode):

		for pre, fill, node in RenderTree(topNode):
			cls = ""
			if(node.branchClosed):
				cls = "X"
			treestr = u"%s%s (%s)" % (pre, node.name, cls)
			#print(treestr.ljust(8), node.length, node.width)
			print(treestr)	

	def removeClauseNode(self, nodeID):
	
		for clause in self.clauseList:
			
			if(clause[0]==nodeID):
				self.clauseList.remove(clause)
				return True

		return False

	def addClauseNodes(self, activeNode, nextClause): #, clauseIndex
		
		# Remember since well be replaced
		clause = nextClause

		#newIndex = clauseIndex + 1
		newIndex = self.clauseList.index(nextClause) + 1

		#print("Active clause: " + str(clause))

		# Last clauses reached, we are at the leafs
		nextClause=None
		if(newIndex < len(self.clauseList)): # clauseIndex
			nextClause = self.clauseList[newIndex] #  clauseIndex

		# Create model tree
		for atom in clause:

			atomId = str(atom)

			#tKey = atomId.replace('-', '').replace('~', '')
			#if (not tKey in self.atomDict):  # tupleVal1
			#	self.atomDict[tKey] = ""  # prefix

			clauseNode = TableauNode(atomId, parent=activeNode, children=None, mode=self.mode)
			#clauseNode.mode = self.mode
			lastNode = clauseNode

			closeFromTempNodes = False

			# EQ Temporal mode
			if(self.mode==3):

				hasTempRelation = False
				if (self.isTempMode == True):
					hasTempRelation = clauseNode.assignTemporalInfo(self.tempRels, self.tempIntervals)

				self.assignTruthValues(lastNode, hasTempRelation)

				if (hasTempRelation):
					# Check if both atoms are in the branch, otherwise close it
					hasOverlap = clauseNode.checkParentOverlapt()

					# Case where temporal relation misses left/right atom (no overlap) -> Close branch
					if(not hasOverlap):
						clauseNode.branchClosed = True
						continue
					else:

						# Assign truthvalues for tempRel node
						#self.assignTruthValues(lastNode, self.mode)


						# Add nodes for left/right atom and create truth values
						atomIdLeft = clauseNode.tempAtom1
						clauseNodeLeft = TableauNode(atomIdLeft, parent=clauseNode, children=None, mode=self.mode)
						clauseNodeLeft.assignTemporalInfo(self.tempRels, self.tempIntervals)

						clauseNodeLeft.truthValues = lastNode.truthValues.copy()
						#self.assignTruthValues(clauseNodeLeft, self.isTempMode)
						# clauseNodeLeft.overwriteParentNodes()

						##### CHECK why closed?
						closeFromTempNodes = clauseNodeLeft.checkBranchClosing(atomIdLeft)
						clauseNodeLeft.branchClosed = closeFromTempNodes

						atomIdRight = clauseNode.tempAtom2
						clauseNodeRight= TableauNode(atomIdRight, parent=clauseNodeLeft, children=None,  mode=self.mode)
						clauseNodeRight.assignTemporalInfo(self.tempRels, self.tempIntervals)

						clauseNodeRight.truthValues = lastNode.truthValues.copy()
						#self.assignTruthValues(clauseNodeRight, self.isTempMode)


						closeFromTempNodes2 = clauseNodeRight.checkBranchClosing(atomIdRight)
						clauseNodeRight.branchClosed = closeFromTempNodes2
						#if (not closeFromTempNodes):
						closeFromTempNodes = (closeFromTempNodes or closeFromTempNodes2) # If close no need to open branch again

						lastNode = clauseNodeRight

			# Check if branch is alrady closed
			if(not closeFromTempNodes):
				closed = lastNode.checkBranchClosing(atomId) # clauseNode
				if (closed):
					clauseNode.branchClosed = True
					continue
			else:
				# Only close sub nodes
				continue


			#print("Next 2: " + str(nextClause))
			#newIndex = clauseIndex + 1
			if (not nextClause is None): # reached bottom
				self.addClauseNodes(lastNode, nextClause) # clauseNode
			else:
				clauseNode.isLeaf = True
				self.leafAtomsOpen.append(lastNode) # clauseNode

	def rearangeClauses(self):

		tempList = []

		for clause in self.clauseList:

			move = False

			for atom in clause:
				atomId = str(atom)

				if(atomId in self.tempRels):
					move = True
					break
			if(move):
				tempList.append(clause)

		# Remove from list (and merge atom into one for later)
		i = 0
		tempList2 = []
		for clause in tempList:
			self.clauseList.remove(clause)

			tempList = list(clause)
			joinString = " ".join(tempList)
			#clause2 = [joinString]
			tempList2.append((joinString,)) # clause2
			#clause.append()


		# Move to end by simply adding it
		if(len(tempList2) > 0):
			self.clauseList.extend(tempList2)

	def solve(self, printTrace, aToIvs = {}):
			
		self.atomToIntervalIdDict = aToIvs

		topNode = None
		
		#print("Starting... ")

		# Get root atom and create root node

		atomId = str(self.topAtom) # "a:" +

		removed = self.removeClauseNode(atomId)

		if(not removed):
			print("Top atom is given or is not in clauses!")
			sys.exit()

		topNode = TableauNode(atomId, parent=None, children=None, mode=self.mode)
		#topNode.mode = self.mode

		if(atomId in self.tempRels):
			print("Spatial atom can not be at the top!")
			exit

		# Assign many-valued truth values if mode=3
		if(self.mode==3):
			self.assignTruthValues(topNode, False) # self.isTempMode

		#clauseCycle = cycle(self.clauseList)
		firstClause =  self.clauseList[0] #  next(clauseCycle)

		print("Top item: " + atomId)

		# Move temporal clauses to end
		self.rearangeClauses()
		
		self.addClauseNodes(topNode, firstClause) # , 0
		
		if(printTrace):
			self.printTree(topNode)

		(models, modelIntervals) = self.createModels()

		return (models, modelIntervals)

	
def main(argv):

	parser = optparse.OptionParser()
	parser.add_option('--file', action="store", dest="file", default="")
	parser.add_option('--tempf', action="store", dest="tempf", default="")
	parser.add_option('--mode', action="store", dest="mode", default=2)
	parser.add_option('--top', action="store", dest="top", default="")
	parser.add_option('--reduct', action="store_true", dest="reduct", default=False)
	parser.add_option('--print', action="store_true", dest="printTrace", default=False)
	(options, args) = parser.parse_args()

	file1 = open(options.file, 'r')
	lines1 = file1.readlines()
	file1.close()
	
	print("Mode: " + str(options.mode))	
	print("Reduct: " + str(options.reduct))	

	tempMode = False
	tRels ={}

	if (len(options.tempf) > 0):
		tempMode = True
		tRels = createTempRel()
		print("Temporal mode")

	clauseList = createClauseList(lines1, tRels)
			
	print("Clauses in CNF: " + str(clauseList))	

	tempIntervals = {}
	interValCombos= []
	if(len(options.tempf) > 0):
		tempIntervals = readIntervalDict(options.tempf)

		for key1 in tempIntervals:

			ivGroup = tempIntervals[key1]
			interValComb = []
			for key2 in ivGroup:
				ivs = ivGroup[key2]
				newKey = str(key1) + ";" + str(key2)
				interValComb.append(newKey)

			interValCombos.append(interValComb)

	# Main

	# MODE: Non-temporal
	if(not tempMode): #
		tabGen = TableauGenerator(clauseList, tempIntervals, options.top, int(options.mode), tempMode)
		(models, modelIntervals) = tabGen.solve(options.printTrace)
		if (options.printTrace):
			print(str(models))
	# MODE: Temporal
	else:

		if(len(interValCombos) > 0):
			#tupleCombos = tuple(interValCombos)
			ivCandidates = list(itertools.product(*interValCombos))
			count = 1

			for ivCand in ivCandidates:

				if (options.printTrace):
					print("Temporal Setting " + str(count))

				# Move candidates to
				ivCandDict = {}

				for candEntry in ivCand:
					tempArray = candEntry.split(';')
					ivCandDict[tempArray[0]] = tempArray[1]

				listCopy = clauseList.copy() # Since it will be altered
				tabGen = TableauGenerator(listCopy, tempIntervals, options.top, int(options.mode), tempMode)
				tabGen.tempRels = tRels
				(models, modelIntervals) = tabGen.solve(options.printTrace, ivCandDict)
				if(options.printTrace):
					print("Tv: " + str(models))
					print("Iv: " + str(modelIntervals))
				else:
					print("Model count: " + str(len(models)))

				count = count + 1





	print("Finished")	

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

	