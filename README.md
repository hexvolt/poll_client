POLL CLIENT
===========

This is a client application for the test POLL SERVER app that consumes
messages about models changes from the server through the RabbitMQ.


Setting up and Installation
---------------------------

* Clone the project


    git clone git@bitbucket.org:hexvolt/poll_client.git

* Set up RabbitMQ credentials

Write down the parameters of your RabbitMQ server into your environment
variables or to the setting.py file (see RABBITMQ_USER, RABBITMQ_PASSWORD, etc)

* Set up and run Redis

Follow [installation instructions](http://redis.io/download#installation)

Run:

    src/redis-server
