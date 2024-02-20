from flask import jsonify, render_template
from http import HTTPStatus

from . import app, db
from .forms import SearchForm


class InvalidAPIUsage(Exception):
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(message=self.message)


@app.errorhandler(404)
def page_not_found(error):
    search_form = SearchForm()
    return render_template(
        '404.html', search_form=search_form
    ), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_error(error):
    search_form = SearchForm()
    db.session.rollback()
    return render_template(
        '500.html', search_form=search_form
    ), HTTPStatus.INTERNAL_SERVER_ERROR


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code
