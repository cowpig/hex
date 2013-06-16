from game_library import *


class Game:
    def __init__(self, board, players):
        self.board = board
        # list of players, currently only supporting two
        self.players = players
        self.turn = 0
        self.moves = {}
        self.illegal_move_penalty = 10
        self.movement_cooldown = 5

        for i, player in enumerate(players):
            # Set the home nodes for each player
            board.home_nodes[i].contents.peek().set_owner(player)
            # Create the starting pieces for each player
            for neighbor in board.home_nodes[i].dirs.values():
                new_id = player.get_next_id()
                p = Piece(neighbor, player, new_id, 1)

    def next_move(self):
        player1, player2 = self.players
        moves = {}
        if self.turn in self.moves:
            moves.update(self.moves[self.turn])
        if self.turn in player1.moves:
            moves.update(player1.moves[self.turn])
        if self.turn in player2.moves:
            moves.update(player2.moves[self.turn])
        
        for p, order in moves.iteritems():
            if order[0] == "move":
                if p.can_move_to(order[1]):
                    p.move_to(order[1])
                    p.cooldown = self.movement_cooldown
                else:
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "spawn":
                if p.can_move_to(order[1]):
                    p.cooldown = spawn_time(p.range)
                    # only one piece can be created per player per turn
                    self.moves[self.turn+p.cooldown][p.owner] = ("new_piece", order[1])
                else:
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "new_piece":
                new_id = p.get_next_id()
                Piece(order[1], p, new_id, 1)

        for order, loc in moves.values():
            if len(loc.contents) > 1:
                self.resolve(loc)

    def resolve(self, loc):
        owners = set([item.owner for item in loc.contents])
        if len(owners) > 1:
            for item in loc.contents:
                if type(item) == Home:
                    end_game(item.owner)
                else:
                    del item
        else:
            new_range = 0
            for item in loc.contents:
                if type(item) == Piece:
                    new_range += item.range 
                    del item
            if new_range > 0:
                p = owners.pop()
                new_id = p.get_next_id()
                Piece(loc, p, new_id, new_range, cooldown=combine_time(new_range))

    def end_game(loser):
        pass


b = Board(40, 40)
g = Game(b, [Player("A", set()), Player("B", set())])
print b
p1, p2 = g.players
p1_moves = {}
for piece in p1.pieces:
    p1_moves[piece] = ("move", piece.loc["W"])

p1.moves[0] = p1_moves

g.next_move()
print b