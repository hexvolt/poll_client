import json
from urllib.parse import urljoin

import requests

import settings


def fetch_polls(callback=None):

    response = requests.get(urljoin(settings.POLL_SERVER_URL, 'questions'))

    polls = json.loads(response.content.decode('utf-8'))

    result = polls.get('results', [])

    return callback(result)
