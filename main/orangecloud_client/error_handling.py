import logging

_logger = logging.getLogger(__name__)


class ClientError(Exception):
    def __init__(self, response, msg):
        super(ClientError, self).__init__(msg)
        self.response = response


def raise_response_error(response, domain, msg, *args):
    _logger.error('%s - error in response: \n%s', domain, response.text)
    raise ClientError(response, ('%s: %s' % (domain, msg)) % args)
