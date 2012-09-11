# -*- coding: utf-8 -*-
import simplejson

from flask import render_template, flash, redirect, url_for, jsonify
from flask import session, request, g
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.login import login_required

from booknote import app, db, lm, oid
from booknote.models import User, Book, Author
from booknote.forms import LoginForm, BookForm, AuthorForm
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
        remember_me = session['remember_me']
        session.pop('remember_me')
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/books/')
def books_list():
    books = Book.query.order_by('-id').all()
    return render_template('books_list.html', books=books)


@app.route('/authors/')
def authors_list():
    authors = Author.query.order_by('-id').all()
    return render_template('authors_list.html', authors=authors)


@app.route('/')
def index():
    return books_list()


@app.route('/books/add/', methods=['GET', 'POST', ])
@login_required
def add_book():
    form = BookForm()
    success = False
    data = ''
    if form.validate_on_submit():
        success = True
        data = repr(form.title.data) + repr(form.authors.data)
        db.session.add(form.save())
        db.session.commit()
        if form.need_m2m_save:
            db.session.add(form.save_m2m())
            db.session.commit()
        flash('book was successfully added')
        return redirect(url_for('books_list'))
    return render_template('add_book.html',
                           form=form, data=data, success=success)


@app.route('/books/delete/<int:id>', methods=['POST', ])
@login_required
def delete_book(id):
    count = Book.query.filter_by(id=id).delete()
    db.session.commit()
    return jsonify(dict(success=bool(count)))


@app.route('/books/edit/<int:id>', methods=['GET', 'POST', ])
@login_required
def edit_book(id):
    book = Book.query.get(id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        if book:
            form.populate_obj(book)
        else:
            book = form.save()
        db.session.add(book)
        db.session.commit()
        flash('Successfully updated bood info')
        return redirect(url_for('books_list'))
    return render_template('add_book.html', form=form)


@app.route('/authors/add/', methods=['GET', 'POST', ])
@login_required
def add_author():
    form = AuthorForm()
    success = False
    data = ''
    if form.validate_on_submit():
        success = True
        data = repr(form.name.data)
        db.session.add(form.save())
        db.session.commit()
    return render_template('add_author.html',
                           form=form, data=data, success=success)


@app.route('/authors/delete/<int:id>', methods=['POST', ])
@login_required
def delete_author(id):
    count = Author.query.filter_by(id=id).delete()
    db.session.commit()
    return jsonify(dict(success=bool(count)))


@app.route('/authors/edit/<int:id>', methods=['GET', 'POST', ])
@login_required
def edit_author(id):
    return 'temp edit '


@app.route('/authors_autocomplite')
def authors_autocomplite():
    # add if request.is_xhr here
    q = request.args.get('q')

    if not q or len(q) < app.config['MIN_AUTOCOMPLITE_LENGTH']:
        return jsonify(success=False, error='parameter is to short')

    authors = Author.case_insensetive_get_authors_where_name_contains(q)
    authors_lst = [{ 'id': a.id, 'name': a.name } for a in authors]
    return to_json(authors_lst)


