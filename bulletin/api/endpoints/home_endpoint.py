from rest_framework.response import Response

from ..base import Endpoint

HOME = {
    'name': 'bulletin',
    'description': 'WebObs to seismic bulletin web services.',
    'url': 'https://gitlab.com/bpptkg/bulletin',
    'organization': 'BPPTKG',
    'original_author': 'Indra Rudianto',
}


class HomeEndpoint(Endpoint):
    def get(self, request):
        return Response(HOME)
