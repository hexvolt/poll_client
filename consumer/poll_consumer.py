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
        """
        Callback the fires each time the Rabbit queue gets the new message
        from the server.

        """
        super(PollUpdatesConsumer, self).on_message(channel, basic_deliver,
                                                    properties, body)
        message = body.decode('utf-8')

        self.publish_message(message)

    @tornado.gen.coroutine
    def publish_message(self, message):
        """
        Publishes the Poll-message to the Redis pub/sub channel.

        :param str message: a string with JSON-encoded message received from
                            RabbitMQ with information about Polls changes

        """
        redis_pub_client = tornadoredis.Client()

        yield tornado.gen.Task(
            redis_pub_client.publish, settings.REDIS_PUBSUB_CHANNEL, message
        )
