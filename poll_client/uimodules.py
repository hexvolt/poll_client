import tornado.web


class Poll(tornado.web.UIModule):

    def render(self, poll):

        return self.render_string('modules/poll.html', poll=poll)
