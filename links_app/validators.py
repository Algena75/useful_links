import operator
import re
from http import HTTPStatus

from flask import flash

from .error_handlers import InvalidAPIUsage
from .models import Link
from .utils import ARRAY, LANG_CHOICES, get_unique_short_id


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


def validate_link(data):
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'original_url' not in data:
        raise InvalidAPIUsage('\"original_url\" является обязательным полем!')
    data['original_url'] = validate_url(data['original_url'])
    if Link.query.filter_by(original=data['original_url']).first():
        raise InvalidAPIUsage('Такая ссылка уже есть!')
    if 'description' not in data:
        raise InvalidAPIUsage('\"description\" является обязательным полем!')
    if Link.query.filter_by(text=data['description']).first():
        raise InvalidAPIUsage('Такое описание уже есть!')
    if data.get('language'):
        if data.get('language') not in list(operator.concat(*LANG_CHOICES)):
            raise InvalidAPIUsage(
                f'Язык должен быть из списка {LANG_CHOICES}'
            )
    else:
        data['language'] = 'RU'
    if data.get('short_link'):
        short_id = validate_custom_id(data.get('short_link'))
        if Link.query.filter_by(short=short_id).first() is not None:
            raise InvalidAPIUsage(f'Имя "{short_id}" уже занято.')
    else:
        data['short_link'] = get_unique_short_id()
    return data


def validate_search_string(search_string):
    if not search_string or search_string.strip() == '':
        raise InvalidAPIUsage('Строка поиска не может быть пустой')
    return search_string


def validate_form(form):
    wrong = False
    if Link.query.filter_by(original=form.original_link.data).first():
        flash('Такая ссылка уже есть!')
        wrong = True
    if Link.query.filter_by(text=form.link_description.data).first():
        flash('Такое описание уже есть!')
        wrong = True
    if form.custom_id.data and form.custom_id.data.strip() != '':
        short_url = form.custom_id.data
        if Link.query.filter_by(short=short_url).first() is not None:
            flash(f'Имя {short_url} уже занято!')
            wrong = True
    else:
        form.custom_id.data = get_unique_short_id()
    return form, wrong
