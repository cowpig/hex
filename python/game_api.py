from game import Game, make_nearly_random_moves
import io

class PlayerConnection(object):
	def __init__(self, infile, outfile, userID):
		self.infile = io.FileIO(infile, "wb")
		self.outfile = io.FileIO(outfile, "wb")
		self.userID = userID

class GameApi(object):
	def __init__(self, A_conn, B_conn):
		self.connections = {"A" : A_conn, "B" : B_conn}
		self.game = Game()

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
		turn = self.game.turn
		for player in self.game.players:
			instructions = self.connections[player.id].read()
			player.moves[turn] = parse_instructions(instructions)
		
		self.game.next_move()
		new_state = self.game.get_game_state()

		self.push_state(new_state)

		return new_state

	def push_state(self, gamestate):
		for player_id, conn in self.connections:
			conn.outfile.writeline(json.dumps({player_id : gamestate[player_id]}))

	# parses a move input string
	def parse_instructions(self, input_str):
		try:
			move_dict = json.loads(input_str)
			for piece_id, order_string in move_dict:
				order, dest_str = order_string.split(" ")
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
			msg = "Error parsing order string:\n\t{}".format(order_string)
			msg += "\nerror message:\n\t{}".format(e.message)
			return None
			# raise Exception(msg)
		
		return moves
