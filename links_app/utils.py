import string
from random import choices

from . import db
from .models import Link, Tag

ARRAY = string.ascii_letters + string.digits


def get_unique_short_id(count_char=6):
    short_url = ''.join(choices(ARRAY, k=count_char))
    if Link.query.filter_by(short=short_url).first() is not None:
        get_unique_short_id()
    return short_url


def create_new_link(form):
    pass
    link = Link(
        original=form.original_link.data, 
        short=form.custom_id.data, 
        text=form.link_description.data,
        lang=form.text_lang.data
    )
    tags = form.link_tags.data if form.link_tags.data else 'Python'
    tags =[tag.strip() for tag in tags.split(',')]
    for tag in tags:
        tag_in_db = db.session.query(Tag).filter_by(name=tag).first()
        if tag_in_db:
            link.tags.append(tag_in_db)
        else:
            new_tag = Tag(name=tag)
            db.session.add(new_tag)
            db.session.flush()
            link.tags.append(new_tag)
    db.session.add(link)
    db.session.commit()
