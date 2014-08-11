import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from game_api import GameApi

# todo : assign connection to a player

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		pass # do nothing, I think
	
	def on_message(self, message):
		pass # it on to django's WSIG

	def on_close(self):
		pass # a message to let django know


application = tornado.web.Application([(r'/ws', WSHandler),])

if __name__ == "__main__":
	# connect to django's WSIG
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8000) # ?
	tornado.ioloop.IOLoop.instance().start()

