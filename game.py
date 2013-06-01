from game_library import *


class Game:
    def __init__(self, board, players):
        self.board = board
        # list of players, currently only supporting two
        self.players = players
        self.turn = 0
        self.moves = []

        # Create the starting pieces for each player
        for i, player in enumerate(players):
            print player
            board.home_nodes[i].contents.set_owner(player)
            for neighbor in board.home_nodes[i].dirs.values():
                new_id = "{}{}".format(player.id, len(player.pieces))
                p = Piece(player, new_id, 1, neighbor)

    def next_move(self):
        moves = self.moves[turn]
        moves.update(player1.moves[turn])
        moves.update(player2.moves[turn])


b = Board(40, 40)
g = Game(b, [Player("A"), Player("B")])
print b