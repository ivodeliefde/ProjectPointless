import heapq
from math import sqrt
import psycopg2
import neighbourFinding

class Priority:                                        			
# check if the list is empty, insert item to queue, remove item with lowest number
	def __init__(self):
		self.elements = []
	
	def empty(self):
		return len(self.elements) == 0
	
	def put(self, item, total_cost):
		heapq.heappush(self.elements, (total_cost, item))
	
	def get(self):
		return heapq.heappop(self.elements)[1]              	# Pop and return the smallest item from the heap

def get_nodes(dbms_name, user, password):
# In this function we extract the point from the database
	conn = psycopg2.connect("host='localhost' dbname='"+dbms_name+"' user='"+ user + "' password='"+ password + "'")
	cur = conn.cursor()
	cur.execute('select * from emptyspace;')
	return cur.fetchall()

def nodes_dict(nodes):
# In this functin we create a dictionary with point_geom[materializedpath]=(x,y,z)
	point_geom = {}
	for row in nodes:
		point_geom[row[0]] = (float(row[1]), float(row[2]), float(row[3]), (float(row[4])/2), row[0])
	return point_geom

def neighbors(current, nodes):
# This is going to be the neigbors function
	empty_node_set = set()
	for row in nodes:
		empty_node_set.add(row[0])

	possible = neighbourFinding.giveMeAllNeighbours(current, 8)
	empty = empty_node_set
	return possible & empty
	
def euclideon_dist(current, neighbor):                          
# In here we calculate the euclideon distance
	dx=(current[0]+current[3])-(neighbor[0]+neighbor[3])
	dy=(current[1]+current[3])-(neighbor[1]+neighbor[3])
	dz=(current[2]+current[3])-(neighbor[2]+neighbor[3])
	return sqrt((dx**2)+(dy**2)+(dz**2))

def a_star_search(point_geom, start, goal, nodes):
#In this function we run the A* algorithm
	open_list = Priority()                      				# Make class open_list
	open_list.put(start, 0)                     				# Add start to open_list with cost = 0            
	came_from = {}         										# This creates a dict --> came_from[neighbor] =  current                     
	cost_so_far = {}                            				# This is the cost it takes so far
	cost_so_far[start] = 0                      				# The cost from start to none is 0

	while not open_list.empty():								#while the empty_list is not empty
		current = open_list.get()               				# With this line we get the smallest total cost, total cost is the cost_so_far + cost to neighbor
		if current == goal:                    			 		# If the current is the goal than the path is found and return the came_from dict and the cost_so_far
			return came_from, cost_so_far							
		
		for neighbor in neighbors(current, nodes):                                    									# Check for all neighbors in current
			new_cost = cost_so_far[current] + euclideon_dist(point_geom[current], point_geom[neighbor])         # Calculate the cost to get to a neighbor from the star
			if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:      							# If neighbor cost_so_far or new_cost to get to the neighbor is smaller than getting their via a different path
				cost_so_far[neighbor] = new_cost                                     							# Update or create new cost to get to neighbor
				total_cost = new_cost + euclideon_dist(point_geom[goal], point_geom[neighbor])                 	# Sum the cost to get to cost(start, neighbor) + cost(neighbor, goal) = total_cost
				open_list.put(neighbor, total_cost)                                  							# Put neighbor in open_list with the total cost 
				came_from[neighbor] = current  																	# add current and neighbor to cam_from dict
	
	raise ValueError('No Path Found')

def reconstruct_path(came_from, goal, cost_so_far, nodes):
# this function reconstructs the path
	path = [nodes_dict(nodes)[goal]]
	while goal in came_from:
		goal = came_from[goal]
		# print nodes_dict(nodes)[goal]
		path.append(nodes_dict(nodes)[goal])

	try:
		import winsound 
		winsound.Beep(900, 200)
	except:
		pass

	return path[::-1]
	
if __name__ == "__main__":
# settings for the database connection
	dbms_name = 'bouwpubcolor_obstacles'
	user = 'postgres'
	password = ''
# extract nodes from database
	nodes = get_nodes(dbms_name, user, password)
# start and goal for A* 
	start = '0000' 
	goal = 	'2450'
# run the A*
	print "get route from {0} to {1}".format(start, goal)
	came_from, cost_so_far =  a_star_search(nodes_dict(nodes), start, goal, nodes)
	path = reconstruct_path(came_from, goal, cost_so_far, nodes)
	print 'path =', path #, 'distance =', distance
