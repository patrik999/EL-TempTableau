import re

def getTruthValue(atom, truthValuesAtom):

    tValue = None

    if '-' in atom:
        tValue = truthValuesAtom[atom.replace('-', '')]
        if(tValue <= 0):
            tValue = 2
        else:
            tValue = tValue * (-1)
    elif '~' in atom:
        tValue = truthValuesAtom[atom.replace('~', '')]
        tValue = tValue * (-1)
    else:
        tValue = truthValuesAtom[atom]

    return tValue

def binTruthValues(formula, truthValues):

    tValue = None

    tokens = re.split(';|,|>', formula)
    #tokens = formula.split(' ')

    # Disjunction
    if ';' in formula:
        for atom in tokens:
            tValAtom = getTruthValue(atom, truthValues)
            if tValue is None:
                tValue = tValAtom
            else:
                tValue = max(tValue, tValAtom)

    # Conjunction
    elif  ',' in formula:
        for atom in tokens:
            tValAtom = getTruthValue(atom, truthValues)
            if tValue is None:
                tValue = tValAtom
            else:
                tValue = min(tValue, tValAtom)
    # Implication
    elif  '>' in formula:
        # get left and right
        leftAndRightAtom = formula.split('>')
        tValAtomLeft = getTruthValue(leftAndRightAtom[0], truthValues)
        tValAtomRight= getTruthValue(leftAndRightAtom[1], truthValues)
        if(tValAtomLeft <= 0 or tValAtomLeft <= tValAtomRight):
            tValue = 2
        else:
            tValue = tValAtomRight
    else:
        # Single atom
        tValue = getTruthValue(formula, truthValues)

    return tValue

#def main(argv):

# Syntax: ; (or) | , (and) | - (wkneg) | ~ (wkneg) |  > (impl)

# Iterate through all combinations

for tv1 in range(-2,3):

    for tv2 in range(-2,3):

        truthValues = {}
        truthValues['a'] = tv1 # 0
        truthValues['b'] = tv2 # 0

        print("Input: " + str(truthValues))

        f1 = "a;b"
        tVal = binTruthValues(f1, truthValues)
        #print(f1  +" has tv: " + str(tVal))

        f2 = "a,b"
        tVal = binTruthValues(f2, truthValues)
        #print(f2  +" has tv: " + str(tVal))

        f3 = "-a"
        tVal = binTruthValues(f3, truthValues)
        #print(f3  +" has tv: " + str(tVal))

        f4 = "~a"
        tVal = binTruthValues(f4, truthValues)
        #print(f4  +" has tv: " + str(tVal))

        f5 = "a>b"
        tVal1 = binTruthValues(f5, truthValues)
        #print(f5  +" has tv: " + str(tVal1))

        f6 = "-a;b"
        tVal2 = binTruthValues(f6, truthValues)
        #print(f6  +" has tv: " + str(tVal2))

        if tVal1 != tVal2:
            print(f5  +" has tv: " + str(tVal1))
            print(f6  +" has tv: " + str(tVal2))
            print("DEVIATION")

        #f7 = "~a;b"
        #tVal = binTruthValues(f7, truthValues)
        #print(f7  +" has tv: " + str(tVal))


#if __name__ == "__main__":
#    import sys
#    main(sys.argv[1:])