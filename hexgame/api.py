from game import Game, make_nearly_random_moves
import io
import json

class PlayerConnection(object):
    def __init__(self, infile, outfile, userID):
        self.infile = infile
        self.outfile = outfile
        self.userID = userID

    def read(self):
        try:
            with open(self.infile, "rb") as f:
                return f.read()
        except Exception as e:
            print "error reading file {} :\n{}".format(self.infile, e)
            return ""

    def write(self, string):
        try:
            with open(self.outfile, "wb") as f:
                f.write(string)
        except Exception as e:
            print "error writing to file {} :\n{}".format(self.infile, e)

class GameApi(object):
    def __init__(self, A_conn, B_conn):
        self.connections = {"A" : A_conn, "B" : B_conn}
        self.game = None

    def repl_test(self, msg):
        try:
            exec msg
        except Exception as e:
            print e.message
            self.send("Error caught: %s" % e.message)
            
        self.send(self.game.gui_output())

    def new_game(self, *args):
        self.game = Game(*args)

        starting_state = self.game.get_game_state()

        self.push_state(starting_state)
        return self.game.get_game_state()

    def make_opponent_moves(self, player):
        make_nearly_random_moves(self.game.opponent(player), self.game, self.game.board)

    def next_move(self):
        # print "next move..."
        # print "A"
        # for piece in self.game.get_game_state()["A"]["pieces"]:
        #     print piece["id"], piece["loc"]
        # print "B"
        # for piece in self.game.get_game_state()["B"]["pieces"]:
        #     print piece["id"], piece["loc"]

        turn = self.game.turn
        for player in self.game.players:
            instructions = self.connections[player.id].read()
            # print "read from player ", player.id
            # print instructions
            player.moves[turn] = self.parse_instructions(player, instructions)
        
        self.game.next_move()
        new_state = self.game.get_game_state()

        self.push_state(new_state)

        return new_state

    def push_state(self, gamestate):
        for player_id, conn in self.connections.iteritems():
            # print "sending to player", player_id
            # print json.dumps({player_id : gamestate[player_id]})
            conn.write(json.dumps({player_id : gamestate[player_id]}))


    # parses a move input string
    def parse_instructions(self, player, input_str):
        moves = {}
        try:
            move_dict = json.loads(input_str)
            for piece_id, order_string in move_dict.iteritems():
                piece = player[piece_id]

                if order_string.startswith("move"):
                    order = "move"
                    dest_str = order_string[5:]
                elif order_string.startswith("spawn"):
                    order = "spawn"
                    dest_str = order_string[6:]
                else:
                    raise Exception("order should start with 'move' or 'spawn'")

                # we will allow destinations to be given in one of two ways
                #   E-E-SE, for destinations relative to the node
                #   (x,y) for absolute destinations
                if dest_str[0] == "(":
                    x, y = dest_str[1:-1].split(",")
                    dest = self.game.board[int(x), int(y)]
                else:
                    directions = dest_str.split("-")
                    dest = piece.loc
                    for direction in directions:
                        dest = dest[direction]

                moves[piece] = (order, dest)

        except Exception as e:
            msg = "Error parsing order string:\n\t{}".format(input_str)
            msg += "\nerror message:\n\t{}".format(e.message)
            # raise Exception(msg)
            print msg
            return {}
        
        return moves
