import random
import json
import os.path
import os
import sys

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


# returns a list of nodes that are within one hexagon of a given piece
def vision_for_piece(piece, loc_dict, board_size):
    out = set()
    
    # not actually using range atm
    piece_range = piece["r"]

    piece_loc = piece["loc"]
    board_size = eval(board_size)

    possible_dirs = ["NE", "E", "SE", "SW", "W", "NW"]

    # just return all the nodes within a distance of 1 now
    for d in possible_dirs:
        loc = str(offset(piece_loc, d, *board_size))
        if loc in loc_dict:
            out.add(loc)

    return list(out)

def wait_read_delete(filename):
    while not os.path.isfile(filename):
        continue
    with open(filename) as f:
        gamestate = f.read()
    
    os.remove(filename)
    return gamestate


# given a gamestate, return a json object that looks like this:
#   {
#       'piece_id' : 'order (destination)'
#   }
# where:
#   piece_id is the id of a piece (shockingly!)
#   order can be "move" or "spawn"
#   and destination is the (x, y) coordinates of a target node
def play_game(input_filename, output_filename):

    while True:
        gamestate = wait_read_delete(input_filename)

        state = json.loads(gamestate)

        my_id = state.keys()[0]
        state = state[my_id]

        if my_id == "A":
            opponent = "B"
        else:
            opponent = "A"

        instructions = {}
        didspawn = False

        for piece in state["pieces"]:
            # if the piece is on cooldown
            if piece["cd"]:
                continue
            
            if not didspawn:
                order = random.choice(['move', 'spawn'])
                didspawn = True
            else:
                order = 'move'

            if opponent in state["homes"]:
                destination = state["homes"][opponent]
            else:
                candidates = vision_for_piece(piece, state["vision"], state["board"])
                destination = random.choice(candidates)

            instructions[piece["id"]] = "{} {}".format(order, destination)

        with open(output_filename, "w") as f:
            f.write(json.dumps(instructions))

play_game(sys.argv[1], sys.argv[2])