from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, URLField, TextAreaField, SearchField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

PATTERN = r'^[0-9A-Za-z]+$'


class AddLinkForm(FlaskForm):
    link_tags = StringField(
        'Введите теги через запятую',
        validators=[Optional(strip_whitespace=True),]
    )
    link_description = TextAreaField(
        validators=[DataRequired(message='Обязательное поле'),]
    )
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    URL()]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(1, 16, message='Длина не превышает 16 символов'),
                    Optional(strip_whitespace=True),
                    Regexp(PATTERN, message='Недопустимые символы')]
    )
    text_lang = SelectField(
        'Язык текста',
        choices=[('RU', 'rus'), ('EN', 'eng')]
    )
    submit_1 = SubmitField('Добавить')


class SearchForm(FlaskForm):
    search_string = SearchField(
        'Что искать?',
        validators=[Length(1, 16, message='Длина не превышает 16 символов')]
    )
    submit_2 = SubmitField('Искать')
