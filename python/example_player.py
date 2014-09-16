import random
import json

def get_vision(piece_loc, other_locs):
    # TODO
    return other_locs

def next_move(gamestate):
    print gamestate

    state = json.loads(gamestate)
    my_id = state.keys()[0]
    state = state[my_id]

    if my_id == "A":
        opponent = "B"
    else:
        opponent = "A"

    instructions = {}
    didspawn = False

    for piece, piece_info in state["pieces"]:
        # if the piece is on cooldown
        if piece_info["cd"]:
            continue
        
        if not didspawn:
            order = random.choice(['move', 'spawn'])
            didspawn = True
        else:
            order = 'move'

        if opponent in state["homes"]:
            destination = state["homes"][opponent]
        else:
            candidates = get_vision(piece_info["coord"], state["board"])
            destination = random.sample(candidates,1)[0]

        instructions[piece] = "{} {}".format(order, destination)

    return json.dumps(instructions)
    