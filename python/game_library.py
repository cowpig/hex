import json, random


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

class Board:
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
		self.contents = PeekSet()

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
# This represents any object that can appear within the "contents" of
# a hex Node. All such classes are children of this class.
class Item(object):
	def __init__(self, loc, owner, id=""):
		self.owner = owner
		self.loc = loc
		loc.contents.add(self)
		self.id = id

	def demo_id(self):
		return self.id

	def remove(self):
		self.loc.contents.remove(self)

class Home(Item):
	def __init__(self, loc, owner=None):
		super(Home, self).__init__(loc, owner, owner.id if owner != None else '#')

	def set_owner(self, player):
		self.owner = player
		if self.owner != None:
			self.id = self.owner.id
			self.owner.home_node = self.loc
		else:
			self.id = '#'

	def __repr__(self):
		return "{}'s home".format(self.owner)

class Piece(Item):
	names = ["Abby","Abel","Abie","Acey","Acie","Adah","Adam","Adan","Adda","Adel","Aden","Adin","Aida","Aili","Ajay","Alan","Alba","Alby","Alda","Aldo","Alec","Alek","Alex","Alia","Alla","Ally","Alma","Alta","Alto","Alva","Alvy","Alys","Amey","Amie","Amil","Amin","Amir","Amit","Amma","Amon","Amos","Amya","Andy","Anie","Anna","Anne","Anya","Arah","Arba","Arch","Aria","Aric","Arie","Arla","Arlo","Arly","Arne","Arno","Aron","Arra","Arta","Arvo","Asha","Asia","Ason","Atha","Audy","Aura","Avie","Avis","Avon","Axel","Ayla","Babe","Baby","Bama","Barb","Bart","Beau","Bebe","Beda","Bell","Bena","Bert","Bess","Beth","Bill","Bina","Bird","Birt","Blas","Bode","Bose","Boss","Boyd","Brad","Brea","Bree","Bret","Bria","Bryn","Buck","Budd","Buel","Bula","Buna","Bunk","Burk","Burl","Burr","Burt","Bush","Byrd","Cade","Cael","Cain","Cale","Cali","Cami","Cara","Cari","Carl","Caro","Cary","Case","Cash","Cass","Cato","Ceil","Cena","Chad","Chas","Chaz","Cher","Chet","Chin","Chip","Ciji","Clay","Clem","Cleo","Cloe","Coby","Codi","Cody","Coen","Cole","Colt","Cora","Cori","Cory","Coty","Cris","Cruz","Cuba","Curt","Daja","Dale","Dana","Dane","Dani","Dann","Dara","Darl","Dave","Davy","Dawn","Dean","Debi","Deja","Dell","Dema","Demi","Dena","Deon","Derl","Desi","Dian","Dick","Dicy","Dina","Dink","Dino","Dion","Dirk","Diya","Dock","Dola","Doll","Dona","Donn","Dora","Dori","Dorr","Doss","Doug","Dove","Drew","Duff","Duke","Dwan","Dyan","Earl","Ebba","Eben","Eber","Echo","Eddy","Eden","Edie","Edla","Edna","Edra","Effa","Eino","Elam","Elba","Elby","Elda","Elex","Elia","Elie","Ella","Elle","Elma","Elmo","Elna","Elon","Eloy","Elsa","Else","Elta","Elva","Elza","Elzy","Emil","Emit","Emma","Emmy","Emry","Enid","Enos","Enzo","Eola","Erby","Eric","Erie","Erik","Erin","Eris","Erla","Erle","Erma","Erna","Eryn","Esau","Esco","Essa","Esta","Etha","Etna","Etta","Eula","Euna","Eura","Evan","Ever","Evia","Evie","Evon","Ewin","Exie","Ezra","Fate","Fawn","Faye","Ferd","Fern","Finn","Flem","Flor","Floy","Foch","Ford","Fran","Fred","Gabe","Gael","Gage","Gail","Gale","Gary","Gaye","Gena","Gene","Geno","Geri","Gigi","Gina","Gino","Glen","Gray","Greg","Guss","Gust","Gwen","Gwyn","Hale","Hali","Hall","Hamp","Hana","Hank","Hans","Harl","Harm","Hart","Hays","Hedy","Herb","Hill","Hoke","Hope","Hoyt","Huey","Hugh","Hugo","Hung","Hunt","Icey","Icie","Ilah","Ilda","Illa","Ilma","Ines","Inez","Inga","Iola","Iona","Ione","Iris","Irma","Irva","Isai","Isam","Isis","Isla","Isom","Ivah","Ivan","Iver","Ivey","Ivie","Ivor","Jace","Jack","Jada","Jade","Jair","Jake","Jame","Jami","Jana","Jane","Jann","Jase","Jaye","Jean","Jeff","Jena","Jens","Jere","Jeri","Jess","Jett","Jill","Joan","Jobe","Jodi","Jody","Joel","Joey","John","Joni","Jory","Jose","Josh","Joye","Jrue","Juan","Judd","Jude","Judi","Judy","Jule","Juli","June","Kaci","Kacy","Kade","Kael","Kaia","Kala","Kale","Kali","Kami","Kane","Kara","Kari","Karl","Kate","Kati","Katy","Kaya","Kaye","Keli","Kent","Keon","Keri","Kian","Kiel","King","Kipp","Kira","Kirk","Kirt","Kiya","Knox","Kobe","Koby","Koda","Kody","Koen","Kole","Kori","Kory","Kris","Kurt","Kyan","Kyla","Kyle","Kyra","Laci","Lacy","Lady","Lafe","Lala","Lana","Lane","Lani","Lara","Lark","Lars","Lary","Leah","Leda","Leia","Leif","Lela","Lena","Leon","Lera","Lesa","Less","Leta","Leva","Levi","Levy","Lexi","Liam","Lida","Lige","Lila","Lily","Lina","Link","Linn","Lisa","Lise","Lish","Lita","Liza","Loda","Lois","Lola","Loma","Lona","Lone","Long","Loni","Lora","Lori","Lota","Lott","Love","Loyd","Luca","Lucy","Luda","Luis","Luka","Luke","Lula","Lulu","Luna","Lupe","Lura","Lute","Lyda","Lyla","Lyle","Lynn","Mace","Maci","Mack","Macy","Maia","Male","Mame","Mara","Marc","Mari","Mark","Mart","Mary","Math","Matt","Maud","Maya","Maye","Mayo","Meda","Mell","Mena","Merl","Meta","Miah","Mike","Mila","Milo","Mima","Mimi","Mina","Mira","Miya","Mona","Mont","Mora","Mose","Murl","Myah","Myer","Myla","Myra","Myrl","Nada","Nana","Nash","Neal","Neha","Neil","Nell","Nels","Nena","Neta","Neva","Newt","Nick","Nico","Niki","Niko","Nila","Nile","Nils","Nina","Nira","Nita","Noah","Noel","Nola","Noma","Nona","Nora","Nova","Nyah","Nyla","Obed","Obie","Ocie","Octa","Odie","Odin","Odis","Odus","Okey","Olaf","Olan","Olar","Olen","Oley","Olga","Olie","Olin","Olof","Omar","Omer","Omie","Oney","Onie","Opal","Opha","Orah","Oral","Oran","Oren","Orie","Orin","Oris","Orla","Orlo","Orma","Orra","Osie","Otha","Otho","Otis","Otto","Ovid","Owen","Ozie","Page","Park","Pate","Paul","Pete","Phil","Pink","Ples","Polk","Purl","Rafe","Rahn","Rand","Raul","Reba","Reed","Reid","Rena","Rene","Reno","Reta","Reva","Rhea","Rhys","Rian","Rice","Rich","Rick","Rico","Risa","Rita","Riya","Robb","Robt","Roby","Rock","Roel","Rolf","Roll","Roma","Rome","Rona","Roni","Rory","Rosa","Rose","Ross","Rosy","Roxy","Rube","Rubi","Ruby","Rudy","Ruel","Ruie","Rush","Russ","Ruth","Ryan","Ryne","Sada","Sade","Sage","Sara","Saul","Scot","Sean","Sena","Seth","Shad","Shae","Shan","Shay","Shea","Shep","Shon","Sina","Sing","Skip","Skye","Stan","Star","Sula","Suzy","Syed","Taft","Tahj","Taja","Tami","Tana","Tara","Tari","Tate","Taya","Tena","Tera","Teri","Tess","Thad","Thea","Theo","Thor","Thos","Tina","Tiny","Tisa","Tito","Tobe","Tobi","Toby","Todd","Toma","Toni","Tony","Tori","Tory","Toya","Trae","Trey","Troy","Tuan","Tula","Tyra","Vada","Vara","Veda","Vela","Vena","Vera","Vere","Verl","Vern","Veta","Veva","Vick","Vicy","Vida","Vina","Vira","Vita","Vito","Viva","Wade","Walt","Ward","Wash","Watt","Wava","Webb","Wess","West","Whit","Will","Wing","Wirt","Wong","Wood","Xena","Yair","Yoel","York","Zack","Zada","Zaid","Zain","Zana","Zane","Zara","Zeke","Zela","Zena","Zeno","Zeta","Zina","Zion","Zita","Zoey","Zoie","Zola","Zona","Zora","Zula"]

	def __init__(self, loc, owner, id=None, range=1, cooldown=0):
		if id == None:
			id = Piece.names.pop(random.randint(0,len(Piece.names)))

		super(Piece, self).__init__(loc, owner, id)
		# Distance, in hexes, that this Piece can see or move
		self.range = range

		# Turns until this Piece can move or spawn
		self.cooldown = cooldown

		# Update the player object with this piece
		owner.pieces.add(self)

		loc.contents.add(self)
		owner.pieces.add(self)

	def remove(self):
		self.owner.pieces.remove(self)
		self.loc.contents.remove(self)

	def can_move_to(self, loc):
		if self.cooldown != 0:
			return False
		
		if not loc in self.vision():
			return False

		if loc == self.owner.home_node:
			return False
		
		return True

	def move_to(self, loc):
		self.loc.contents.remove(self)
		self.loc = loc
		loc.contents.add(self)


	def vision(self):
		seen = set([self.loc])
		to_check = set(self.loc.neighbors())
		depth = self.range
		while depth > 0:
			new_nodes = set()
			for n in to_check:
				seen.add(n)
				if n.contents.empty():
					new_nodes.update(n.neighbors())
			to_check = new_nodes - seen
			depth -= 1
		return seen

	def demo_id(self):
		return "{}{}".format(self.owner.id, self.range)

	def __repr__(self):
		out = {}
		out['r'] = self.range
		out['id'] = self.id
		out['cd'] = self.cooldown
		out['loc'] = self.loc.coord
		return json.dumps(out)

def combine_time(r):
	return (3+r) * 2

def combine(piece1, piece2):
	assert(piece1.loc == piece2.loc)
	assert(piece1.owner == piece2.owner)
	
	piece1.remove()
	piece2.remove()

	if piece1.range >= piece2.range:
		new_id = piece1.id
		Piece.names.append(piece2.id)
	else:
		new_id = piece2.id
		Piece.names.append(piece1.id)

	new_range = piece1.range + piece2.range

	Piece(piece1.loc, piece1.owner, new_id, new_range, combine_time(new_range))


def spawn_time(r):
	return sum([i*6 for i in range(r)])/2 + r + 5 

