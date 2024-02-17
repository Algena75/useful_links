import re
from http import HTTPStatus

from .error_handlers import InvalidAPIUsage
from .utils import ARRAY


def validate_hostname(hostname):
    """
    Helper class for checking hostnames for validation.

    This is not a validator in and of itself, and as such is not exported.
    """

    hostname_part = re.compile(r"^(xn-|[a-z0-9_]+)(-[a-z0-9_-]+)*$", re.IGNORECASE)

    # Encode out IDNA hostnames. This makes further validation easier.
    try:
        hostname = hostname.encode("idna")
    except UnicodeError:
        pass
    # Turn back into a string in Python 3x
    if not isinstance(hostname, str):
        hostname = hostname.decode("ascii")
    if len(hostname) > 253:
        return False

    # Check that all labels in the hostname are valid
    parts = hostname.split(".")
    for part in parts:
        if not part or len(part) > 63:
            return False
        if not hostname_part.match(part):
            return False
    return True


def validate_url(url):
    regex = (
        r"^[a-z]+://"
        r"(?P<host>[^\/\?:]+)"
        r"(?P<port>:[0-9]+)?"
        r"(?P<path>\/.*?)?"
        r"(?P<query>\?.*)?$"
    )
    match = re.search(regex, url)
    if match is None or not validate_hostname(match.group("host")):
        raise InvalidAPIUsage("Неправильный URL")
    return url


def validate_custom_id(short_id):
    short_id.strip()
    if len(short_id) > 16:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки',
            status_code=HTTPStatus.BAD_REQUEST
        )
    for letter in short_id:
        if letter not in ARRAY:
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки',
                status_code=HTTPStatus.BAD_REQUEST
            )
    return short_id
