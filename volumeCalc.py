import psycopg2
from terminaltables import AsciiTable
from PointlessConverter import write_dbms 
#-------------------------------------------------------------------------------#
# function to query the DBMS
def callDB(query, dbmsname, user, password):
	# Create the Database connection
	conn = psycopg2.connect("host='localhost' dbname='{0}' user='{1}' password='{2}'".format(dbmsname, user, password))
	cur = conn.cursor()
	# Execute the query
	cur.execute(query)
	# Retrieve and return the table
	table = cur.fetchall()
	return table
#-------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------#
# The inaccurate method for calculating the volume


def getStatistics(fileName):
	with open("{0}".format(fileName), "r") as f:
   		lenX = float(f.readline().split(' ', 1 )[1])
   		lenY = float(f.readline().split(' ', 1 )[1])
   		lenZ = float(f.readline().split(' ', 1 )[1])
   		Scale = float(f.readline().split(' ', 1 )[1])
   		f.close()
   	return lenX, lenY, lenZ, Scale

def bboxVolumeCal(lenX, lenY, lenZ, Scale):
   	volume = lenX * lenY * lenZ 
   	return volume

def fastVolumeCalc(dbmsname, user="postgres", password=""):
	lenX, lenY, lenZ, Scale = getStatistics("scalingStatistics.txt")
	emptyVolume = (256 / Scale)**3
	bboxVolume = bboxVolumeCal(lenX, lenY, lenZ, Scale)
	exteriorVolume = emptyVolume - bboxVolume

	f = open('volumeStats.txt','w')

	table_data = [
    ['Fast', 'Volume'],
    ['Boundingbox', "{0:0.2f} m3".format(bboxVolume)],
    ['Exterior', "{0:0.2f} m3".format(exteriorVolume)],
    ['bbox %', "{0:0.1f} %".format(bboxVolume/emptyVolume*100)],
    ['Total', "{0:0.2f} m3".format(emptyVolume)]
	]
	table = AsciiTable(table_data)

	f.write("{0}\n".format(table.table))
	f.close()

	return table.table
	# return "Total volume: {0} \nBoundingbox volume: {1} \nExterior volume: {2}\n{3:0.1f}% of the empty space is in the bbox".format(emptyVolume, bboxVolume, exteriorVolume, bboxVolume/emptyVolume*100) 
#-------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------#
# The accurate method for calculating the volume
def calcDBstatistics(dbmsname, user, password):
	sql = "select max(CAST(x AS float)), max(CAST(y AS float)), max(CAST(z AS float)) from pointcloud;"
	table = callDB(sql, dbmsname, user, password)
	return table[0]

def loopSlices(dbmsname, user, password, direction, maxValue):
	print "+-------------+------------+\n| Loop through {0}\n+-------------+------------+".format(direction)
	conn = psycopg2.connect("host='localhost' dbname='{0}' user='{1}' password='{2}'".format(dbmsname, user, password))
	cur = conn.cursor()

	# based on the boundary dimension we select the direction in which we slice
	if direction == 'x':
		dimension1 = 'z'
		dimension2 = 'y'
	elif direction == 'z':
		dimension1 = 'y'
		dimension2 = 'x'
	elif direction == 'y':
		dimension1 = 'x'
		dimension2 = 'z'

	print "| The maximum value for \n| {0} is {1:0.2f} \n+-------------+------------+".format(direction, maxValue) 
	materialPaths = set()
	for i in range(int(maxValue)):
		if i % 50 == 0:
			print "| Calculated {0} slices".format(i)
		sql = "select min(trunc(CAST({0} AS float))), max(trunc(CAST({0} AS float))), min(trunc(CAST({4} AS float))), max(trunc(CAST({4} AS float))) from pointcloud where trunc(CAST({1} AS float)) >= {2} AND trunc(CAST({1} AS float)) < {3};".format(dimension1, direction, i, i+1, dimension2)
		cur.execute(sql)
		table = cur.fetchall()
		if None in table[0]:
			continue
		else:
			minVal1 = table[0][0]
			maxVal1 = table[0][1]
			minVal2 = table[0][2]
			maxVal2 = table[0][3]
			sql = "select materialpath, leafsize from emptyspace where CAST({0} AS float) >= {1} AND CAST({0} AS float) < {2} AND CAST({3} AS float) > {4} AND CAST({3} AS float) < {5};".format(direction, i, i+1, dimension1, minVal1, maxVal1)
			cur.execute(sql)
			# Retrieve the table
			table = cur.fetchall()
			for row in table:
				materialPaths.add(row)
	print "| Calculated {0} slices\n+-------------+------------+".format(i)
	return materialPaths

def calcEmptyVolume(Scale, dbmsname, user, password):
	sql = "select leafsize from emptyspace;"
	table = callDB(sql, dbmsname, user, password)
	volume = 0
	for row in table:
		volume += (row[0]/Scale)**3
	return 1

def accurateVolumeCalc(dbmsname, user="postgres", password=""):
	lenX, lenY, lenZ, Scale = getStatistics("scalingStatistics.txt")
	
	Xmax, Ymax, Zmax = calcDBstatistics(dbmsname, user, password)
	
	# loop through slices x and store all empty leaf (as tuples of x,y,z,leafsize) nodes between min x and max x in a set
	Xempty = loopSlices(dbmsname, user, password, 'x', Xmax)
	# loop through slices y and store all empty leaf (as tuples of x,y,z,leafsize) nodes between min y and max y in a set
	Yempty = loopSlices(dbmsname, user, password, 'y', Ymax)
	# loop through slices z and store all empty leaf (as tuples of x,y,z,leafsize) nodes between min z and max z in a set
	Zempty = loopSlices(dbmsname, user, password, 'z', Zmax)
	# These loops check the slices of the finest resolution (1x1x1)

	# Check which boxes are present in ALL sets and store those in another set
	XYempty = Xempty & Yempty
	XYZempty = XYempty & Zempty
	
	# These boxes together represent the accurate volume of the building 
	interiorVolume = 0
	for each in XYZempty:
		interiorVolume += (each[1]/Scale)**3

	emptyVolume = calcEmptyVolume(Scale, dbmsname, user, password)
	exteriorVolume = emptyVolume - interiorVolume
	bbox = bboxVolumeCal(lenX, lenY, lenZ, Scale)
	
	f = open('volumeStats.txt','a')

	table_data = [
    ['Accurate', 'Volume'],
    ['Interior', "{0:0.2f} m3".format(interiorVolume)],
    ['Exterior', "{0:0.2f} m3".format(exteriorVolume)],
    ['Interior %', "{0:0.1f} %".format(interiorVolume/emptyVolume*100)],
    ['Total', "{0:0.2f} m3".format(emptyVolume)],
    ['D total', "{0:0.2f} m3".format(((256/Scale)**3)-emptyVolume)],
    ['Boundingbox', "{0:0.2f} m3".format(bbox)],
    ['Diff int', "{0:0.2f} m3".format(bbox - interiorVolume)]
	]
	
	table = AsciiTable(table_data)

	f.write("{0}\n".format(table.table))
	f.close()

	f = open('temp.txt','w')
	for each in XYZempty:
		f.write("'"+ str(each[0]) + "',")
	f.close()

	conn = psycopg2.connect("host='localhost' dbname='"+ dbmsname +"' user='"+ user + "' password='"+ password + "'")
	cur = conn.cursor()
	cur.execute('CREATE TABLE interiorspace(materialpath varchar(100));')
	conn.commit()


	write_dbms(dbmsname, 'interiorspace', user, password)

	try:
		import winsound 
		winsound.Beep(900, 200)
	except:
		pass

	return table.table
#-------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------#
if __name__ == "__main__":

	

	conn = psycopg2.connect("host='localhost' dbname='bouwpubcolor' user='postgres' password=''")
	cur = conn.cursor()
	cur.execute('DROP TABLE interiorspace;')
	# cur.execute('CREATE TABLE interiorspace(materialpath varchar(100), x varchar(100), y varchar(100), z varchar(100), leafsize varchar(100));')
	conn.commit()

	# write_dbms("bouwpubcolor", 'interiorspace', 'postgres', '')

	print fastVolumeCalc("bouwpubcolor")

	print accurateVolumeCalc("bouwpubcolor")