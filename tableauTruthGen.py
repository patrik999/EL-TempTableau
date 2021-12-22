import re

def getTruthValue(atom, truthValuesAtom):

    tValue = None

    if '-~' in atom:
        atomTemp = atom.replace('-', '').replace('~', '')
        tValue = truthValuesAtom[atomTemp]
        tValue = tValue * (-1)
        tValue = calcWeakNeg(tValue)
    elif '-' in atom:
        countNeg = atom.count('-')
        atomTemp = atom.replace('-', '').replace('~', '')
        tValue = truthValuesAtom[atomTemp]

        while countNeg >= 1:
            tValue = calcWeakNeg(tValue)
            countNeg=countNeg-1

    elif '~' in atom:
        atomTemp = atom.replace('-', '').replace('~', '')
        tValue = truthValuesAtom[atomTemp]
        tValue = tValue * (-1)
    else:
        tValue = truthValuesAtom[atom]

    return tValue

def calcWeakNeg(tValue):

    if(tValue <= 0):
        return 2
    else:
        return tValue * (-1)


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

def test_tableau(allTruthValues):

    for tv1 in allTruthValues:
        for tv2 in allTruthValues:

            truthValues = {}
            truthValues['a'] = tv1 # 0
            truthValues['b'] = tv2 # 0
            print("Input: " + str(truthValues))

            f1 = "a>b"
            tVal1 = binTruthValues(f1, truthValues)
            print(f1  +" has tv: " + str(tVal1))

            f2 = "-a;b"
            tVal2 = binTruthValues(f2, truthValues)
            print(f2  +" has tv: " + str(tVal2))

            f3 = "--a,-b"
            tVal3 = binTruthValues(f2, truthValues)
            print(f3  +" has tv: " + str(tVal3))

            if tVal1 != tVal2:
                print("DEVIATION 1:")
            if tVal1 != tVal3:
                print("DEVIATION 2:")


def test_doubleWeekNeg(allTruthValues):

    for tv1 in allTruthValues:
        for tv2 in allTruthValues:

            truthValues = {}
            truthValues['a'] = tv1 # 0
            truthValues['b'] = tv2 # 0
            print("Input: " + str(truthValues))

            f1 = "a"
            res1 = binTruthValues(f1, truthValues)
            #print(f1  +" has tv: " + str(res1))

            #f1a = "-a"
            #tVal1a = binTruthValues(f1a, truthValues)
            #print(f1a  +" has tv: " + str(tVal1a))

            f2 = "--a"
            res2 = binTruthValues(f2, truthValues)
            print(f2  +" has tv: " + str(res2))

            f3 = "-~a"
            res3 = binTruthValues(f3, truthValues)
            print(f3  +" has tv: " + str(res3))

            if res1 != res2:
                print("DEVIATION 1:")
            if res1 != res3:
                print("DEVIATION 2:")

def test_impl(allTruthValues):

    for tv1 in allTruthValues:
        for tv2 in allTruthValues:

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
                print("DEVIATION:")
                print(f5  +" has tv: " + str(tVal1))
                print(f6  +" has tv: " + str(tVal2))

            #f7 = "~a;b"
            #tVal = binTruthValues(f7, truthValues)
            #print(f7  +" has tv: " + str(tVal))


if __name__ == "__main__":

    # Syntax: ; (or) | , (and) | - (wkneg) | ~ (wkneg) |  > (impl)
    # Iterate through all combinations

    #allTruthValues = range(-2,3)
    allTruthValues = {-2,0,2}
    print(str(allTruthValues))

    #test_impl(allTruthValues)
    #test_doubleWeekNeg(allTruthValues)
    test_tableau(allTruthValues)

    #print("Everything passed")