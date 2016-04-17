import tornado.gen
import tornado.web
import tornado.websocket
import tornadoredis

import settings
from poll_client.services import fetch_polls


class MainHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        redis_client = tornadoredis.Client()

        # getting latest changes from Redis
        poll_changes = yield tornado.gen.Task(
            redis_client.lrange, 'poll:log', 0, -1
        )

        # fetching all polls as initial data for displaying
        polls = yield tornado.gen.Task(fetch_polls)

        self.render('index.html', polls=polls, poll_changes=poll_changes)


class SubscribePollChangesHandler(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super(SubscribePollChangesHandler, self).__init__(*args, **kwargs)

        self.redis_channel = settings.REDIS_PUBSUB_CHANNEL

        self.redis_sub_client = tornadoredis.Client()

        self.subscribe_redis_channel()

    @tornado.gen.coroutine
    def subscribe_redis_channel(self):

        self.redis_sub_client.connect()

        yield tornado.gen.Task(
            self.redis_sub_client.subscribe, self.redis_channel
        )

        self.redis_sub_client.listen(self.on_redis_message)

    def on_redis_message(self, message):
        if message.kind == 'message':
            self.write_message(str(message.body))

        if message.kind == 'disconnect':
            # closing the WebSocket connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        """
        On WebSocket close handler
        """
        if self.redis_sub_client.subscribed:
            self.redis_sub_client.unsubscribe(self.redis_channel)
            self.redis_sub_client.disconnect()
