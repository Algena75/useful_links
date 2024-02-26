import string
from random import choices
from sqlalchemy import func

from . import db
from .models import Link, Tag

ARRAY = string.ascii_letters + string.digits
LANG_CHOICES = [('RU', 'rus'), ('EN', 'eng')]


def get_unique_short_id(count_char=6):
    short_url = ''.join(choices(ARRAY, k=count_char))
    if Link.query.filter_by(short=short_url).first() is not None:
        get_unique_short_id()
    return short_url


def create_new_link(link, tags):
    tags = [tag.strip() for tag in tags.split(',')]
    for tag in tags:
        tag_in_db = db.session.query(Tag).filter(
            func.lower(Tag.name) == func.lower(tag)
        ).first()
        if tag_in_db:
            link.tags.append(tag_in_db)
        else:
            new_tag = Tag(name=tag)
            db.session.add(new_tag)
            db.session.flush()
            link.tags.append(new_tag)
    db.session.add(link)
    db.session.commit()
    return link


def change_tag_is_active(tag_name):
    tag_to_change = Tag.query.filter(
        func.lower(Tag.name) == func.lower(tag_name)
    ).first_or_404()
    tag_to_change.is_active = True if not tag_to_change.is_active else False
    db.session.commit()
    return tag_to_change
