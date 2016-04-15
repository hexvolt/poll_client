import logging

from pika import TornadoConnection, ConnectionParameters, PlainCredentials

logger = logging.getLogger(__name__)


class BaseConsumerRabbitMQClient(object):
    """
    A base class for asynchronous interaction with Rabbit MQ. It implements
    the basic logic of methods and callback functions needed for consuming
    messages from Rabbit MQ in async mode and links them with each other.
    In that way the child classes may overwrite only those event handlers
    or methods that need nonstandard implementation for a certain application.

    Partially based on examples given in pika's library documentation.
    """

    def __init__(self, username, password, host, port, io_loop=None):

        credentials = PlainCredentials(username=username, password=password)

        self._connection_parameters = ConnectionParameters(
            host=host, port=port, credentials=credentials
        )

        self._exchange_name = None
        self._exchange_type = None
        self._queue_name = None
        self._routing_key = None
        self._exclusive = False
        self._io_loop = io_loop
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._no_ack = False

    def connect(self, exchange_name, exchange_type, queue_name=None,
                routing_key=None, exclusive=False, no_ack=False):
        """
        This method connects to RabbitMQ and sets the connection properties.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :param exchange_name: a name of RabbitMQ's Exchange
        :param exchange_type: a type of RabbitMQ's Exchange
        :param queue_name: a name of the queue you want to connect to or None
                           if you want let the server assign the name
        :param routing_key: a routing key for bindind exchange and queue
        :param exclusive: if True, a queue will be deleted after disconnecting.
                          Usually applicable with dynamic name queues.
        :param no_ack: if True, communication with RabbitMQ will be performed
                       without ACK messages.
        """
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type
        self._queue_name = queue_name or ''
        self._routing_key = routing_key
        self._exclusive = exclusive
        self._no_ack = no_ack

        logger.info('Connecting to Rabbit MQ server')
        self._connection = TornadoConnection(
            parameters=self._connection_parameters,
            on_open_callback=self.on_connection_open,
            on_close_callback=self.on_connection_close,
            custom_ioloop=self._io_loop
        )

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        logger.info('Closing connection')
        self._connection.close()

    def on_connection_close(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds:(%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_open(self, connection):
        """
        This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object.

        :type connection: pika.SelectConnection

        """
        logger.info('Connection opened')

        self.open_channel()

    def reconnect(self):
        """
        Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        if not self._closing:
            # Create a new connection
            self.connect(
                self._exchange_name, self._exchange_type, self._queue_name,
                self._routing_key, self._exclusive, self._no_ack
            )

    def on_channel_close(self, channel, reply_code, reply_text):
        """
        Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        logger.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        """
        This method is invoked by pika when the channel has been opened.

        :param pika.channel.Channel channel: The channel object

        """
        logger.info('Channel opened')
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_close)

        # since the channel is now open, we are declaring the exchange to use.
        self.setup_exchange(self._exchange_name)

    def setup_exchange(self, exchange_name):
        """
        Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declare_ok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        logger.info('Declaring exchange `%s`', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declare_ok,
                                       exchange_name,
                                       self._exchange_type)

    def on_exchange_declare_ok(self, frame):
        """
        Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method frame: Exchange.DeclareOk response frame

        """
        logger.info('Exchange declared')
        self.setup_queue(self._queue_name)

    def setup_queue(self, queue_name):
        """
        Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declare_ok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        logger.info('Declaring queue `%s`', queue_name)
        self._channel.queue_declare(
            self.on_queue_declare_ok, queue_name, exclusive=self._exclusive
        )

    def on_queue_declare_ok(self, method_frame):
        """
        Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we're binding the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bind_ok method
        will be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        if not self._queue_name:
            self._queue_name = method_frame.method.queue

            logger.info('A queue name `%s` has been assigned by server',
                        self._queue_name)

        logger.info('Binding exchange `%s` to queue `%s` with routing `%s`',
                    self._exchange_name, self._queue_name, self._routing_key)
        self._channel.queue_bind(self.on_bind_ok, self._queue_name,
                                 self._exchange_name, self._routing_key)

    def on_bind_ok(self, frame):
        """
        Invoked by pika when the Queue.Bind method has completed. At this
        point we're starting consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method frame: The Queue.BindOk response frame

        """
        logger.info('Queue bound')
        self.start_consuming()

    def on_consumer_cancelled(self, method_frame):
        """
        Callback that will be invoked if RabbitMQ for some reason cancels
        the consumer receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        logger.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, channel, basic_deliver, properties, body):
        """
        Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel channel: The channel object
        :param pika.Spec.Basic.Deliver basic_deliver: basic_deliver method
        :param pika.Spec.BasicProperties properties: properties
        :param str|unicode body: The message body

        """
        logger.info('Received message #%s: %s',
                    basic_deliver.delivery_tag, body)
        if not self._no_ack:
            self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """
        Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def on_cancel_ok(self, unused_frame):
        """
        This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def stop_consuming(self):
        """
        Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            logger.info('Stopping consuming')
            self._channel.basic_cancel(self.on_cancel_ok, self._consumer_tag)

    def start_consuming(self):
        """
        This method issues the Basic.Consume RPC command which returns
        the consumer tag that is used to uniquely identify the consumer
        with RabbitMQ. We keep the value to use it when we want to cancel
        consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        logger.info('Starting consuming')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self._queue_name,
                                                         no_ack=self._no_ack)

    def close_channel(self):
        """
        Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        logger.info('Closing the channel')
        self._channel.close()

    def open_channel(self):
        """
        Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)
