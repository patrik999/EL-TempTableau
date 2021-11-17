#!/usr/bin/env python

from lattice import Lattice 
import graphviz
#from itertools import chain, combinations

def main(argv):

	def powerset(s):
		x = len(s)
		masks = [1 << i for i in range(x)]
		for i in range(1 << x):
			yield set([ss for mask, ss in zip(masks, s) if i & mask])


	def intersection(a,b): 
		return a&b
	
	def union(a,b): 
		return  a|b
	
	print("Start")	
	
	#ps2=[set(),set(['x']),set(['y']),set(['z']),set(['x','y']),set(['x','z']),set(['y','z']),set(['x','y','z'])]
	#ps2=[set(),set(['1']),set(['2']),set(['3']), set(['1','2']),set(['1','3']),set(['2','3']), set(['1','2','3'])] #
	
	ps=list(powerset(['1', '2', '3', '4', '5']))
	print(str(ps))
	#print(str(ps2))
	
	
	#L=Lattice(ps)
	L=Lattice(ps,union,intersection)
	 
	print(str(L.BottonElement))
	
	print(str(L.TopElement))
	
	set_with_y=L.wrap(set(['2'])) 
	#set_with_y=L.wrap(set(['y'])) 	
	print(str(set_with_y))
	
	set_with_yz=L.wrap(set(['2','3']))
	#set_with_yz=L.wrap(set(['y','z']))
	print(str(set_with_yz))	
	
	set_with_xz=L.wrap(set(['1','3']))
	#set_with_xz=L.wrap(set(['x','z']))
	print(str(set_with_xz))	
	
	smaller = (set_with_y <= set_with_yz)
	larger = (set_with_y <= set_with_yz)
	eq = (set_with_xz == set_with_yz)
	print(str(smaller) + " " + str(larger) + " " + str(eq))
	
	hasse = L.Hasse().replace("set()", "{}")
	#print(hasse)
	scc = graphviz.Source(hasse)
	scc.render('./hasse1.gv')
	

	print("Finished")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])