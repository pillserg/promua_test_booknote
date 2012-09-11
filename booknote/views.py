from flask import render_template, flash, redirect, url_for
from flask import session, request, g
from booknote import app
from booknote.models import User, Book, Author


@app.route('/')
def index():
    #mock user
    g.user = User(username='blah', email='blah@i.ua')
    context = {}

    return render_template('index.html', **context)
