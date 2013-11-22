import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from game_api import GameApi

# todo : assign connection to a player

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print 'new connection'
		self.api = GameApi(self.write_message)
		self.player = self.api.game.players[0]
		self.opponent = self.api.game.opponent(self.player)
		self.write_message(self.api.game.gui_output())
	
	def on_message(self, message):
		print 'message received %s' % message
		return_statement = self.api.parse_input(message, self.player)
		# if type(return_statement) == None:
		self.api.make_opponent_moves(self.player)
		self.api.next_move()
		self.write_message(self.api.game.gui_output())
		# else:
		# 	self.write_message(return_statement)


	def on_close(self):
		print 'connection closed'


application = tornado.web.Application([(r'/ws', WSHandler),])

if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8000)
	tornado.ioloop.IOLoop.instance().start()