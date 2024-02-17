from datetime import datetime

from . import db


link_tag = db.Table('link_tag',
    db.Column('link_id', db.Integer, db.ForeignKey('links.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False)
    links = db.relationship('Link', secondary=link_tag, back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class Link(db.Model):
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
            id = self.id,
            original = self.original,
            short = self.short,
            tags = self.tags,
            text = self.text,
            timestamp = self.timestamp,
            lang = self.lang
        )

    def from_dict(self, data):
        for field in ['tags', 'text', 'original', 'lang']:
            if field in data:
                setattr(self, field, data[field])
