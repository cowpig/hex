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
    # note: the home bases of each player will be 
    def __init__(self, width, height):
        self.grid = []
        for x in xrange(width):
            self.grid.append(range(height))

        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                self.grid[x][y] = None

        start = Node((random.randrange(width), random.randrange(height)))
        start.contents = home_base("player1", start)
        self[start.coord[0], start.coord[1]] = start
        self.nodes = [start]
        self.home_nodes = [start]
        coastal = [start]

        nodes_between_homes = min(height, width)/2
        random_dir = random.choice(start.dirs.keys())
        n = start
        for i in xrange(nodes_between_homes):
            new_coord = offset(n.coord, random_dir, width, height)
            new_node = Node(new_coord)
            n[random_dir] = new_node
            new_node[opposite(random_dir)] = n


            self[new_node.coord[0], new_node.coord[1]] = new_node
            self.nodes.append(new_node)
            coastal.append(new_node)
            
            if i == nodes_between_homes - 1:
                n.contents = home_base("player2", n)
                self.home_nodes.append(n)
            
            n = new_node

        for i in xrange(int((width*height)/1.5) - nodes_between_homes):
            # find a coastal node to expand
            while True:
                n = coastal[random.randrange(len(coastal))]
                if not n.landlocked():
                    break
                coastal.remove(n)

            # create a new node
            nextdir = random.choice(n.empty_adj())
            new_coord = offset(n.coord, nextdir, width, height)
            new_node = Node((new_coord))

            # connect it to its neighbors
            for dir in new_node.dirs:
                x, y = offset(new_coord, dir, width, height)
                other = self[x, y]

                if other != None:
                    new_node[dir] = self[x, y]
                    self[x, y][opposite(dir)] = new_node

            # put it on the grid
            self[new_node.coord[0], new_node.coord[1]] = new_node
            self.nodes.append(new_node)
            if not n.landlocked():
                coastal.append(new_node)

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
                if self.grid[x][y] == None:
                    out += "--"
                elif self.grid[x][y].contents == None:
                    out += "_{}".format(self.grid[x][y].num_neighbors())
                else:
                    out += "_{}".format(self.grid[x][y].contents.ascii)
            out += '\n'
        return out

class Node:
    def __init__(self, coord, NE=None, E=None, SE=None, SW=None, W=None, NW=None):
        self.dirs = {"NE": NE, "E":E, "SE":SE, "SW":SW, "W":W, "NW":NW}
        self.coord = coord
        self.contents = None

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

    def __getitem__(self, dir):
        return self.dirs[dir]

    def __setitem__(self, dir, other_node):
        self.dirs[dir] = other_node

    def __repr__(self):
        out = {}
        out['type'] = "node"
        out['coord'] = self.coord
        out['neighbors'] = self.num_neighbors()
        out['contents'] = self.contents
        return json.dumps(out)

#
# Below are helper functions for the Board and Node classes

# returns a grid coord (x, y) offset by one unit in the given direction
def offset(coord, dir, xmax, ymax):
    if coord[1] % 2 == 0:
        if dir == "NE":
            return ((coord[0])%xmax, (coord[1]-1)%ymax)
        if dir == "E":
            return ((coord[0]+1)%xmax, coord[1]%ymax)
        if dir == "SE":
            return ((coord[0])%xmax, (coord[1]+1)%ymax)
        if dir == "SW":
            return ((coord[0]-1)%xmax, (coord[1]+1)%ymax)
        if dir == "W":
            return ((coord[0]-1)%xmax, coord[1])
        if dir == "NW":
            return ((coord[0]-1)%xmax, (coord[1]-1)%ymax)
        else:
            raise Exception("Must specify a valid direction.")
    else:
        if dir == "NE":
            return ((coord[0]+1)%xmax, (coord[1]-1)%ymax)
        if dir == "E":
            return ((coord[0]+1)%xmax, coord[1]%ymax)
        if dir == "SE":
            return ((coord[0]+1)%xmax, (coord[1]+1)%ymax)
        if dir == "SW":
            return ((coord[0])%xmax, (coord[1]+1)%ymax)
        if dir == "W":
            return ((coord[0]-1)%xmax, coord[1])
        if dir == "NW":
            return (coord[0]%xmax, (coord[1]-1)%ymax)
        else:
            raise Exception("Must specify a valid direction.")

        # "NE":(0,-1),\
        # "E":(1,0),\
        # "SE":(0,1),\
        # "SW":(-1,1),\
        # "W":(-1,0),\
        # "NW":(-1,-1)}

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



# These gameplay objects are not yet set in stone

class Game:
    def __init__(self, board, player1, player2):
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.move_numer = 0

    def next_move(self):
        pass
        # move order phase

class Player:
    def __init__(self, pieces, connection):
        # I'm not sure how this will work yet, but a Player object
        # should connect to an actual player
        self.connection = connection
        # Each move is a Piece:Instruction dict
        self.moves = []
        # Set of Piece objects
        self.pieces = pieces

    def __repr__(self):
        out = {}
        out["type"] = "player"
        out["pieces"] = self.pieces
        return json.dump(out)

def home_base(player, loc):
    description = "Home base for player {}".format(player)
    return Item(player, loc, description, "#")

class Item:
    def __init__(self, owner, loc, description, ascii):
        self.owner = owner
        self.loc = loc
        self.description = description
        self.ascii = ascii

    def __repr__(self):
        out = {}
        out["type"] = "base"
        out["owner"] = self.owner
        out['loc'] = self.loc
        return json.dump(out)

class Piece:
    def __init__(self, owner, id, range, loc, cooldown=0):
        # Distance, in hexes, that this Piece can see or move
        self.range = range
        # Identifying string
        self.id = id
        # Turns until this Piece can move or spawn
        self.cooldown = cooldown
        # Player that owns the Piece
        self.owner = owner
        # Node in which the Piece currently is
        self.loc = loc
        # Let that node know it's there
        loc.contents = self

    def move(self, loc):
        if self.cooldown == 0:
            cooldown += 1

        if not loc in self.vision():
            cooldown += 1
            return "{} received a penalty of 1 for making an illegal move"


    def vision(self):
        seen = set([self.loc])
        to_check = set(self.loc.neighbors())
        depth = self.range
        while depth > 0:
            new_nodes = set()
            while len(to_check) > 0:
                n = to_check.pop()
                if n != None:
                    seen.add(n)
                    if n.contents == None:
                        new_nodes = new_nodes.union(set(n.neighbors()))
            to_check = new_nodes - seen
            depth -= 1
        return seen

    def __repr__(self):
        out = {}
        out['type'] = "piece"
        out['range'] = self.range
        out['id'] = self.id
        out['cooldown'] = self.cooldown
        out['owner'] = self.owner
        out['loc'] = self.loc.coord
        return json.dumps(out)
