import tornado.gen
import tornado.web
import tornadoredis


class MainHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        redis_client = tornadoredis.Client()

        poll_changes = yield tornado.gen.Task(
            redis_client.lrange, 'poll:log', 0, 10
        )

        self.render('templates/index.html', poll_changes=poll_changes)
