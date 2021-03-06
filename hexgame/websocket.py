import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from demo import DemoAPI

# todo : assign connection to a player

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        self.api = DemoAPI(self.write_message)
        print self.api.game.board
    
    def on_message(self, message):
        print 'message received %s' % message
        return_statement = self.api.parse_input(message)
        self.write_message(return_statement)

    def on_close(self):
        print 'connection closed'


application = tornado.web.Application([(r'/ws', WSHandler),])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()