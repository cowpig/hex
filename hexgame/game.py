import library as lib
import cPickle
import logging
import random
import json

class Game:
    def __init__(self, 
                board=None, 
                players=None, 
                moves=None,
                logger_level=logging.CRITICAL):
        logging.root.setLevel(logger_level)
        logging.info("constructor called")
        if players == None:
            players = [lib.Player("A", lib.PeekSet()), lib.Player("B", lib.PeekSet())]
        if moves == None:
            moves = {}

        if board == None:
            self.board = lib.Board(40,40)
        elif isinstance(board, lib.Board):
            self.board = board
        elif type(board) == tuple:
            self.board = lib.board(*board)
        else:
            raise AttributeError("The legal types for board parameter are: "\
                                    "None (autosize), Tuple (size), Board (pre-defined)")

        # list of players, currently only supporting two
        self.players = players
        self.turn = 0
        self.moves = moves
        self.illegal_move_penalty = 2
        self.movement_cooldown = 3
        self.game_over = False
        self.winner = None

        for player, home_node in zip(self.players, self.board.home_nodes):
            # Set the home nodes
            home_node.contents.peek().set_owner(player)
            
            # Create the starting pieces
            for neighbor in home_node.neighbors():
                p = lib.Piece(neighbor, player)
                logging.info("created {} at {} for {}".format(p.id, neighbor, player.id))

    def get_player(self, player_id):
        if not type(player_id) == str:
            raise Exception("player_id must be a string.")

        for player in self.players:
            if player.id == player_id:
                return player

        return None

    def next_move(self):
        logging.info("\n=====TURN {}=====\n".format(self.turn))
        player1, player2 = self.players
        moves = {}
        if self.turn in self.moves:
            moves.update(self.moves[self.turn])
        if self.turn in player1.moves:
            moves.update(player1.moves[self.turn])
        if self.turn in player2.moves:
            moves.update(player2.moves[self.turn])
        
        # Keep track of all moves so they can be saved to disk
        self.moves[self.turn] = moves

        for p, order in moves.iteritems():
            logging.info("Executing order:{}.{}({},{})".format(p.id, order[0], *order[1].coord))
            if order[0] == "move":
                if p.can_move_to(order[1]):
                    p.move_to(order[1])
                    p.cooldown = self.movement_cooldown
                    logging.info("\t{}.cooldown = {}, moved to ({},{})"\
                        .format(p.id, p.cooldown, *p.loc.coord))
                else:
                    logging.info("\tIllegal move detected. {}.cooldown {}->{}"\
                        .format(p.id, p.cooldown, p.cooldown+self.illegal_move_penalty))
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "spawn":
                # TODO: I think this needs some improvement
                if p.can_move_to(order[1]):
                    p.cooldown = lib.spawn_time(p.range)
                    # only one piece can be created per player per turn
                    if self.turn+p.cooldown not in self.moves:
                        self.moves[self.turn+p.cooldown] = {}
                    self.moves[self.turn+p.cooldown][p.owner] = ("new_piece", order[1])
                else:
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "new_piece":
                p_new = lib.Piece(order[1], p)
                logging.info("\t{} created at ({},{})".format(p_new.id, *p_new.loc.coord))

        for order, loc in moves.values():
            if len(loc.contents) > 1:
                self.resolve(loc, moves)

        # decrement all the cooldowns
        for piece in player1.pieces:
            if piece.cooldown > 0 and piece not in moves:
                piece.cooldown -= 1
        for piece in player2.pieces:
            if piece.cooldown > 0 and piece not in moves:
                piece.cooldown -= 1

        self.turn += 1

    def resolve(self, loc, moves):
        logging.info("Resolving conflict at ({},{})".format(*loc.coord))
        to_remove = set()
        
        owners = set([item.owner for item in loc.contents])
        player1, player2 = self.players

        if (player1 in owners) and (player2 in owners):
            attackers = set()
            for item in loc.contents:
                if isinstance(item, lib.Home):
                    logging.info("Home base {} has been captured! "\
                        "The game is over.".format(item))
                    self.end_game(item.owner)
                    return
                if item in moves:
                    logging.info("\t{} moved this turn; {} is registered as an attacker"\
                        .format(item.id, item.owner.id))
                    attackers.add(item.owner)

            for item in loc.contents:
                if self.opponent(item.owner) in attackers:
                    to_remove.add(item)

            for item in to_remove:
                logging.info("\tremoving {} at ({},{})".format(item.id, *loc.coord))
                item.remove()
        else:
            new_range = 0
            # if we add items other than  Pieces and Home bases, this while condition will have to change
            while len(loc.contents) > 1:
                p1, p2 = loc.contents.peek(2)
                logging.info("\tcombining pieces {} and {} at ({}, {})".format(p1.id, p2.id, *loc.coord))
                lib.combine(p1, p2)

    def opponent(self, player):
        if isinstance(player, lib.Item):
            player = item.owner
        if isinstance(player, lib.Player):
            if self.players[0] == player:
                return self.players[1]
            elif self.players[1] == player:
                return self.players[0]
            else:
                raise Exception("Player {} is not in this game.".format(player.id))
        raise TypeError("opponent(p) can take a Player or Item as a parameter.")

    def end_game(self, loser):
        self.winner = self.opponent(loser)
        self.game_over = True

    # Assuming no bugs, only the player IDs would have to be saved, rather than their
        # entire moves dicts
    def save_game(self, filename):
        with open(filename, 'wb') as f:
            cPickle.dump(f, [self.board, self.players, self.moves, self.turn])

    def get_game_state(self, players=None):
        out = {}
        if players == None:
            players = self.players
            out["board"] = self.board.to_dict()
            out["ascii"] = self.board.__str__()

        for player in players:
            homes = {player.id : str(player.home_node)}
            if self.opponent(player).home_node in player.vision():
                homes[self.opponent(player).id] = self.opponent(player).home_node
            player_info = {
                        "pieces" : [p.to_dict() for p in player.pieces],
                        "homes" : homes,
                        "vision" : {
                            str(node) : node.contents_string() for node in player.vision()
                        },
                        "board" : str((self.board.width, self.board.height))
                    }
            out[player.id] = player_info

        return out

    def gui_output_for_node(self, node):
        raise Exception("deprecated")
        out = {}
        out['coord'] = node.coord
        out['id'] = node.contents.peek().demo_id() if not node.contents.empty() else ""
        out['vis'] = ""
        for player in self.players:
            if node in player.vision():
                out['vis'] += player.id
        return out

    def gui_output(self):
        raise Exception("deprecated")
        return json.dumps([self.gui_output_for_node(n) for n in self.board.nodes], 
                            separators=(',',':'))

def load_game(filename, go_to_turn=False):
    with open(filename, 'rb') as f:
        board, players, moves, turn = cPickle.load(filename)
    for player in players:
        player.pieces = lib.PeekSet()
    game = Game(board, players, moves)
    if go_to_turn:
        for i in xrange(turn):
            game.next_move()
    return game


def test_game():
    b = lib.Board(40, 40)
    g = Game(b)
    g.log_to_terminal = True
    print b
    p1, p2 = g.players

    p1_moves = {}

    p1_moves[p1[0]] = ("move", p1[0].loc["NW"])
    p1_moves[p1[5]] = ("move", p1[5].loc["E"])
    p1_moves[p1[3]] = ("move", p1[3].loc["NE"])
    p1_moves[p1[4]] = ("move", p1[4].loc["W"])

    p1.moves[0] = p1_moves

    g.next_move()
    print b
    for piece in p1.pieces:
        print piece

    p1[0].move_to(p2[0].loc["E"]["E"])
    p1[3].move_to(p2[0].loc["NE"])

    while p1[0].cooldown != 0:
        g.next_move()

    p1_moves = {}
    p2_moves = {}

    print p1[0].can_move_to(p2[2].loc)
    print p1[0].loc.dist(p2[2].loc)
    print ["{},{}".format(*n.coord) for n in p1[0].vision()]

    print ["{},{}".format(*n.coord) for n in p1[3].vision()]

    p1_moves[p1[0]] = ("move", p2[4].loc)
    p1_moves[p1[3]] = ("move", p2[0].loc["E"])
    p2_moves[p2[0]] = ("move", p2[0].loc["E"])

    p1.moves[g.turn] = p1_moves
    p2.moves[g.turn] = p2_moves

    g.next_move()
    print b

def make_random_moves(player, game):
    player.moves[game.turn] = {}
    didspawn = False
    for piece in player.pieces:
        if not didspawn:
            order = random.choice(['move', 'spawn'])
            didspawn = True
        else:
            order = 'move'
        if piece.cooldown == 0:
            player.moves[game.turn][piece] = (order, random.sample(piece.vision(),1)[0])

# both players move completely randomly
def random_game(store_gamelog=False):
    gamelog = []
    b = lib.Board(20, 20)
    g = Game(b, [lib.Player("A", lib.PeekSet()), lib.Player("B", lib.PeekSet())])
    g.log_to_terminal = True
    print b
    p1, p2 = g.players
    from time import sleep
    import random
    while not g.game_over:
        for player in g.players:
            make_random_moves(player, g)
        g.next_move()
        print b
        gamelog.append([n.gui_output() for n in b.nodes])
        sleep(0.05)

    gamelog.append([n.gui_output() for n in b.nodes])
    if store_gamelog:
        with open("demo_log.txt", "wb") as f:
            f.write(json.dumps(gamelog))

def make_nearly_random_moves(player, game, board):
    player.moves[game.turn] = {}
    didspawn = False
    moved = False
    for piece in player.pieces:
        if not didspawn:
            order = random.choice(['move', 'spawn'])
            didspawn = True
        else:
            order = 'move'
        if piece.cooldown == 0:
            if game.opponent(player).home_node in piece.vision():
                player.moves[game.turn][piece] = ("move", game.opponent(player).home_node)
                moved = True
            else:
                candidates = piece.vision() - set(board.home_nodes)
                player.moves[game.turn][piece] = ("move", random.sample(candidates,1)[0])
                moved = True
    return moved

# this is a stupid gameplaying algorithm designed just to create a watchable demo

def dumb_game(store_gamelog=False):
    gamelog = []
    b = lib.Board(20, 20)
    g = Game(b, [lib.Player("A", lib.PeekSet()), lib.Player("B", lib.PeekSet())])
    g.log_to_terminal = False
    print b
    p1, p2 = g.players
    from time import sleep
    import random
    lines_logged = 0
    while not g.game_over:
        for player in g.players:
            moved = make_nearly_random_moves(player, g, b)
        g.next_move()
        print b
        if moved and lines_logged < 20:
            gamelog.append([g.gui_output_for_node(n) for n in b.nodes])
        sleep(0.05)

    if store_gamelog:
        with open("demo_log.txt", "wb") as f:
            f.write("var input=")
            f.write(json.dumps(gamelog))
            f.write(";")

if __name__ == "__main__":
    dumb_game()
