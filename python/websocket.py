import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from game_api import GameApi

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        self.write_message("Hello World")
        self.api = GameApi(self.write_message)
      
    def on_message(self, message):
        print 'message received %s' % message
        self.api.repl(message)
 
    def on_close(self):
      print 'connection closed'


application = tornado.web.Application([
  (r'/ws', WSHandler),
])


if __name__ == "__main__":
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8000)
  tornado.ioloop.IOLoop.instance().start()