from bitstring import BitStream, BitArray


def getEqualInnerNeighbours(materialisedPath):

	# Set up the different values of the input materialised path
	# print "Current node: ", materialisedPath
		# The final digit of the materialised path for calculating inner neighbours
	leafDecimal = int(materialisedPath[-1])

	# Check inner neighbours 
		# take the mask to switch on/off every bit (dimension) of the highst level of resolution
	xBinary = BitArray(bin="{0:03b}".format(leafDecimal)) ^ BitArray(bin='001')
	yBinary = BitArray(bin="{0:03b}".format(leafDecimal)) ^ BitArray(bin='010')
	zBinary = BitArray(bin="{0:03b}".format(leafDecimal)) ^ BitArray(bin='100')

	# 	# results in 3 inner neighbours (a, b and c) --> it converts the binary coordinate back to integers
	xMP = "{0}{1}".format(materialisedPath[0:-1], int(xBinary.bin, 2))
	yMP = "{0}{1}".format(materialisedPath[0:-1], int(yBinary.bin, 2))
	zMP = "{0}{1}".format(materialisedPath[0:-1], int(zBinary.bin, 2))

	return [xMP, yMP, zMP]


def getK(materialisedPath, dimension):
	dimension = dimension.lower()
	# NOTE: this is only the code for x in the paper (and z in our case - the paper has the binary numbers flipped in the Matrices of J, B and E)
	# print "Get K for node: {0} in dimension: {1}\n".format(materialisedPath, dimension)

	if dimension == 'x':
		dimension = 2
	elif dimension == 'y':
		dimension = 1
	elif dimension == 'z':
		dimension = 0
	else:
		return "Please input a dimension!"

	n = len(materialisedPath)

	prevNode = None
	for i, node in enumerate(reversed(materialisedPath)):
		if i == 0: # Here we define Xn (or Yn or Zn for that matter), which doesn't get checked any further because it's the first position
			Xn = "{0:03b}".format(int(node))[dimension]		
		else:
			if "{0:03b}".format(int(node))[dimension] == Xn: #X(n-i)
				pass
			else:
				if int("{0:03b}".format(int(prevNode))[dimension]) == int(Xn): #X(n-k)+1
					return i #in this case i == k
		prevNode = node

		if i+1 == n: #in this case there's no neigbor in this direction
			# print "No neigbor found!" 
			return False
	

def getEqualOuterNeighbours(materialisedPath):
	Kx = getK(materialisedPath, 'x')
	Ky = getK(materialisedPath, 'y')
	Kz = getK(materialisedPath, 'z')
		# take the complement of the entire materialised for every dimension
	xMP = ""
	yMP = ""
	zMP = ""

	for i, node in enumerate(reversed(materialisedPath)):
	 	if Kx == False:
	 		pass
	 	elif i > Kx:
	 		xMP += str(node)
	 	else:
			nodex = BitArray(bin="{0:03b}".format(int(node)))
			xDigit = nodex ^ BitArray(bin='001')
			xMP += str(int(xDigit.bin, 2))
		
		if Ky == False:
	 		pass
	 	elif i > Ky:
	 		yMP += str(node)
	 	else:
			nodey = BitArray(bin="{0:03b}".format(int(node)))
			yDigit = nodey ^ BitArray(bin='010')
			yMP += str(int(yDigit.bin, 2))
		
		if Kz == False:
	 		pass
	 	elif i > Kz:
	 		zMP += str(node)
	 	else:
			nodez = BitArray(bin="{0:03b}".format(int(node)))
			zDigit = nodez ^ BitArray(bin='100')
			zMP += str(int(zDigit.bin, 2))

	neighbours = []
	neighbours.append((xMP[::-1], Kx))
	neighbours.append((yMP[::-1], Ky))
	neighbours.append((zMP[::-1], Kz))

	return neighbours


def getLargerNeighbours(equalNeighbours):
	# We create an empty list that will contain all larger sized neighbours
	largerNeighbours = set()
	# We loop through all the equal sized neighbours
	for neighbour in equalNeighbours:
		# For every equal sized neighbour we loop through the digits
		for i, digit in enumerate(neighbour[0]):
			# If the level is smaller than K we append it to the list with larger sized neighbours
			if i < neighbour[1]:
				i += 1
				largerNeighbours.add(neighbour[0][:-i])
	
	return largerNeighbours, [equalNeighbours[0][0],equalNeighbours[1][0],equalNeighbours[2][0]]

def createMPs(curDict, prevNeighbours):
	newNeighbours = set()
	# print curDict
	# print prevNeighbours
	for prev in prevNeighbours:
		for each in curDict:
			new = prev + each
			newNeighbours.add(new)
	# print newNeighbours
	return newNeighbours

def getSmallerNeighbours(EqualInnerNeighbours, EqualOuterNeighbours, maxLevels, currentNode):

	neighbours = set()
	# print currentNode, BitArray(bin="{0:03b}".format(int(currentNode[-1])))
	Xn = int(BitArray(bin="{0:03b}".format(int(currentNode[-1])))[2])
	Yn = int(BitArray(bin="{0:03b}".format(int(currentNode[-1])))[1])
	Zn = int(BitArray(bin="{0:03b}".format(int(currentNode[-1])))[0])

	compXn = int((bin(Xn) ^ BitArray(bin='1')).bin)
	# print Xn, compXn
	compYn = int((bin(Yn) ^ BitArray(bin='1')).bin)
	# print Yn, compYn
	compZn = int((bin(Zn) ^ BitArray(bin='1')).bin)
	# print Zn, compZn

	Dict = {
		'innerx' : [],
		'innery' : [],
		'innerz' : [],
		'outerx' : [],
		'outery' : [],
		'outerz' : []
	}

	for i in range(4):
		d1 = int(BitArray(bin="{0:02b}".format(i))[0])
		d2 = int(BitArray(bin="{0:02b}".format(i))[1])

		Dict['innerx'].append(str(int(BitArray(bin="{0}{1}{2}".format(d1, d2, Xn)).bin, 2)))
		Dict['innery'].append(str(int(BitArray(bin="{0}{1}{2}".format(d1, Yn, d2)).bin, 2)))
		Dict['innerz'].append(str(int(BitArray(bin="{0}{1}{2}".format(Zn, d1, d2)).bin, 2)))
		Dict['outerx'].append(str(int(BitArray(bin="{0}{1}{2}".format(d1, d2, compXn)).bin, 2)))
		Dict['outery'].append(str(int(BitArray(bin="{0}{1}{2}".format(d1, compYn, d2)).bin, 2)))
		Dict['outerz'].append(str(int(BitArray(bin="{0}{1}{2}".format(compZn, d1, d2)).bin, 2)))
	
	# print Dict

	prevInnerX, prevInnerY, prevInnerZ, prevOuterX, prevOuterY, prevOuterZ = ([EqualInnerNeighbours[0]]), ([EqualInnerNeighbours[1]]), ([EqualInnerNeighbours[2]]), ([EqualOuterNeighbours[0]]), ([EqualOuterNeighbours[1]]), ([EqualOuterNeighbours[2]])
	# print prevInnerX, prevInnerY, prevInnerZ, prevOuterX, prevOuterY, prevOuterZ

	neighboursXi = set()
	neighboursYi = set()
	neighboursZi = set()
	neighboursXo = set()
	neighboursYo = set()
	neighboursZo = set()

	for i in range(maxLevels-len(currentNode)):
		newInnerX = createMPs(Dict['innerx'], prevInnerX)	
		for each in newInnerX:
			neighboursXi.add(each)
		prevInnerX = newInnerX

	
		newInnerY = createMPs(Dict['innery'], prevInnerY)	
		for each in newInnerY:
			neighboursYi.add(each)
		prevInnerY = newInnerY

		newInnerZ = createMPs(Dict['innerz'], prevInnerZ)	
		for each in newInnerZ:
			neighboursZi.add(each)
		prevInnerZ = newInnerZ

		if len(prevOuterX) == '':
			newOuterX = createMPs(Dict['outerx'], prevOuterX)	
			for each in newOuterX:
				neighboursXo.add(each)
			prevOuterX = newOuterX
	
		if len(prevOuterY) == '':
			newOuterY = createMPs(Dict['outery'], prevOuterY)	
			for each in newOuterY:
				neighboursYo.add(each)
			prevOuterY = newOuterY

		if len(prevOuterZ) == '':
			newOuterZ = createMPs(Dict['outerz'], prevOuterZ)	
			for each in newOuterZ:
				neighboursZo.add(each)
			prevOuterZ = newOuterZ

	neighbours = neighboursZo | neighboursYo | neighboursXo | neighboursZi | neighboursYi | neighboursXi

	return neighbours


def giveMeAllNeighbours(currentNode, maxLevels):
	EqualOuterNeighbours = getEqualOuterNeighbours(currentNode)
	EqualInnerNeighbours = getEqualInnerNeighbours(currentNode)
	LargerNeighbours, EqualOuterNeighbours = getLargerNeighbours(EqualOuterNeighbours)

	
	SmallerNeighbours = getSmallerNeighbours(EqualInnerNeighbours, EqualOuterNeighbours, maxLevels, currentNode)
	allNeighbours = set()

	for i in range(3):
		allNeighbours.add(EqualOuterNeighbours[i])
		allNeighbours.add(EqualInnerNeighbours[i])

	allNeighbours = allNeighbours.union(LargerNeighbours)
	allNeighbours = allNeighbours.union(SmallerNeighbours)

	return allNeighbours

if (__name__ == '__main__'):
	neighbours = giveMeAllNeighbours('7', 3)
	 