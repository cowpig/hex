from game import Game

class GameApi(object):
	def __init__(self, msgfunc):
		self.send = msgfunc

	def repl(self, x):
		exec x

	def new_game(self, *args):
		self.game = Game(*args)