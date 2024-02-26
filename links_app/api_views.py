from http import HTTPStatus

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import Link, Tag
from .utils import change_tag_is_active, create_new_link
from .validators import validate_link, validate_search_string


@app.route('/api/', methods=['GET', 'POST'])
def add_record():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        if Tag.query.filter_by(is_active=True).count() > 0:
            links = Link.to_collection_dict(
                db.session.query(Link).join(Link.tags).filter(
                    Tag.is_active == 1
                ), page, per_page, '.add_record', filters=True
            )
        else:
            links = Link.to_collection_dict(
                Link.query, page, per_page, '.add_record'
            )
        if not links:
            raise InvalidAPIUsage('Записей не найдено', HTTPStatus.NOT_FOUND)
        return jsonify(links), HTTPStatus.OK
    if 'multipart' in request.content_type:
        data = request.form.to_dict()
    else:
        data = request.get_json()
    data = validate_link(data)
    new_record = Link(
        original=data.get('original_url'),
        short=data.get('short_link'),
        text=data.get('description'),
        lang=data.get('language')
    )
    tags = data.get('tags') if data.get('tags') else 'Python'
    new_record = create_new_link(new_record, tags)
    data['tags'] = [x.name for x in new_record.tags]
    data['id'] = new_record.id
    return jsonify(data), HTTPStatus.CREATED


@app.route('/api/<short_id>/', methods=['GET'])
def get_url(short_id):
    record = Link.query.filter_by(short=short_id).first()
    if record is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'original_url': record.original}), HTTPStatus.OK


@app.route('/api/links/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    link = Link.query.filter_by(id=id).first()
    if not link:
        raise InvalidAPIUsage('Запись не найдена', HTTPStatus.NOT_FOUND)
    db.session.delete(link)
    db.session.commit()
    return 'Запись удалена', HTTPStatus.NO_CONTENT


@app.route('/api/tags/', methods=['GET'])
def get_tags():
    return jsonify({'tags': [item.to_dict() for item in Tag.query.all()]})


@app.route('/api/tags/<tag_name>/', methods=['POST'])
def api_change_tag_status(tag_name):
    tag_to_change = change_tag_is_active(tag_name)
    return jsonify(tag_to_change.to_dict()), HTTPStatus.OK


@app.route('/api/search/<search_string>/', methods=['GET'])
def search_func(search_string):
    search_string = validate_search_string(search_string).strip()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    links = Link.to_collection_dict(
        Link.query.filter(Link.text.contains(search_string)),
        page, per_page, '.search_func', search=search_string
    )
    if not links:
        raise InvalidAPIUsage('Записей не найдено', HTTPStatus.NOT_FOUND)
    return jsonify(links), HTTPStatus.OK
