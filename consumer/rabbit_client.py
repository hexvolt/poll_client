import settings

from consumer.base_consumer import BaseConsumerRabbitMQClient


class PollUpdatesConsumer(BaseConsumerRabbitMQClient):

    def __init__(self):

        super(PollUpdatesConsumer, self).__init__(
            username=settings.RABBITMQ_USERNAME,
            password=settings.RABBITMQ_PASSWORD,
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
        )
