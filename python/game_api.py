from game import Game

class GameApi(object):
	def __init__(self, msgfunc):
		self.send = msgfunc

	def repl(self, x):
		try:
			exec x
		except Exception as e:
			self.send("Error caught: %s" % e.message)

	def new_game(self, *args):
		self.game = Game(*args)