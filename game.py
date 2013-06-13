from game_library import *


class Game:
    def __init__(self, board, players):
        self.board = board
        # list of players, currently only supporting two
        self.players = players
        self.turn = 0
        self.spawn_times = []

        for i, player in enumerate(players):
            # Set the home nodes for each player
            board.home_nodes[i].contents.set_owner(player)
            # Create the starting pieces for each player
            for neighbor in board.home_nodes[i].dirs.values():
                new_id = "{}{}".format(player.id, len(player.pieces))
                p = Piece(player, new_id, 1, neighbor)

    def next_move(self):
        moves = {}
        moves.update(player1.moves[self.turn])
        moves.update(player2.moves[self.turn])





b = Board(40, 40)
g = Game(b, [Player("A", set()), Player("B", set())])
print b