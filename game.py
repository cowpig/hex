from game_library import *


class Game:
    def __init__(self, board, players):
        self.board = board
        # list of players, currently only supporting two
        self.players = players
        self.turn = 0
        self.moves = []
        self.illegal_move_penalty = 10

        # Create the starting pieces for each player
        for i, player in enumerate(players):
            # print player
            board.home_nodes[i].contents.set_owner(player)
            for neighbor in board.home_nodes[i].dirs.values():
                new_id = "{}{}".format(player.id, len(player.pieces))
                p = Piece(player, new_id, 1, neighbor)

    def spawn_time(x):
        return sum([i*6 for i in range(x)])/2 + x + 5 

    def next_move(self):
        moves = self.moves[self.turn]
        moves.update(player1.moves[self.turn])
        moves.update(player2.moves[self.turn])
        
        for p, order in moves.iteritems():
            if order[0] == "move":
                if p.can_move_to(order[1]):
                    p.move_to(order[1])
                else:
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "spawn":
                if p.can_move_to(order[1]):
                    p.cooldown = self.spawn_time(p.range)
                    # only one piece can be created per player per turn
                    self.moves[self.turn+p.cooldown][p.owner] = ("new_piece", order[1])
                else:
                    p.cooldown += self.illegal_move_penalty
            elif order[0] == "new_piece":
                new_id = p.get_next_id
                Piece(p, new_id, 1, order[1])

        for order, loc in moves.values:
            if len(loc.contents) > 1:
                self.resolve(loc)

    def resolve(loc):
        pass



b = Board(40, 40)
g = Game(b, [Player("A", set()), Player("B", set())])
print b