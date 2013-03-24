import json, random

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

        # "NE":(0,-1),\
        # "E":(1,0),\
        # "SE":(0,1),\
        # "SW":(-1,1),\
        # "W":(-1,0),\
        # "NW":(-1,-1)}

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

class Player:
    def __init__(self, pieces, connection):
        self.pieces = pieces
        self.connection = connection

    def __repr__(self):
        out = {}
        out["type"] = "player"
        out["pieces"] = "pieces"
        return out


class Piece:
    def __init__(self, owner, id, range, cooldown=0):
        self.range = range
        self.id = id
        self.cooldown = cooldown
        self.owner = owner

    def __repr__(self):
        out = {}
        out['type'] = "piece"
        out['range'] = self.range
        out['id'] = self.id
        out['cooldown'] = self.cooldown
        out['owner'] = self.owner
        return json.dumps(out)

class Board:
    def __init__(self, width, height):
        self.grid = []
        for x in xrange(width):
            self.grid.append(range(height))

        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                self.grid[x][y] = None

        start = Node((random.randrange(width), random.randrange(height)))
        self.grid[start.coord[0]][start.coord[1]] = start
        self.nodes = [start]
        coastal = [start]
        self.log = []

        for i in xrange(int((width*height)/1.5)):
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
                other = self.grid[x][y]

                if other != None:
                    new_node.dirs[dir] = self.grid[x][y]
                    self.grid[x][y].dirs[opposite(dir)] = new_node
                    s = "connecting node {} at {} to node {} at {} | direction {}-{}".\
                    format(new_node, new_node.coord, self.grid[x][y], self.grid[x][y].coord\
                        , dir, opposite(dir))
                    self.log.append(s)

            # put it on the grid
            self.grid[new_node.coord[0]][new_node.coord[1]] = new_node
            self.nodes.append(new_node)
            if not n.landlocked():
                coastal.append(new_node)


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
                out += "_{}".format(self.grid[x][y].num_neighbors()) if self.grid[x][y] != None else "--"
            out += '\n'
        return out

class Node:
    def __init__(self, coord, NE=None, E=None, SE=None, SW=None, W=None, NW=None):
        self.dirs = {"NE": NE, "E":E, "SE":SE, "SW":SW, "W":W, "NW":NW}
        self.coord = coord
        self.contents = None

    def empty_adj(self):
        out = []
        for d in self.dirs:
            if self.dirs[d] == None:
                out.append(d)
        return out

    def neighbors(self):
        out = []
        for d in self.dirs:
            if self.dirs[d] != None:
                out.append(d)
        return out

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

    def __repr__(self):
        out = {}
        out['type'] = "node"
        out['coord'] = self.coord
        out['neighbors'] = self.num_neighbors()
        out['contents'] = self.contents
        return json.dumps(out)

