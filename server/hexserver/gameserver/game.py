from 


def load_game(filename, go_to_turn=False):
	with open(filename, 'rb') as f:
		board, players, moves, turn = cPickle.load(filename)
	for player in players:
		player.pieces = gl.PeekSet()
	game = Game(board, players, moves)
	if go_to_turn:
		for i in xrange(turn):
			game.next_move()
	return game


def test_game():
	b = gl.Board(40, 40)
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
	b = gl.Board(20, 20)
	g = Game(b, [gl.Player("A", gl.PeekSet()), gl.Player("B", gl.PeekSet())])
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
	b = gl.Board(20, 20)
	g = Game(b, [gl.Player("A", gl.PeekSet()), gl.Player("B", gl.PeekSet())])
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