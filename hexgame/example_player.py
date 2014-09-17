import random
import json

def vision_for_piece(piece_loc, vision):
    # TODO
    return vision.keys()

def next_move(gamestate):
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
            candidates = vision_for_piece(piece["loc"], state["vision"])
            destination = random.choice(candidates)

        instructions[piece["id"]] = "{} {}".format(order, destination)

    return json.dumps(instructions)
    