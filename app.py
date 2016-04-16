import logging.config
import sys

import tornado.ioloop
import tornado.web

import settings

from poll_client import views
from consumer.poll_consumer import PollUpdatesConsumer


def make_app():
    return tornado.web.Application([
        (r"/", views.MainHandler),
        (r"/subscribe", views.SubscribePollChangesHandler),
    ], **settings.APP_SETTINGS)

if __name__ == "__main__":
    arg = sys.argv[1] if sys.argv[1:] else 'localhost:8000'
    ip, port = arg.split(':')

    logging.config.dictConfig(settings.LOGGING)

    poll_consumer = PollUpdatesConsumer()
    poll_consumer.connect(
        exchange_name=settings.RABBITMQ_APP_EXCHANGE,
        exchange_type='fanout',
        exclusive=True,
        no_ack=True
    )

    app = make_app()
    app.listen(address=ip, port=port)

    tornado.ioloop.IOLoop.current().start()
