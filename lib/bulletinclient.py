"""
Bulletin web services Python client.
"""

from __future__ import print_function

import argparse
import os
import sys
import json

import requests

USER_HOME = os.path.expanduser('~')
WORK_DIR = os.path.join(USER_HOME, '.bulletin')
if not os.path.isdir(WORK_DIR):
    os.makedirs(WORK_DIR)

VERSION = '0.1.0'


class WebObsAction:
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


def parse_args():
    parser = argparse.ArgumentParser(
        description='Bulletin web services Python client. '
                    '(Version {version})'.format(version=VERSION))

    default_url = 'http://192.168.0.43:6352/api/v1/webobs/'
    parser.add_argument(
        '-u', '--url',
        default=default_url,
        help='Bulletin WebObs endpoint URL. '
             'Default to {url}.'.format(url=default_url))

    parser.add_argument(
        'action',
        help='WebObs action name. Valid names are WEBOBS_HIDE_EVENT, '
             'WEBOBS_UPDATE_EVENT, and WEBOBS_DELETE_EVENT.')

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

    print('Request body:', data)
    response = requests.post(args.url, data)

    print('Response:', json.loads(response.text))
    if response.status_code == 200:
        print('Action submitted.')
    else:
        print('Action failed to be submitted.')


if __name__ == '__main__':
    main()
