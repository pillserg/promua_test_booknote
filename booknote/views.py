from flask import render_template, flash, redirect, url_for
from flask import session, request, g
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.login import login_required

from booknote import app, db, lm, oid
from booknote.models import User, Book, Author
from booknote.forms import LoginForm, BookForm, AuthorForm


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
    return redirect(url_for('index'))


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


@app.route('/books')
def books_list():
    books = Book.query.all()
    return render_template('index.html', books=books)


@app.route('/authors')
def authors_list():
    authors = Author.query.all()
    return render_template('authors_list.html', authors=authors)


@app.route('/')
def index():
    return books_list()


@app.route('/add_book/', methods=['GET', 'POST', ])
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
    return render_template('add_book.html',
                           form=form, data=data, success=success)


@app.route('/delete_book/<int:id>', methods=['POST', ])
@login_required
def delete_book(id):
    try:
        book = Book.query.get(id)
    except Exception:
        pass

    return 'temp delete'


@app.route('/edit_book/<int:id>', methods=['GET', 'POST', ])
@login_required
def edit_book(id):
    return 'temp edit '


@app.route('/add_author/', methods=['GET', 'POST', ])
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


@app.route('/delete_author/')
@login_required
def delete_author():
    return 'temp delete'


@app.route('/edit_author/')
@login_required
def edit_author():
    return 'temp edit '
