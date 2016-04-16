import os

import poll_client.uimodules

# RabbitMQ consumer settings
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', 5672)
RABBITMQ_USERNAME = os.environ.get('RABBITMQ_USERNAME', 'guest')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_APP_EXCHANGE = 'poll'

# Poll Server location settings
POLL_SERVER_URL = os.environ.get('POLL_SERVER_URL', 'http://0.0.0.0:8000')

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': 0
        },
        'consumer': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': 0
        }
    }
}

# Tornado app settings
APP_SETTINGS = {
    'static_path': 'static/',
    'template_path': 'templates/',
    'ui_modules': poll_client.uimodules,
}
