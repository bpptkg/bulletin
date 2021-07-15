from rest_framework.response import Response

from ..base import Endpoint

API_V1 = {
    'version': '1',
    'name': 'bulletin-api-v1',
}


class APIv1Endpoint(Endpoint):
    def get(self, request):
        return Response(API_V1)
