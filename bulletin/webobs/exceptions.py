from rest_framework.exceptions import APIException


class MissingParameter(APIException):
    status_code = 400
    default_detail = 'Missing parameter.'
    default_code = 'missing_parameter'


class InvalidParameter(APIException):
    status_code = 400
    default_detail = 'Parameter name is invalid.'
    default_code = 'invalid_parameter'
