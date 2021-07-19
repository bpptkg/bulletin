"""
Bulletin web services Python client.
"""

from __future__ import print_function

import argparse
import datetime
import json
import os
import re
import sys
import uuid

import requests

__version__ = '0.1.0'
__author__ = 'Indra Rudianto'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2021-present BPPTKG'

USER_HOME = os.path.expanduser('~')
BULLETIN_DIR = os.path.join(USER_HOME, '.bulletin')
if not os.path.isdir(BULLETIN_DIR):
    os.makedirs(BULLETIN_DIR)

FAILED_REQUEST_DIR = os.path.join(BULLETIN_DIR, 'failedrequest')
if not os.path.isdir(FAILED_REQUEST_DIR):
    os.makedirs(FAILED_REQUEST_DIR)

DEFAULT_URL = 'http://192.168.0.43:9056/api/v1/webobs/'

datetime_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)


def get_fixed_timezone(offset):
    """Return a tzinfo instance with a fixed offset from UTC."""
    if isinstance(offset, timedelta):
        offset = offset.total_seconds() // 60
    sign = '-' if offset < 0 else '+'
    hhmm = '%02d%02d' % divmod(abs(offset), 60)
    name = sign + hhmm
    return datetime.timezone(datetime.timedelta(minutes=offset), name)


def parse_datetime(value):
    """
    Parse a string and return a datetime.datetime

    Raise ValueError if the input is well formatted but not a valid datetime.
    Return None if the input isn't well formatted.
    """
    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        kw['microsecond'] = kw['microsecond'] and kw['microsecond'].ljust(
            6, '0')
        tzinfo = kw.pop('tzinfo')
        if tzinfo == 'Z':
            tzinfo = utc
        elif tzinfo is not None:
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == '-':
                offset = -offset
            tzinfo = get_fixed_timezone(offset)
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        kw['tzinfo'] = tzinfo
        return datetime.datetime(**kw)


def is_valid_datetime(value):
    """
    Check if value is a valid datetime string.
    """
    try:
        dateobj = parse_datetime(value)
        if dateobj is None:
            return False
        return True
    except ValueError:
        return False


class WebObsAction(object):
    """
    Enum constants of supported WebObs actions.
    """
    WEBOBS_UPDATE_EVENT = 'WEBOBS_UPDATE_EVENT'
    WEBOBS_HIDE_EVENT = 'WEBOBS_HIDE_EVENT'
    WEBOBS_RESTORE_EVENT = 'WEBOBS_RESTORE_EVENT'
    WEBOBS_DELETE_EVENT = 'WEBOBS_DELETE_EVENT'

    ALL = [
        WEBOBS_UPDATE_EVENT,
        WEBOBS_HIDE_EVENT,
        WEBOBS_RESTORE_EVENT,
        WEBOBS_DELETE_EVENT,
    ]


class FailedRequestStorage(object):
    """
    A class representing failed request storage.
    """

    def __init__(self, storagedir=None):
        if storagedir is not None:
            self.storagedir = storagedir
        else:
            self.storagedir = FAILED_REQUEST_DIR

    def store(self, data, *, gid=None, response=None, exc=None):
        """
        Store data to the storage directory.

        Every data stored will be given global unique identifier (gid),
        basically using uuid4. You can also pass custom gid value in the keyword
        argument.

        Error message (errmsg) can also be passed to know why the request
        failed.
        """
        if gid is None:
            uid = uuid.uuid4().hex
        else:
            uid = gid

        path = os.path.join(self.storagedir, '{}.json'.format(uid))
        content = {
            'gid': uid,
            'data': data,
            'action': data['action'],
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'argv': sys.argv,
            'userid': os.getuid(),
            'exc': exc,
            'response': None,
        }

        if response is not None:
            content['response'] = {
                'headers': dict(response.headers),
                'links': response.links,
                'ok': response.ok,
                'reason': response.reason,
                'status_code': response.status_code,
                'text': response.text,
                'url': response.url,
            }

        with open(path, 'w') as fd:
            json.dump(content, fd, indent=4, sort_keys=True)

        return path

    def load(self, gid):
        """
        Load failed request file using gid index.
        """
        if gid is None:
            raise ValueError('gid could not be None.')
        path = os.path.join(self.storagedir, '{}.json'.format(gid))
        if not os.path.isfile(path):
            raise FileNotFoundError('File {} could not be found.'.format(path))

        with open(path, 'r') as fd:
            content = json.load(fd)
        return content


def parse_args():
    parser = argparse.ArgumentParser(
        description='Bulletin web services Python client. '
                    '(Version {version})'.format(version=__version__))

    parser.add_argument(
        '-u', '--url',
        default=DEFAULT_URL,
        help='Bulletin WebObs endpoint URL. '
             'Default to {url}.'.format(url=DEFAULT_URL))

    parser.add_argument(
        'action',
        choices=WebObsAction.ALL,
        help='WebObs action name.')

    parser.add_argument(
        '--eventid',
        help='Event ID (eventid), e.g. 2021-07#3330. '
             'For WEBOBS_HIDE_EVENT, WEBOBS_RESTORE_EVENT, '
             'and WEBOBS_DELETE_EVENT, eventid is required.')

    parser.add_argument(
        '--eventdate',
        help="Event date in UTC time zone. "
             "For WEBOBS_UPDATE_EVENT, eventdate value is required.")

    parser.add_argument(
        '--sc3id',
        help='SeisComP3 ID, e.g. ://bpptkg2021nhcvwk. '
             'For WEBOBS_UPDATE_EVENT, specifying the value is recommended.')

    parser.add_argument(
        '--eventtype',
        help='Event type, e.g. VTA, VTB. '
             'For WEBOBS_UPDATE_EVENT, specifying the value is recommended. '
             'For WEBOBS_RESTORE_EVENT, eventtype value is required.')

    parser.add_argument(
        '--operator',
        help='Operator name that modify the event. e.g. YUL.')

    return parser.parse_args()


def validate_arguments(args):
    if args.action not in WebObsAction.ALL:
        print("Error: Unrecognize action name: '{}'. "
              "Supported action names are {}."
              "".format(args.action, WebObsAction.ALL),
              file=sys.stderr)
        sys.exit(1)

    missing_eventid_msg = (
        'Error: {action_name} action requires event ID (eventid) '
        'to be set. You set the value by adding --eventid in the '
        'script arguments.')

    missing_eventtype_msg = (
        'Error: {action_name} action requires eventtype to be set. '
        'You set the value by adding --eventtype in the '
        'script arguments.')

    missing_eventdate_msg = (
        'Error: {action_name} action requires eventdate to be set. '
        'You can set the value by adding --eventdate '
        'in the script arguments.'
    )

    action = args.action

    if action == WebObsAction.WEBOBS_UPDATE_EVENT:
        if args.eventdate is None:
            print(missing_eventdate_msg.format(action_name=action),
                  file=sys.stderr)
            sys.exit(1)

        if not is_valid_datetime(args.eventdate):
            print('Error: Invalid eventdate value: {}'.format(args.eventdate),
                  file=sys.stderr)
            sys.exit(1)

    elif action == WebObsAction.WEBOBS_HIDE_EVENT:
        if args.eventid is None:
            print(missing_eventid_msg.format(action_name=action),
                  file=sys.stderr)
            sys.exit(1)

    elif action == WebObsAction.WEBOBS_RESTORE_EVENT:
        if args.eventid is None:
            print(missing_eventid_msg.format(action_name=action),
                  file=sys.stderr)
            sys.exit(1)

        if args.eventtype is None:
            print(missing_eventtype_msg.format(action_name=action),
                  file=sys.stderr)
            sys.exit(1)

    elif action == WebObsAction.WEBOBS_DELETE_EVENT:
        if args.eventid is None:
            print(missing_eventid_msg.format(action_name=action),
                  file=sys.stderr)
            sys.exit(1)


def main():
    args = parse_args()
    validate_arguments(args)

    if args.action == WebObsAction.WEBOBS_UPDATE_EVENT:
        data = {
            'action': args.action,
            'eventdate': args.eventdate,
            'eventid': args.eventid,
            'sc3id': args.sc3id,
            'eventtype': args.eventtype,
            'operator': args.operator,
        }

    elif args.action == WebObsAction.WEBOBS_HIDE_EVENT:
        data = {
            'action': args.action,
            'eventid': args.eventid,
            'operator': args.operator,
        }

    elif args.action == WebObsAction.WEBOBS_RESTORE_EVENT:
        data = {
            'action': args.action,
            'eventid': args.eventid,
            'eventtype': args.eventtype,
            'operator': args.operator,
        }

    elif args.action == WebObsAction.WEBOBS_DELETE_EVENT:
        data = {
            'action': args.action,
            'eventid': args.eventid,
            'operator': args.operator,
        }

    frstorage = FailedRequestStorage()
    print('Request body:', data)

    try:
        response = requests.post(args.url, data)
        if response.ok:
            print('Response: {}'.format(response.json()))
            print('Action submitted.')
        else:
            print('Action failed to be submitted.')
            print('Response: {}'.format(response.text))

            path = frstorage.store(data, response=response)
            print('Failed request data is stored in {}'.format(path))
    except requests.exceptions.RequestException as err:
        print(err)
        print('Action failed to be submitted.')

        path = frstorage.store(data, exc=str(err))
        print('Failed request data is stored in {}'.format(path))


if __name__ == '__main__':
    main()
