from game_library import *
import cPickle


class Game:
    def __init__(self, board, players, moves={}):
        self.board = board
        # list of players, currently only supporting two
        self.players = players
        self.turn = 0
        self.moves = moves
        self.illegal_move_penalty = 2
        self.movement_cooldown = 3
        self.log_str = ""
        self.log_to_terminal = False
        self.game_over = False

        for i, player in enumerate(players):
            # Set the home nodes for each player
            board.home_nodes[i].contents.peek().set_owner(player)
            # Create the starting pieces for each player
            for neighbor in board.home_nodes[i].dirs.values():
                new_id = player.get_next_id()
                p = Piece(neighbor, player, new_id, 1)

    def log(self, s):
        if self.log_to_terminal:
            print s
        self.log_str += s + "\n" 

    def next_move(self):
        self.log("\n=====TURN {}=====\n".format(self.turn))
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
            self.log("Executing order:{}.{}({},{})".format(p.id, order[0], *order[1].coord))
            if order[0] == "move":
                if p.can_move_to(order[1]):
                    p.move_to(order[1])
                    p.cooldown = self.movement_cooldown
                    self.log("\t{}.cooldown = {}, moved to ({},{})"\
                        .format(p.id, p.cooldown, *p.loc.coord))
                else:
                    self.log("\tIllegal move detected. {}.cooldown {}->{}"\
                        .format(p.id, p.cooldown, p.cooldown+self.illegal_move_penalty))
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "spawn":
                # TODO: I think this needs some improvement
                if p.can_move_to(order[1]):
                    p.cooldown = spawn_time(p.range)
                    # only one piece can be created per player per turn
                    if self.turn+p.cooldown not in self.moves:
                        self.moves[self.turn+p.cooldown] = {}
                    self.moves[self.turn+p.cooldown][p.owner] = ("new_piece", order[1])
                else:
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "new_piece":
                new_id = p.get_next_id()
                p_new = Piece(order[1], p, new_id, 1)
                self.log("\t{} created at ({},{})".format(p_new.id, *p_new.loc.coord))

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
        self.log("Resolving conflict at ({},{})".format(*loc.coord))
        to_remove = set()
        
        owners = set([item.owner for item in loc.contents])
        player1, player2 = self.players

        if (player1 in owners) and (player2 in owners):
            attackers = set()
            for item in loc.contents:
                if isinstance(item, Home):
                    self.log("Home base {} has been captured! "\
                        "The game is over.".format(item))
                    self.end_game(item.owner)
                    return
                if item in moves:
                    self.log("\t{} moved this turn; {} is registered as an attacker"\
                        .format(item.id, item.owner.id))
                    attackers.add(item.owner)

            for item in loc.contents:
                if self.opponent(item.owner) in attackers:
                    to_remove.add(item)

            for item in to_remove:
                self.log("\tremoving {} at ({},{})".format(item.id, *loc.coord))
                item.remove()
        else:
            new_range = 0
            for item in loc.contents:
                if type(item) == Piece:
                    new_range += item.range 
                    to_remove.add(item)

            for item in to_remove:
                self.log("\tremoving {} at ({},{})".format(item.id, *loc.coord))
                item.remove()

            if new_range > 0:
                p = owners.pop()
                new_id = p.get_next_id()
                Piece(loc, p, new_id, new_range, cooldown=combine_time(new_range))
                self.log("\t{} with range {} created at ({},{})".\
                    format(new_id, new_range, *loc.coord))

    def opponent(self, player):
        if isinstance(player, Item):
            player = item.owner
        if isinstance(player, Player):
            if self.players[0] == player:
                return self.players[1]
            elif self.players[1] == player:
                return self.players[0]
            else:
                raise Exception("Player {} is not in this game.".format(player.id))
        raise TypeError("opponent(p) can take a Player or Item as a parameter.")

    def end_game(self, loser):
        self.game_over = True

    # Assuming no bugs, only the player IDs would have to be saved, rather than their
        # entire moves dicts
    def save_game(self, filename):
        with open(filename, 'wb') as f:
            cPickle.dump(f, [self.board, self.players, self.moves, self.turn])

def load_game(filename, go_to_turn=False):
    with open(filename, 'rb') as f:
        board, players, moves, turn = cPickle.load(filename)
    for player in players:
        player.pieces = PeekSet()
    game = Game(board, players, moves)
    if go_to_turn:
        for i in xrange(turn):
            game.next_move()
    return game


b = Board(40, 40)
g = Game(b, [Player("A", PeekSet()), Player("B", PeekSet())])
g.log_to_terminal = True
print b
p1, p2 = g.players
# p1_moves = {}

# p1_moves[p1[0]] = ("move", p1[0].loc["NW"])
# p1_moves[p1[5]] = ("move", p1[5].loc["E"])
# p1_moves[p1[3]] = ("move", p1[3].loc["NE"])
# p1_moves[p1[4]] = ("move", p1[4].loc["W"])

# p1.moves[0] = p1_moves

# g.next_move()
# print b
# for piece in p1.pieces:
#     print piece

# p1[0].move_to(p2[0].loc["E"]["E"])
# p1[3].move_to(p2[0].loc["NE"])

# while p1[0].cooldown != 0:
#     g.next_move()

# p1_moves = {}
# p2_moves = {}

# print p1[0].can_move_to(p2[2].loc)
# print p1[0].loc.dist(p2[2].loc)
# print ["{},{}".format(*n.coord) for n in p1[0].vision()]

# print ["{},{}".format(*n.coord) for n in p1[3].vision()]

# p1_moves[p1[0]] = ("move", p2[4].loc)
# p1_moves[p1[3]] = ("move", p2[0].loc["E"])
# p2_moves[p2[0]] = ("move", p2[0].loc["E"])

# p1.moves[g.turn] = p1_moves
# p2.moves[g.turn] = p2_moves

# g.next_move()
# print b
from time import sleep
import random
while not g.game_over:
    for player in g.players:
        player.moves[g.turn] = {}
        didspawn = False
        for piece in player.pieces:
                if not didspawn:
                    order = random.choice(['move', 'spawn'])
                else:
                    oder = 'move'
                if piece.cooldown == 0:
                    player.moves[g.turn][piece] = (order, random.sample(piece.vision(),1)[0])
    g.next_move()
    print b
    sleep(0.05)