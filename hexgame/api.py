from game import Game, make_nearly_random_moves
import io
import json

class PlayerConnection(object):
    def __init__(self, infile, outfile, userID):
        self.infile = io.FileIO(infile, "rb")
        self.outfile = io.FileIO(outfile, "wb")
        self.userID = userID

class MockConnection(object):
    def __init__(self, infile, outfile, uid):
        self.infile = infile
        self.outfile = outfile
        self.uid = uid

class MockFile(object):
    def __init__(self, example_function):
        self.example_function = example_function
        self.fakefile = ""

    def read(self):
        return self.fakefile

    def writeline(self, string):
        self.fakefile = self.example_function(string)


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
            instructions = self.connections[player.id].infile.read()
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
            try:
                conn.outfile.writeline(json.dumps({player_id : gamestate[player_id]}))
            except Exception as e:
                print e

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
            raise Exception(msg)
            print msg
            return {}
        
        return moves
