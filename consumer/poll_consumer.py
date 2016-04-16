import json

import tornado.gen
import tornadoredis

from consumer.base_consumer import BaseConsumerRabbitMQClient
import settings


class PollUpdatesConsumer(BaseConsumerRabbitMQClient):

    def __init__(self):

        super(PollUpdatesConsumer, self).__init__(
            username=settings.RABBITMQ_USERNAME,
            password=settings.RABBITMQ_PASSWORD,
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
        )

    def on_message(self, channel, basic_deliver, properties, body):
        super(PollUpdatesConsumer, self).on_message(channel, basic_deliver,
                                                    properties, body)
        message = json.loads(body.decode('utf-8'))

        self.save_message(message)

    @tornado.gen.coroutine
    def save_message(self, message):
        """
        Saves the Poll-message to the Redis storage.

        :param dict message: a parsed message received from RabbitMQ with
                             information about Poll-server's database changes
                             {
                                 'model': '...',
                                 'action': '...',
                                 'instance': {...}
                             }
        """
        redis_client = tornadoredis.Client()

        yield tornado.gen.Task(
            redis_client.lpush, 'poll:log', json.dumps(message)
        )
