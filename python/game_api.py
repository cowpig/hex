from game import Game

class GameApi(object):
	def __init__(self, msgfunc):
		self.send = msgfunc
		self.game = Game()

	def repl(self, msg):
		try:
			exec msg
		except Exception as e:
			self.send("Error caught: %s" % e.message)
			
		self.send(self.game.gui_output())

	def new_game(self, *args):
		self.game = Game(*args)