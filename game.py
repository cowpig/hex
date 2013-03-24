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

class Piece:
    def __init__(self, owner, id, range, cooldown=0):
        self.range = range
        self.id = id
        self.cooldown = cooldown
        self.owner = owner

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
            nextdir = random.choice(n.empty_neighbors())
            new_coord = offset(n.coord, nextdir, width, height)
            new_node = Node((new_coord))

            if self.grid[new_coord[0]][new_coord[1]] != None:
                import pdb
                pdb.set_trace()

            # connect it to its neighbors
            for dir in new_node.dirs:
                x, y = offset(new_coord, dir, width, height)
                other = self.grid[x][y]
                # try:
                if other != None:
                    new_node.dirs[dir] = self.grid[x][y]
                    self.grid[x][y].dirs[opposite(dir)] = new_node
                    s = "connecting node {} at {} to node {} at {} | direction {}-{}".\
                    format(new_node, new_node.coord, self.grid[x][y], self.grid[x][y].coord\
                        , dir, opposite(dir))
                    self.log.append(s)
                # except:
                #     print self.__repr__()
                #     print "error binding {} and {}".format(new_node, other)

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

    def empty_neighbors(self):
        out = []
        for d in self.dirs:
            if self.dirs[d] == None:
                out.append(d)
        return out

    def nonempty_neighbors(self):
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
        return "Node object with {} neighbors at coord {}".format(self.num_neighbors(), self.coord)
