#!/usr/bin/env python

import getopt, sys
import optparse
import time
import itertools

from scc import strongly_connected_components_path 
from util_mm import createClauseList
from util_mm import createModelList
#from lattice import Lattice
#import graphviz
from queue import Queue

class MinModelGenerator:

	clauseList = []
	depGraph = []
	superDepGraph = []
	atomDict = {}
	clausDict = {}
	clausDictNeg = {}
	mode = 2 # 2 (binary) or 3-valued (el)
	modelList = []
	printTrace = True

	def __init__(self, clauses, modelL, mde, trace):  # __init__
		self.clauseList = clauses
		self.mode = mde
		self.modelList = modelL
		self.printTrace = trace

	def solve(self, reduct):

		
		runLoop = True
		count = 0

		# Delete empty source nodes (recursively)
		self.deleteSources()

		while runLoop:		
			
			# Check each source S in super DP graph, and verify if minimal for T_S
			runLoop = False
			count=count+1

			if(self.printTrace):
				print("ITERATION: " + str(count))
				print("SCC: " + str(self.superDepGraph))
			
			# Collect all scc's that are sources
			#scc_sources = []
			scc_sources = Queue(maxsize = 0) # infinite

			for scc_dict in self.superDepGraph:

				isSource = True
				sourceAtoms = []
				
				# Determine if it is a source
				for node in scc_dict:
					
					tempA = node.split(":")
					
					# Check if atom or clause
					if(tempA[0]=='a'):
						sourceAtoms.append(node)
					
					# Check incoming edges (from other SCC) in DG (then no delete)
					if(self.hasIncomingEdgesDC(node, scc_dict)):
						isSource = False
						break
				
				if(isSource):
					
					resTuple = (scc_dict, sourceAtoms)
					scc_sources.put(resTuple) # append
					if(self.printTrace):
						print("Source: " + str(scc_dict))
			
			# Process all scc sources in queue
			addedToQueue = {}
			while not scc_sources.empty():
			#for resTuple in scc_sources: 
				
				resTuple = scc_sources.get()
				scc_dict = resTuple[0]
				sourceAtoms = resTuple[1]
					
				# Create intersection X between S-atoms and (given) model M
				modelIntersX = set(self.modelList) & set(sourceAtoms)
				modelDiffY = set(sourceAtoms) - set(modelIntersX)
				# Reduct to formulas applied, modelDiffY not needed
				if(reduct):
					modelDiffY = []

				if (self.printTrace):
					print("Model intersection X: " + str(modelIntersX) + " Y: " +  str(modelDiffY))
				
				# Get all clauses that have only S-atoms from S (called T_S)
				sourceOnlyClauses = []
				
				for key, clAtoms in self.clausDict.items():	
					nonSourceAtoms = set(clAtoms) - set(sourceAtoms)
					if(len(nonSourceAtoms)==0):
						#print("Only source atoms")
						sourceOnlyClauses.append(key)
				
				# Check minimality of X with T_S
				minimalOnce = False	
				# Case 1: Intersection with M and source clauses emtpy
				if(len(modelIntersX)==0 and len(sourceOnlyClauses)==0):
					if (self.printTrace):
						print("Case 1: Model and clauses empty")
					minimalOnce = True
				# Case 2: No source only clauses (yet), but has intersection with M
				elif(len(modelIntersX)>0 and len(sourceOnlyClauses)==0):
					# Add to end of queue, but only allow to add once to end of queue
					tempKey = str(scc_dict)
					if(not tempKey in addedToQueue):
						if (self.printTrace):
							print("Case 2: Process at the end")
						scc_sources.put(resTuple)
						addedToQueue[tempKey] = ""
						continue
					else:
						if (self.printTrace):
							print("Case 2: Already processed, but still clauses empty")
						minimalOnce = False	
				else:
				# Case 3: Min. model checking of X and T_S
					if (self.printTrace):
						print("Case 3: Min. model checking")
					minModels = self.createMinModelsBrute(sourceOnlyClauses, sourceAtoms)
					for minModel in minModels:	
						modelDiffMin = set(modelIntersX) - set(minModel)
						if(len(modelDiffMin)==0): #modelIntersX is minimal
							minimalOnce = True
							break
					if(not minimalOnce):
						if (self.printTrace):
							print("Intersection with M is NOT minimal")
					
											
				# Is minimal so delete
				if(minimalOnce):
					runLoop = True
					# Remove model intersection from main model
					for atom2 in modelIntersX:
						self.modelList.remove(atom2)
						
					# Apply REDUCE function
					self.reduce(modelIntersX, modelDiffY)
				else:
					runLoop = False
			
				# Delete SCC
				self.deleteSCC(scc_dict)
				
			# Delete empty source nodes (recursively)
			self.deleteSources()
			
			if(len(self.clausDict)==0):
				runLoop = False

		if (self.printTrace):
			print("Clauses end: " + str(self.clausDict))
			print("Model end: " + str(self.modelList))
		
		if(len(self.modelList) == 0):
			return True
		else:
			return False



	def createMinModelsBrute(self, clauseKeys, sourceAtoms):


		#def powerset(s):
		#	x = len(s)
		#	masks = [1 << i for i in range(x)]
		#	for i in range(1 << x):
		#		yield set([ss for mask, ss in zip(masks, s) if i & mask])


		#def intersection(a,b): 
		#	return a&b
		
		#def union(a,b): 
		#	return  a|b
		
		clauses = {}
		clausesNeg = {}
		
		# Collect all clauses to find minimalmodels
		for key in clauseKeys:
			clauses[key] = self.clausDict[key]
			clausesNeg[key] = self.clausDictNeg[key]
		
		# Create all possible models (exp. many)
		allModels = self.createModels(clauses, clausesNeg, sourceAtoms)
		
		# Filter out non-minimal models
		minModels = []
		
		# Create lattice of models (not needed)
		#atomsRange = list(range(0, len(sourceAtoms)))
		#ps=list(powerset(atomsRange)) 
		#lattice=Lattice(ps,union,intersection)
		#print("Powerset: " + str(ps))		
		
				
		# Convert binary represention of model to set of atoms
		results = []
		for modelBin1 in allModels: #  allModels
			isMin = True
			
			set_m1 = self.modelToSet(modelBin1)
			
			for modelBin2 in allModels:
				
				set_m2 = self.modelToSet(modelBin2)
				
				# Found a smaller model
				if(set_m2 < set_m1):
					isMin = False
					break
				
			if(isMin):
				modelSet = []
				for i in range(len(modelBin1)):
					atom = sourceAtoms[i]
					if(self.mode==2 and modelBin1[i]==1): # truthVal (1)
						modelSet.append(atom)
					if(self.mode==3 and modelBin1[i]!=0): # truthVal (2, -2)
						modelSet.append(atom)
					
				results.append(modelSet)

		if (self.printTrace):
			print("Possible Models: " + str(allModels))
			print("Minimal Models: " + str(results))
		
		return results


	def modelToSet(self, model):
		result = []
		
		for i in range(len(model)):
		
			if(self.mode==2 and model[i]==1): # truthVal (1)
				result.append(i)

			if(self.mode==3 and model[i]!=0): # truthVal (2, -2)
				result.append(i)
				
		return set(result)

		
		
	def createModels(self, clauses, clausesNeg, sourceAtoms):
		
		# Order of sourceAtoms are positions in model 
		nrLiterals = len(sourceAtoms) #  clause
		
		if(self.mode==2): # boolean logic
			models = list(itertools.product([0, 1], repeat=nrLiterals))		
		if(self.mode==3): # 3-valued logic
			models = list(itertools.product([-2, 0, 2], repeat=nrLiterals))	

		if (self.printTrace):
			print("Model space: " + str(models))
		modelsReturn = []
		
		for i in range(len(models)):
			model = models[i] # i-1

			if(self.mode==2 and not self.isModel2Val(model, clauses, clausesNeg, sourceAtoms)): # clause
				continue

			if(self.mode==3 and not self.isNoModel3Val(model, clauses, clausesNeg, sourceAtoms)): # clause
				continue
			
			modelsReturn.append(model)
		
		return modelsReturn 

			
	def isModel2Val(self, model, clauses, clausesNeg, sourceAtoms): #clause
				
		#Check each clause, if the interpretation is a model of the clause
		
		satClausesCount = 0		
			
		for key, clause in clauses.items():
		
			negAtoms = clausesNeg[key]		
			isModel = False
			
			for i in range(len(model)):
				truthVal = model[i] #i-1
				
				atom = sourceAtoms[i]
				
				# If atom is not in clause ignore (continue)
				if(not atom in  clause):
					continue
				
				# If atom is in clause, check if negated
				negated = (atom in negAtoms)
				#negated = ('-' in clause[i]) 
							
				# literal is negated and truthVale=False -> accept
				if(truthVal==0 and negated):
					isModel = True
					break
				# literal is positive and truthVale=True -> accept
				if(truthVal==1 and not negated):
					isModel = True
					break
			
			if(isModel):
				satClausesCount=satClausesCount+1
			
		allClausesSat = (len(clauses) == satClausesCount)
			
		return allClausesSat  # noModel

	def isNoModel3Val(self, model, clauses, clausesNeg, sourceAtoms): # clause
		
		#noModel = True

		satClausesCount = 0		
			
		for key, clause in clauses.items():

			negAtoms = clausesNeg[key]		
			isModel = False
		
			for i in range(len(model)):
				truthVal = model[i] #i-1

				atom = sourceAtoms[i]

				# If atom is not in clause ignore (continue)
				if(not atom in  clause):
					continue

				# If atom is in clause, check if negated
				negatedWeak = (atom in negAtoms)
				#negatedWeak = ('-' in clause[i]) 
				
				negatedStrong = ('~' in clause[i])			
				
				#if((truthVal==0) and negatedWeak and (not negatedStrong)):
				#	noModel = False
				#	break
				#if((truthVal==-2) and negatedStrong and (not negatedWeak)):
				#	noModel = False
				#	break
				#if((truthVal==2) and (not negatedWeak) and (not negatedStrong)):
				#	noModel = False
				#	break
					
				#print("D0: " + str(clause[i]) + " " + str(truthVal) + " " + str(negatedWeak) + " " + str(negatedStrong))
				 
				if((truthVal==0) and negatedWeak and (not negatedStrong)):
					isModel = True
					break
				if((truthVal==-2) and negatedStrong and (not negatedWeak)):
					isModel = True
					break
				if((truthVal==2) and (not negatedWeak) and (not negatedStrong)):
					isModel = True
					break	
						

			if(isModel):
				satClausesCount=satClausesCount+1
			
		allClausesSat = (len(clauses) == satClausesCount)
			
		return allClausesSat  # noModel
					
					
	def reduce(self, X, Y):
	
		clauseDel = []
		xDict = {}
		yDict = {}

		
		# Move reduce atoms to temp dict
		for atomX in X:
			xDict[atomX] = ""
		for atomY in Y:
			yDict[atomY] = ""

		if (self.printTrace):
			print("Reduce X: " + str(xDict) + "  Y: " + str(yDict))

		if (self.printTrace):
			print("Before Reduce: " + str(self.clausDict))

		for key, clAtoms in self.clausDict.items():		
			# Remove clauses with atoms X that are in head (postive), atoms Y in body (negative)
			# Remove all remaiming atoms X u Y in clauses
			atomDel = []
			atomNeg = self.clausDictNeg[key]
			for atom in clAtoms:
				
				if(atom in yDict):
					if(atom in atomNeg): #Atom is negated
						clauseDel.append(key)
						break
					else:
						atomDel.append(atom)
						
				
				if(atom in xDict):
					if(not atom in atomNeg): #Atom is positive
						clauseDel.append(key)
						break
					else:
						atomDel.append(atom)
			
			for aDel in atomDel:
				if(aDel in clAtoms):
					clAtoms.remove(aDel)

		for cDel in clauseDel:
			self.clausDict.pop(cDel)	

		if (self.printTrace):
			print("After Reduce: " + str(self.clausDict))
		
		#return
		

	def analyze(self, reduct, modelListRaw):
		
		count1 = 0
		
		if(reduct):
			
			newClauseList = []

			#print("Create reduct...")

			for clause1 in self.clauseList:
				
				postAtoms = []
				negAtoms = []

				for atom in clause1:
					if('-' in atom):
						# Only add neg. atoms that are in M
						atom2 = atom.replace('-','')
						if(atom2 in modelListRaw): # self.modelList
							negAtoms.append(atom)
					else:
						postAtoms.append(atom)
				
				# Intersect of positive atoms with M
				posIntersect = set(postAtoms) & set(modelListRaw)
				
				#clause1.clear()
				negAtoms.extend(posIntersect)
				clause1 = tuple(negAtoms)
				
				if(len(clause1) > 0):
					newClauseList.append(clause1)
				
			
			# Remove duplicates
			newClauseList = list(set(newClauseList))	

			if (self.printTrace):
				print("After reduct: " + str(newClauseList))

			
			self.clauseList = newClauseList
		
		## Create dependency graph
		
		# Iterate clauses (outer)
		for clause1 in self.clauseList:
			
			count1 += 1
			clauseId = "c:" + str(count1)
						
			
			# Put atoms to dict (fast access)
			atomsInC1 = [] # {}
			atomsInC1Neg = {}
			for i in range(len(clause1)):
				
				atom = clause1[i]
				#prefix = ""
				neg = False
				if('-' in atom):
					neg = True
					#	prefix = "-"
				#if('~' in atom):
				#	prefix = prefix + "~"
				
				tupleVal1 = str(atom).replace('-','') # Remove negation
				#tupleVal1 = tupleVal1.replace('~','') # Remove strong negation
				
				#atomsInC1[tupleVal1] = str(i)
				atomId = "a:" + tupleVal1
				
				if(not atomId in self.atomDict): # tupleVal1
					self.atomDict[atomId] = "" #prefix
				atomsInC1.append(atomId)
				if(neg):
					atomsInC1Neg[atomId] = ""
				
				# If atom is negated, e.g., -1 v 2 (which is 1 -> 2), an edge TO the clause node is added
				# If atom is positive, e.g., 1 v 2, an edge FROM the clause node is added
				if(neg):
					dgEdge = (atomId, clauseId)
				else:
					dgEdge = (clauseId, atomId)
				self.depGraph.append(dgEdge)
				
			if(not clauseId in self.clausDict): 
				self.clausDict[clauseId] =  atomsInC1 # "" 
				self.clausDictNeg[clauseId] =  atomsInC1Neg



		if (self.printTrace):
			print("Clauses: " + str(self.clausDict))
			print("Dep. graph: " + str(self.depGraph))


		## Create super-dependency graph
		scc_vertices = []
		scc_edges = {}
		scc_vertices.extend(self.clausDict.keys())
		scc_vertices.extend(self.atomDict.keys())
		
		for node in scc_vertices:
			
			edgeOutList = []
			
			for depend in self.depGraph:
				
				depEdgeFrom = depend[0]
				if(depEdgeFrom==node):
					edgeOutList.append(depend[1])
			
			# if(len(edgeOutList) > 0):
			scc_edges[node] = edgeOutList
		
		for scc in  strongly_connected_components_path(scc_vertices, scc_edges):
			#print(scc)
			self.superDepGraph.append(scc)

		if (self.printTrace):
			print("SCC Super 2: " + str(self.superDepGraph))

	def deleteSources(self):

		while True:
	
			toDelete = []
			
			for scc_dict in self.superDepGraph:
				
				delScc = True
				
				for node in scc_dict:
					
					# Check if atom is SCC (then no delete)
					tempA = node.split(":")
					if(tempA[0]=='a'):
						delScc = False
						break
					
					# Check incoming edges (from other SCC) in DG (then no delete)
					if(self.hasIncomingEdgesDC(node, scc_dict)):
						delScc = False
						break
				
				if(delScc):
					toDelete.append(scc_dict)
			
			# Delete all collected scc's
			for sccDel in toDelete:
				self.deleteSCC(sccDel)
		
			if len(toDelete) == 0:
				return

	def deleteSCC(self, scc):	

		self.superDepGraph.remove(scc)
		 
		# Delete also in DG
		for scc_node in scc:
			
			toDelete2 = []
			for depend in self.depGraph:
				
				depEdgeFrom = depend[0]
				if(depEdgeFrom==scc_node):
					toDelete2.append(depend)

			for del2 in toDelete2:
				self.depGraph.remove(del2)
		

	
	def hasIncomingEdgesDC(self, node, own_scc_dict):			
	
		# Check incoming edges in DG (then no delete)
		for depend in self.depGraph:
			
			depEdgeTo = depend[1]
			depEdgefrom = depend[0]
			if(depEdgeTo==node and (not depEdgefrom in own_scc_dict)):					
				return True
		
		return False


	def printResults(self, atomOrder, resultModels):			

		#print("Atom order: " + str(atomOrder))

		for key,model in resultModels.items():
			sout = "("
			for i in range(len(model)):
				tVal = model[i]

				if(i>0):
					sout = sout + ", "
				if(self.mode==2):
					tVal2 = " "
					if(tVal == 0):
						tVal2 = "-"
					sout = sout + tVal2 + str(i+1)

				if(self.mode==3):
					#sout = sout + str(i+1) + ": " + str(tVal)
					sout = sout + str(tVal)

			print(sout + ")")		


def main(argv):

	parser = optparse.OptionParser()
	parser.add_option('--file', action="store", dest="file", default="")
	parser.add_option('--mode', action="store", dest="mode", default=2)
	parser.add_option('--model', action="store", dest="model", default="")
	parser.add_option('--reduct', action="store_true", dest="reduct", default=False)
	parser.add_option('--print', action="store_true", dest="printTrace", default=True)
	(options, args) = parser.parse_args()

	file1 = open(options.file, 'r')
	lines = file1.readlines()
	file1.close()
	
	print("Mode: " + str(options.mode))	
	print("Reduct: " + str(options.reduct))	
	
	#variabls = 0
	#clauses = 0
	clauseList = createClauseList(lines, {})
	
	
	print("Clauses in CNF: " + str(clauseList))	

	modelList = []
	modelListRaw = []
	createModelList(options.model, modelList, modelListRaw)

	print("Model to check :" + str(modelList))

	# Main
	modelGen = MinModelGenerator(clauseList, modelList, int(options.mode), options.printTrace)
	modelGen.analyze(options.reduct, modelListRaw)
	
	isMinimal = modelGen.solve(options.reduct)
	
	if(isMinimal):
		print("Model is minimal")
	else:
		print("Model is not minimal")
	

	print("Finished")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
