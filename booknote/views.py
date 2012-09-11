from flask import render_template, flash, redirect, url_for
from flask import session, request, g
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.login import login_required

from booknote import app, db, lm, oid
from booknote.models import User, Book, Author
from booknote.forms import LoginForm


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


@app.route('/')
def index():
    #mock user
    context = {}

    return render_template('index.html', **context)
