import logging

_logger = logging.getLogger(__name__)


class ClientError(Exception):
    pass


def raise_response_error(response, domain, msg, *args):
    _logger.error('%s - error in response: \n%s', domain, response.text)
    raise_error(domain, msg, *args)


def raise_error(domain, msg, *args):
    raise ClientError(('%s: %s' % (domain, msg)) % args)
