# -*- coding: utf-8 -*-
import simplejson

from flask import render_template, flash, redirect, url_for, jsonify
from flask import session, request, g
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.login import login_required

from booknote import app, db, lm, oid
from booknote.models import User, Book, Author
from booknote.forms import LoginForm, BookForm, AuthorForm, SearchForm
from booknote.helpers import to_json


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    # add current user to g
    g.user = current_user


@app.route('/login', methods=['GET', 'POST', ])
@oid.loginhandler
def login():
    """
    trys to login user via openID.
    Google by defaul, but other providers can be added in config file.
    After succesfull response after_login is called where user is logged
    in via flaks-login.
    """
    if g.user and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config.get('OPENID_PROVIDERS'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for('index'))


@oid.after_login
def after_login(resp):
    """
    review flask-openid docs if something is not clear here
    """
    if not resp.email:
        flash('Invalid login. Please try again.')
        redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if not user:
        username = resp.nickname or resp.email.split('@')[0]
        username = User.make_unique_username(username)
        user = User(username=username, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session.pop('remember_me')
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/books/', defaults={'page': 1})
@app.route('/books/page/<int:page>')
def books_list(page, per_page=app.config.get('PER_PAGE')):
    pagination = Book.query.order_by('-title').paginate(page, per_page)
    return render_template('books_list.html', pagination=pagination)


@app.route('/authors/', defaults={'page': 1})
@app.route('/authors/page/<int:page>')
def authors_list(page, per_page=app.config.get('PER_PAGE')):
    pagination = Author.query.order_by('-name').paginate(page, per_page)
    return render_template('authors_list.html', pagination=pagination)


@app.route('/')
def index():
    # it's not actualy recently added
    # we need some kind of timestamp in db, but it'll do for now
    NUM_OF_BOOKS_ON_INDEX = 8
    books = Book.query.order_by('-id')[:NUM_OF_BOOKS_ON_INDEX]
    return render_template('index.html', books=books)


def add_or_edit_book(form, msg=None, template_name='process_book.html'):
    if form.validate_on_submit():
        db.session.add(form.save())
        db.session.commit()
        if form.save_m2m():
            db.session.add(form.get_instance())
            db.session.commit()
        if msg:
            flash(msg)
        return redirect(url_for('books_list'))
    return render_template(template_name, form=form)


@app.route('/books/add/', methods=['GET', 'POST', ])
@login_required
def add_book():
    form = BookForm()
    msg = u'Book was successfully added'
    return add_or_edit_book(form, msg)


@app.route('/books/delete/<int:id>', methods=['POST', ])
@login_required
def delete_book(id):
    db.session.delete(Book.query.get_or_404(id))
    db.session.commit()
    return jsonify(dict(success=True))


@app.route('/books/edit/<int:id>', methods=['GET', 'POST', ])
@login_required
def edit_book(id):
    msg = 'Book information was successfully updated'
    form = BookForm(obj=Book.query.get_or_404(id))
    return add_or_edit_book(form, msg)


def add_or_edit_author(form, msg=None, template_name='process_author.html'):
    if form.validate_on_submit():
        db.session.add(form.save())
        db.session.commit()
        if msg:
            flash(msg)
        return redirect(request.args.get('next') or url_for('authors_list'))
    return render_template(template_name, form=form)


@app.route('/authors/add/', methods=['GET', 'POST', ])
@login_required
def add_author():
    form = AuthorForm()
    msg = u'Author was successfully added'
    return add_or_edit_author(form, msg)


@app.route('/authors/edit/<int:id>', methods=['GET', 'POST', ])
@login_required
def edit_author(id):
    form = AuthorForm(obj=Author.query.get_or_404(id))
    msg = u'Author information was successfully updated'
    return add_or_edit_author(form, msg)


@app.route('/authors/delete/<int:id>', methods=['POST', ])
@login_required
def delete_author(id):
    db.session.delete(Author.query.get_or_404(id))
    db.session.commit()
    return jsonify(dict(success=True))


@app.route('/authors_autocomplite')
def authors_autocomplite():
    """
    autocomplite view used by jquery-tokeninput on book add/edit page
    """
    # request.is_xhr ommited for brevity
    q = request.args.get('q')

    if not q or len(q) < app.config['MIN_AUTOCOMPLITE_LENGTH']:
        return jsonify(success=False, error='parameter is to short')

    authors = Author.case_insensetive_get_authors_where_name_contains(q)
    authors_lst = [a.autocomplete_dict for a in authors]
    return to_json(authors_lst)


# error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/search', methods=['GET', 'POST', ], defaults={'page': 1})
@app.route('/search/<int:page>')
def search(page, per_page=app.config.get('PER_PAGE')):
    """
    search view
    actual search query is implemented in forms.SearchForm
    some external solution like whoosh would be an overhead in this case
    simple search looks for like %query_string% nothing more

    2.    Поиск книг по названию либо автору (c)
    """
    form = SearchForm(csrf_enabled=False)
    search_query = ''
    books = []
    pagination = []
    if form.validate_on_submit():
        search_query = form.search_input.data
        books = form.find_books()
        pagination = books.paginate(page, per_page)
    return render_template('search_results.html',
                           search_query=search_query,
                           form=form,
                           pagination=pagination)
