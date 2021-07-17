import pytz
from bulletin.api.base import Endpoint
from django.utils import dateparse, timezone
from rest_framework.response import Response
from wo.actions import SUPPORTED_WEBOBS_ACTION_NAMES, WebObsAction

from . import exceptions, tasks


def get_action(name):
    if name == WebObsAction.WEBOBS_UPDATE_EVENT.name:
        return (
            WebObsAction.WEBOBS_UPDATE_EVENT.name,
            WebObsAction.WEBOBS_UPDATE_EVENT.value,
        )
    elif name == WebObsAction.WEBOBS_HIDE_EVENT.name:
        return (
            WebObsAction.WEBOBS_HIDE_EVENT.name,
            WebObsAction.WEBOBS_HIDE_EVENT.value,
        )
    elif name == WebObsAction.WEBOBS_RESTORE_EVENT.name:
        return (
            WebObsAction.WEBOBS_RESTORE_EVENT.name,
            WebObsAction.WEBOBS_RESTORE_EVENT.value,
        )
    elif name == WebObsAction.WEBOBS_DELETE_EVENT.name:
        return (
            WebObsAction.WEBOBS_DELETE_EVENT.name,
            WebObsAction.WEBOBS_DELETE_EVENT.value,
        )
    return (None, None)


class WebObsEndpoint(Endpoint):

    def post(self, request):
        response = {}

        action = request.POST.get('action')
        if action is None:
            raise exceptions.MissingParameter('Missing action parameter.')

        if action not in SUPPORTED_WEBOBS_ACTION_NAMES:
            raise exceptions.InvalidParameter(
                'Unsupported action name: {}'.format(action))

        eventdate_str = request.POST.get('eventdate')
        eventid = request.POST.get('eventid')
        sc3id = request.POST.get('sc3id')
        operator = request.POST.get('operator')
        eventtype = request.POST.get('eventtype')

        if action == WebObsAction.WEBOBS_UPDATE_EVENT.name:
            try:
                eventdate = dateparse.parse_datetime(eventdate_str)
            except ValueError as e:
                raise exceptions.InvalidParameter(
                    'Invalid eventdate value: {}'.format(eventdate_str))

            if eventdate is None:
                raise exceptions.MissingParameter(
                    'Missing eventdate parameter.')

            if eventdate.tzinfo is not None:
                eventdate = eventdate.replace(tzinfo=pytz.utc)
            else:
                eventdate = pytz.utc.localize(eventdate)

            tasks.update_event.apply_async(
                args=(eventdate, ),
                kwargs={
                    'eventid': eventid,
                    'sc3id': sc3id,
                    'operator': operator,
                    'eventtype': eventtype,
                },
                serializer='pickle',
            )

        elif action == WebObsAction.WEBOBS_HIDE_EVENT.name:
            if eventid is None:
                raise exceptions.MissingParameter('Missing eventid parameter.')

            tasks.hide_event.apply_async(
                args=(eventid, ),
                kwargs={'operator': operator},
                serializer='pickle',
            )

        elif action == WebObsAction.WEBOBS_RESTORE_EVENT.name:
            if eventid is None:
                raise exceptions.MissingParameter('Missing eventid parameter.')

            if eventtype is None:
                raise exceptions.MissingParameter(
                    'Missing eventtype parameter.')

            tasks.restore_event.apply_async(
                args=(eventid, eventtype),
                kwargs={'operator': operator},
                serializer='pickle',
            )

        elif action == WebObsAction.WEBOBS_DELETE_EVENT.name:
            if eventid is None:
                raise exceptions.MissingParameter('Missing eventid parameter.')

            tasks.delete_event.apply_async(
                args=(eventid, ),
                kwargs={'operator': operator},
                serializer='pickle',
            )

        response['status'] = 'submitted'
        response['timestamp'] = timezone.now()
        action_name, action_id = get_action(action)
        response['action'] = {
            'id': action_id,
            'name': action_name,
        }

        return Response(response)
