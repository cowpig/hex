from game import Game

class GameApi(object):
	def __init__(self, msgfunc):
		self.send = msgfunc
		self.game = Game()

	def repl(self, msg):
		try:
			exec msg
		except Exception as e:
			print e.message
			self.send("Error caught: %s" % e.message)
			
		self.send(self.game.gui_output())

	def new_game(self, *args):
		self.game = Game(*args)

	# parses a move input string
	def parse_input(self, input, player_id):
		order_strings = input.split("\n")
		moves = {}
		player = self.game.get_player(player_id)

		for order_string in order_strings:
			try:
				piece_id, the_rest = order_string.split(".")
				order, dest_str = the_rest.split(" ")

				piece = player[piece_id]

				# we will allow destinations to be given in one of two ways
				#	E-E-SE, for destinations relative to the node
				#	(x,y) for absolute destinations
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
				return e

