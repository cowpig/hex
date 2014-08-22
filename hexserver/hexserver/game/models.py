from django.db import models

# Create your models here.


#
# in general, 'loc' will refer to a node, while 'coord' will refer to an (x,y) tuple

#
# The __repr__ for every class is a json object string

#
# Game board.
# Is a hexagonal grid, which can be accessed by (x, y) coordinates, arranged like so:
# (0,0)(1,0)(2,0)(3,0)
#   (0,1)(1,1)(2,1)(3,1)
# (0,2)(1,2)(2,2)(3,2)
#   (0,3)(1,3)(2,3)(3,3)
# (0,4)(1,4)(2,4)(3,4)
# Which wraps around, so (3,4) is connected to (0,4) in the "E" direction, and to 
# (0,0) in the 'SE' direction, for example.

#
# The [] operator is overloaded, so you can access a hex node the way you access
# matrix cells in numpy, for example:
#   In:  board = Board(5,5)
#   In:  board[2,2]
#   Out: {"neighbors": 6, "type": "node", "contents": null, "coord": [2, 2]}

#
# Each hex is managed by a Node object, which are effectively graph nodes which
# can access one another via capital letter directional strings (e.g. "NE")

#
# The [] operator is also overloaded for Node objects, allowing access of nodes
# like this:
#   In:  board = Board(5,5)
#   In:  node = board[2,2]
#   In:  node["W"]
#   Out: {"neighbors": 5, "type": "node", "contents": null, "coord": [1, 2]}

class Board(models.Model):
	# note: the home bases of each player will always be connected,
	#   separated by half the minimum of the width and height of the
	#   grid, and landlocked.
	def __init__(self, width, height):
		# Initialize the hex grid
		self.grid = []
		self.width = width
		self.height = height

		for x in xrange(width):
			self.grid.append(range(height))

		for x in range(len(self.grid)):
			for y in range(len(self.grid[x])):
				self.grid[x][y] = None

		# Pick a node as the first node
		start = Node((random.randrange(width), random.randrange(height)))
		self[start.coord[0], start.coord[1]] = start
		self.nodes = set([start])
		self.home_nodes = [start]
		self.coastal = set()

		nodes_between_homes = min(height, width)/2
		random_dir = random.choice(start.dirs.keys())

		# Add nodes in a random direction until we reach the required distance
		n = start
		for i in xrange(nodes_between_homes):
			new_coord = offset(n.coord, random_dir, width, height)
			new_node = Node(new_coord)
			n[random_dir] = new_node
			new_node[opposite(random_dir)] = n
			self[new_node.coord[0], new_node.coord[1]] = new_node
			self.nodes.add(new_node)
			self.coastal.add(new_node)
			
			n = new_node

		# And that is where the other home node will be
		self.home_nodes.append(n)

		# landlock the home nodes
		for node in self.home_nodes:
			for dir in node.dirs:
				new_coord = offset(node.coord, dir, width, height)
				if self[new_coord] == None:
					new_node = Node((new_coord))
					self.connect(new_node, width, height)
					self.coastal.add(new_node)

		# Build the rest of the map
		for i in xrange(int((width*height)/1.7) - nodes_between_homes):
			# find a random coastal node to expand
			while True:
				n = random.sample(self.coastal, 1)[0]
				if not n.landlocked():
					break
				self.coastal.remove(n)

			# create a new node
			nextdir = random.choice(n.empty_adj())
			new_coord = offset(n.coord, nextdir, width, height)
			new_node = Node((new_coord))

			# connect it to its neighbors and put it on the grid
			self.connect(new_node, width, height)

			if not n.landlocked():
				self.coastal.add(new_node)

		for node in self.home_nodes:
			node.contents.add(Home(node))

	def connect(self, new_node, width, height):
		# connect a node to its neighbors
		for dir in new_node.dirs:
			x, y = offset(new_node.coord, dir, width, height)
			other = self[x, y]

			if other != None:
				new_node[dir] = self[x, y]
				self[x, y][opposite(dir)] = new_node

		self[new_node.coord] = new_node
		self.nodes.add(new_node)

	def __getitem__(self, coords):
		return self.grid[coords[0]][coords[1]]

	def __setitem__(self, coords, new_node):
		self.grid[coords[0]][coords[1]] = new_node

	def __repr__(self):
		out = '  '
		for x in xrange(len(self.grid)):
			out = "{}{: >2}".format(out, x)
		out += '\n'
		for y in xrange(len(self.grid[0])):
			out = "{}{: >2}".format(out, y)
			if y%2==1:
				out += ' '
			for x in xrange(len(self.grid)):
				if self[x, y] == None:
					out += "--"
				elif self[x, y].contents.empty():
					# out += "_{}".format(self[x, y].num_neighbors())
					out += "__"
				else:
					item = self[x,y].contents.peek()
					if isinstance(item, Piece):
						ascii = "{}{}".format(item.owner.id, item.range)
					else:
						ascii = item.id
					if len(ascii) == 1:
						out += "_{}".format(ascii)
					else:
						out += ascii[:2]
			out += '\n'
		return out

	def gui_output(self):
		out = {}
		out['size'] = "{},{}".format(self.width, self.height)
		out['nodes'] = [node.coord for node in self.nodes]
		out['homes'] = {str(list(home.coord)):home.contents.peek().owner.id for home in self.home_nodes}
		return json.dumps(out)



class Node:
	def __init__(self, coord, NE=None, E=None, SE=None, SW=None, W=None, NW=None):
		self.dirs = {"NE": NE, "E":E, "SE":SE, "SW":SW, "W":W, "NW":NW}
		self.coord = coord
		self.contents = []

	# returns directions in which there are no neighbors.
	# used in building board
	def empty_adj(self):
		out = []
		for d in self.dirs:
			if self[d] == None:
				out.append(d)
		return out

	# returns neighboring nodes
	def neighbors(self):
		out = []
		for v in self.dirs.values():
			if v != None:
				out.append(v)
		return out

	# true if there are neighboring nodes in all 6 directions
	def landlocked(self):
		for d in self.dirs.values():
			if d == None:
				return False
		return True

	def num_neighbors(self):
		i=0
		for d in self.dirs.values():
			if d != None:
				i += 1
		return i

	def dist(self, n):
		if isinstance(n, Node):
			target = n.coord
		elif len(n) == 2:
			target = n
		else:
			raise Exception("Must pass in a Node or coordinate pair.")
		if self.coord == target:
			return 0
		distance = 1
		to_check = set(self.neighbors())
		checked_last = set()
		while True:
			next_to_check = []
			for n in to_check:
				if n.coord == target:
					return distance
				next_to_check.extend(n.neighbors())

			next_to_check = set(next_to_check) - to_check - checked_last
			checked_last = to_check
			to_check = next_to_check
			distance += 1
			if len(next_to_check) == 0:
				return None

	def __getitem__(self, dir):
		return self.dirs[dir]

	def __setitem__(self, dir, other_node):
		self.dirs[dir] = other_node

	def __repr__(self):
		out = {}
		out['type'] = "node"
		out['coord'] = self.coord
		out['neighbors'] = self.num_neighbors()
		out['contents'] = self.contents.peek().id if not self.contents.empty() else ""
		return json.dumps(out)




#
# extension of the set class which has peek() and empty() functions
class PeekSet(set):
	def peek(self, n=1):
		if n < 0:
			raise Exception("Cannot return less than 0 items.")

		if len(self) < n:
			raise Exception("Cannot peek at more items than the set contains.")
		
		if n == 1:
			return iter(self).next()
		else:
			out = []
			i = iter(self)
			for _ in xrange(n):
				out.append(i.next())

			return out

	def empty(self):
		return len(self) == 0


#
# Below are helper functions for the Board and Node classes

# returns a grid coord (x, y) offset by one unit in the given direction
def offset(coord, dir, xmax, ymax):
	if coord[1] % 2 == 0:
		if dir == "NE":
			return ((coord[0])%xmax, (coord[1]-1)%ymax)
		elif dir == "E":
			return ((coord[0]+1)%xmax, coord[1]%ymax)
		elif dir == "SE":
			return ((coord[0])%xmax, (coord[1]+1)%ymax)
		elif dir == "SW":
			return ((coord[0]-1)%xmax, (coord[1]+1)%ymax)
		elif dir == "W":
			return ((coord[0]-1)%xmax, coord[1])
		elif dir == "NW":
			return ((coord[0]-1)%xmax, (coord[1]-1)%ymax)
		else:
			raise Exception("Must specify a valid direction.")
	else:
		if dir == "NE":
			return ((coord[0]+1)%xmax, (coord[1]-1)%ymax)
		elif dir == "E":
			return ((coord[0]+1)%xmax, coord[1]%ymax)
		elif dir == "SE":
			return ((coord[0]+1)%xmax, (coord[1]+1)%ymax)
		elif dir == "SW":
			return ((coord[0])%xmax, (coord[1]+1)%ymax)
		elif dir == "W":
			return ((coord[0]-1)%xmax, coord[1])
		elif dir == "NW":
			return (coord[0]%xmax, (coord[1]-1)%ymax)
		else:
			raise Exception("Must specify a valid direction.")

# returns the opposite of the given direction
def opposite(dir):
	if dir == "NE":
		return "SW"
	if dir == "E":
		return "W"
	if dir == "SE":
		return "NW"
	if dir == "SW":
		return "NE"
	if dir == "W":
		return "E"
	if dir == "NW":
		return "SE"

class Player(models.Model):
	user = models.ForeignKey("User")
	game = models.ForeignKey("Game")

	def __init__(self, pieces, user=None, home_node=None):
		# I'm not sure how this will work yet, but a Player object
		# should connect to an actual player
		self.user = user
		
		# This is a turn_number:move dict
			# Each move is a Piece:Instruction dict
				# An instruction is a (string, loc) tuple,
				# where the string can be "move" or "spawn"
		self.moves = {}

		# Set of Piece objects
		self.pieces = pieces

		# atm I'm setting this after the player has already been constructed,
		#  with Home.set_owner(player)
		self.home_node=home_node

	def __getitem__(self, arg):
		if type(arg) == Node:
			for piece in self.pieces:
				if piece.loc == arg:
					return piece
			raise KeyError("Player {} doesn't seem to have a piece "\
					"at location ({},{}).".format(self.id, *arg.coord))

		if type(arg) == int:
			raise Exception("fix me!")
			arg = "{}{}".format(self.id, arg)

		if type(arg) == unicode:
			arg = arg.encode('ascii', 'ignore')

		if type(arg) == str:
			for piece in self.pieces:
				if piece.id == arg:
					return piece
			raise KeyError("Player {} doesn't seem to have a"\
					"pieces with id {}.".format(self.id, arg))

		raise Exception("Attempted to call __getitem__ function of player {}" \
				"with type {}".format(self.id, type(arg)))

	def vision(self):
		out = set()
		for piece in self.pieces:
			out.update(piece.vision())
		return out


	# Probably removing this as I change Piece IDs to actual names
	# def get_next_id(self):
	# 	current_ids = set([p.id for p in self.pieces])

	# 	i = 0
	# 	while True:
	# 		if "{}{}".format(self.id, i) not in current_ids:
	# 			return "{}{}".format(self.id, i)
	# 		i += 1

	def __repr__(self):
		out = {}
		out["type"] = "player"
		out["num_pieces"] = len(self.pieces)
		out["id"] = self.id
		return json.dumps(out)
