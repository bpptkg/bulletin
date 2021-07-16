import json
import os

import bottle
from bottle import get, request, response

app = application = bottle.default_app()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@get('/cgi-bin/mc3.pl')
def request_mc3():
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Cache-Control'] = 'no-cache'
    content_disposition = 'attachment; filename="MC3_dump_bulletin.csv"'
    response.headers['Content-Disposition'] = content_disposition

    with open(os.path.join(BASE_DIR, 'MC3_dump_bulletin.csv'), 'rb') as fd:
        content = fd.read()

    return content


@get('/')
def home():
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'
    return json.dumps({
        'name': 'WebObs MC3 mock web services',
        'organization': 'BPPTKG',
        'original_author': 'Indra Rudianto',
    })


def main():
    bottle.run(host='127.0.0.1', port=6351)


if __name__ == '__main__':
    main()
