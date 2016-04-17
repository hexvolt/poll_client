import tornado.web


class PollUIModule(tornado.web.UIModule):

    template = 'modules/poll.html'

    def render(self, poll=None):

        return self.render_string(self.template, poll=poll)
