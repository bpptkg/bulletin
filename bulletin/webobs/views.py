from rest_framework.response import Response
from bulletin.api.base import Endpoint


class WebObsEndpoint(Endpoint):

    def get(self, request):
        return Response('Hello WebObs!')

