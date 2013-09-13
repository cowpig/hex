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
    def peek(self):
        if len(self) == 0:
            raise Exception("Cannot peek into an empty set")
        return iter(self).next()

    def empty(self):
        return len(self) == 0

class Player:
    def __init__(self, id, pieces, connection=None):
        # I'm not sure how this will work yet, but a Player object
        # should connect to an actual player
        self.connection = connection
        
        # This is a turn_number:move dict
            # Each move is a Piece:Instruction dict
                # An instruction is a (string, loc) tuple,
                # where the string can be "move" or "spawn"
        self.moves = {}

        # Set of Piece objects
        self.pieces = pieces

        # id, usually 'A' or 'B'
        self.id = id

    def __getitem__(self, arg):
        if type(arg) == Node:
            for piece in self.pieces:
                if piece.loc == arg:
                    return piece
            raise KeyError("Player {} doesn't seem to have a piece "\
                    "at location ({},{}).".format(self.id, *arg.coord))

        if type(arg) == int:
            arg = "{}{}".format(self.id, arg)

        if type(arg) == str:
            for piece in self.pieces:
                if piece.id == arg:
                    return piece
            raise KeyError("Player {} doesn't seem to have a"\
                    "pieces with id {}.".format(self.id, arg))

        raise Exception("Attempted to call __getitem__ function of player {}" \
                "with type {}".format(self.id, type(arg)))



    def get_next_id(self):
        current_ids = set([p.id for p in self.pieces])

        i = 0
        while True:
            if "{}{}".format(self.id, i) not in current_ids:
                return "{}{}".format(self.id, i)
            i += 1

    def __repr__(self):
        out = {}
        out["type"] = "player"
        out["num_pieces"] = len(self.pieces)
        out["id"] = self.id
        return json.dumps(out)

# 
# This represents any object that can appear within the "contents" of
# a hex Node. All such classes are children of this class.
class Item(object):
    def __init__(self, loc, owner, id=""):
        self.owner = owner
        self.loc = loc
        loc.contents.add(self)
        self.id = id

    def remove(self):
        self.loc.contents.remove(self)

class Home(Item):
    def __init__(self, loc, owner=None):
        super(Home, self).__init__(loc, owner, owner.id if owner != None else '#')

    def set_owner(self, player):
        self.owner = player
        self.id = self.owner.id if self.owner != None else '#'

    def __repr__(self):
        return "{}'s home".format(self.owner)

class Piece(Item):
    def __init__(self, loc, owner, id, range, cooldown=0):
        super(Piece, self).__init__(loc, owner, id)
        # Distance, in hexes, that this Piece can see or move
        self.range = range

        # Turns until this Piece can move or spawn
        self.cooldown = cooldown

        # Update the player object with this piece
        owner.pieces.add(self)

    def remove(self):
        self.owner.pieces.remove(self)
        self.loc.contents.remove(self)

    def can_move_to(self, loc):
        if self.cooldown != 0:
            return False
        
        if not loc in self.vision():
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

    def __repr__(self):
        out = {}
        out['type'] = "piece"
        out['range'] = self.range
        out['id'] = self.id
        out['cooldown'] = self.cooldown
        out['owner'] = self.owner.id
        out['loc'] = self.loc.coord
        return json.dumps(out)



def combine(piece1, piece2, loc):
    owner = piece1.owner
    owner.pieces.remove(piece1)
    owner.pieces.remove(piece2)

    new_id = owner.get_next_id()

    new_range = piece1.range + piece2.range

    Piece(owner, new_id, new_range, loc)

def spawn_time(r):
    return sum([i*6 for i in range(r)])/2 + r + 5 

def combine_time(r):
    return (3+r) * 2