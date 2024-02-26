from datetime import datetime
from urllib.parse import urljoin

from flask import url_for

from . import db


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = dict()
        if kwargs.get('search'):
            data = {'_search_string': kwargs.get('search')}
        if kwargs.get('filters'):
            data.update({'_filters': [
                tag.name for tag in Tag.query.filter_by(is_active=True)
            ]})
        data.update({
            'count': resources.total,
            'next': url_for(endpoint, page=page + 1, per_page=per_page,
                            **kwargs) if resources.has_next else None,
            'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                            **kwargs) if resources.has_prev else None,
            'results': [item.to_dict() for item in resources.items],
        })
        return data


link_tag = db.Table(
    'link_tag',
    db.Column(
        'link_id', db.Integer, db.ForeignKey('links.id'), primary_key=True
    ),
    db.Column(
        'tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True
    )
)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False)
    links = db.relationship('Link', secondary=link_tag, back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.name}>'

    def to_dict(self):
        return dict(
            name=self.name,
            is_active=self.is_active
        )


class Link(PaginatedAPIMixin, db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    tags = db.relationship('Tag', secondary=link_tag, back_populates='links')
    original = db.Column(db.String(), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    lang = db.Column(db.String, nullable=False, default='RU')

    def __repr__(self):
        return f'<Link {self.text[:30]}>'

    def to_dict(self):
        return dict(
            id=self.id,
            original=self.original,
            short=urljoin('http://localhost:5000/', self.short),
            tags=[tag.name for tag in self.tags],
            text=self.text,
            timestamp=self.timestamp,
            lang=self.lang
        )

    def from_dict(self, data):
        for field in ['tags', 'text', 'original', 'short', 'lang']:
            if field in data:
                setattr(self, field, data[field])
