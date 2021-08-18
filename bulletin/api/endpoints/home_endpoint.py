from rest_framework.response import Response

from ..base import Endpoint

HOME = {
    'name': 'bulletin',
    'description': 'Bulletin Web Services',
    'url': 'https://github.com/bpptkg/bulletin',
    'organization': 'BPPTKG',
    'author': 'BPPTKG',
    'copyright': 'Copyright (c) 2021-present BPPTKG',
}


class HomeEndpoint(Endpoint):
    def get(self, request):
        return Response(HOME)
