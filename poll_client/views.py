import tornado.gen
import tornado.web
import tornadoredis

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
