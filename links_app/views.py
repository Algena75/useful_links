from flask import redirect, render_template, request, url_for

from . import app, db
from .forms import AddLinkForm, SearchForm
from .models import Link, Tag
from .utils import change_tag_is_active, create_new_link
from .validators import validate_form


@app.route('/', methods=['GET', 'POST'])
def index_view():
    page = request.args.get('page', 1, type=int)
    if Tag.query.filter_by(is_active=True).count() == 0:
        link_items = Link.query.paginate(
            page=page, per_page=10, error_out=False
        )
    else:
        link_items = (
            db.session.query(Link).join(Link.tags).filter(Tag.is_active == 1)
            .paginate(page=page, per_page=10, error_out=False)
        )
    form = AddLinkForm()
    search_form = SearchForm()
    if form.submit_1.data and form.validate():
        form, wrong = validate_form(form)
        if not wrong:
            link = Link(
                original=form.original_link.data,
                short=form.custom_id.data,
                text=form.link_description.data,
                lang=form.text_lang.data
            )
            tags = form.link_tags.data if form.link_tags.data else 'Python'
            create_new_link(link, tags)
            return redirect(url_for('index_view'))
    return render_template(
        'links.html',
        form=form,
        search_form=search_form,
        links=link_items.items,
        pagination=link_items,
        tags=Tag.query.all()
    )


@app.route('/<short_url>')
def redirect_func(short_url):
    page = Link.query.filter_by(short=short_url).first_or_404()
    return redirect(page.original)


@app.route('/tag/<tag_name>')
def change_tag_status(tag_name):
    change_tag_is_active(tag_name)
    return redirect(url_for('index_view'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    page = request.args.get('page', 1, type=int)
    search_form = SearchForm(request.form)
    search_string = search_form.data['search_string']
    if not search_string or search_string.strip() == '':
        return redirect(url_for('index_view'))
    link_items = Link.query.filter(
        Link.text.contains(search_string)
    ).paginate(page=page, per_page=10, error_out=False)
    found = True if len(link_items.items) > 0 else False
    form = AddLinkForm()
    return render_template(
        'search.html',
        form=form,
        search_form=search_form,
        links=link_items.items,
        pagination=link_items,
        found=found,
        tags=Tag.query.all()
    )


@app.route('/api/docs')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')
