POLL CLIENT
===========

This is a client application for the test POLL SERVER app that consumes
messages about models changes from the server through the RabbitMQ and
visualises it for the user.


Setting up and Installation
---------------------------

* **Set up you local environment**


    git clone git@bitbucket.org:hexvolt/poll_client.git

It is recommended to use Python 3.3+, so if you don't have it yet, install
Python first and create its virtual environment in your virtualenv folder:


    pyvenv-3.5 <env_name>
    cd <env_name>
    source bin/activate

Install the requirements needed for the project:


    cd <project_dir>
    pip install -r requirements.txt

Set your POLL_SERVER_URL in your OS environment variables or in settings.py


* **Set up the connection with RabbitMQ server**

Write down the parameters of your RabbitMQ server into your environment
variables or to the setting.py file (see RABBITMQ_USER, RABBITMQ_PASSWORD, etc)

* **Set up and run Redis**

Follow [Redis installation instructions](http://redis.io/download#installation)

Run the Redis server:


    src/redis-server

Note: the Redis server should be running when starting the project in order
to be able to save messages consumed from RabbitMQ

* **Run the project**


    make run

Locally the default URL of index page is [http://0.0.0.0:8888/](http://0.0.0.0:8888/)


