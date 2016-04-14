import sys

import tornado.ioloop
import tornado.web

from poll_client import views


def make_app():
    return tornado.web.Application([
        (r"/", views.MainHandler),
    ])

if __name__ == "__main__":
    arg = sys.argv[1:]
    ip, port = arg.split(':') if arg else 'localhost', '8000'

    app = make_app()
    app.listen(port, address=ip)

    tornado.ioloop.IOLoop.current().start()
