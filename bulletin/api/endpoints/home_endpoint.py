from rest_framework.response import Response

from ..base import Endpoint

HOME = {
    'name': 'bulletin',
    'description': 'Bulletin Web Services',
    'url': 'https://gitlab.com/bpptkg/bulletin',
    'organization': 'BPPTKG',
    'original_author': 'Indra Rudianto',
    'copyright': 'Copyright (c) 2021-present BPPTKG',
}


class HomeEndpoint(Endpoint):
    def get(self, request):
        return Response(HOME)
