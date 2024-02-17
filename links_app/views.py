from flask import abort, flash, redirect, render_template, url_for, request

from . import app, db
from .models import Link, Tag
from .forms import AddLinkForm, SearchForm
from .utils import create_new_link, get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    page = request.args.get('page', 1, type=int)
    if Tag.query.filter_by(is_active=True).count() == 0:
        link_items = Link.query.paginate(
            page=page, per_page=10, error_out=False
        )
    else:
        link_items = (
            db.session.query(Link).join(Link.tags).filter(Tag.is_active==True)
            .paginate(page=page, per_page=10, error_out=False)
        )
    form = AddLinkForm()
    search_form = SearchForm()
    wrong = False
    if form.submit_1.data and form.validate():
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
        if not wrong:
            create_new_link(form)
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
    tag_to_change = Tag.query.filter_by(name=tag_name).first_or_404()
    tag_to_change.is_active = True if not tag_to_change.is_active else False
    db.session.commit()
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
    found = True if len(link_items.items)>0 else False
        
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
