# -*- coding: utf-8 -*-
import os
import unittest
from itertools import cycle

from flask import Flask, url_for, g, request, session, current_app
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.login import LoginManager
from flask.ext.testing import TestCase
from flask.ext.sqlalchemy import SQLAlchemy

from config import basedir
from booknote import app, db
from booknote.models import User, Book, Author

def setup_interactive(app):
    lm = LoginManager()
    lm.login_view = "login"
    lm.user_loader(get_user)
    @lm.unauthorized_handler
    def unauth():
        return "UNAUTHORIZED!"
    lm.setup_app(app)

class MainTestCase(TestCase):
    def create_app(self):
        app.config.from_object('tests_config')

        # I am really sleepy now. Played with it for a while now. 
        # but could not found normal way to test login related features
        # thus something like this:
        @app.route("/login")
        def login():
            id = int(request.args["id"])
            user = User.query.get(id)
            force = "force" in request.args
            remember = "remember" in request.args
            if login_user(user, force=force, remember=remember):
                if "permanent" in request.args:
                    session.permanent = True
                return u"Logged in"
            else:
                return u"Go away, creeper"

        return app

    def setUp(self):
        db.create_all()
        self.user = None

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, user):
        self.client.get("/login",
                        query_string={"id": user.id, 'permanent': True})

    def logout(self):
        self.client.get("/logout")

    def create_test_data(self):
        user = User(username='bazingus', email='john@example.com')
        db.session.add(user)
        booksiter = cycle(('book', u'книга', u'Журнал'))
        for title in [unicode(booksiter.next() + str(i)) for i in xrange(30)]:
            db.session.add(Book(title=title))
        authorsiter = cycle(('john dou', u'Барнабус', u'Рей Бредбери'))
        for name in [unicode(authorsiter.next() + str(i)) for i in xrange(5)]:
            db.session.add(Author(name=name))
        db.session.commit()

        self.user_id = user.id

        book = Book.query.get(1)
        for author in Author.query.all()[0:3]:
            book.authors.append(author)
        db.session.add(book)
        db.session.commit()


    def test_make_unique_nickname(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        username = User.make_unique_username('john')
        assert username != 'john'
        u = User(username=username, email='susan@example.com')
        db.session.add(u)
        db.session.commit()
        username2 = User.make_unique_username('john')
        assert username2 != 'john'
        assert username2 != username

    def test_login(self):
        self.create_test_data()
        c = self.client
        user = User.query.first()
        response = c.get("/login", query_string={"id": user.id, 'permanent': True})
        assert response.data == u"Logged in"
        resp = c.get('/')
        assert user.username in resp.data.decode('utf-8')

    def tests_main_views_responses(self):
        """ sanity check """
        with self.app.test_request_context():
            self.assert200(self.client.get(url_for('books_list')))
            self.assertRedirects(self.client.get(url_for('add_book')),
                                 # not very generic
                                 url_for('login') + '?next=%2Fbooks%2Fadd%2F')
            self.assert200(self.client.get(url_for('authors_list')))

    def test_book(self):
        with self.app.test_request_context():
            self.create_test_data()
            user = User.query.get(self.user_id)
            self.login(user)
            resp = self.client.get(url_for('add_book'))
            assert 'form' in resp.data
            booktitle = 'new_cool_test_book'
            resp = self.client.post(url_for('add_book'),
                                    data=dict(title=booktitle,
                                              authors=''))
            new_book = Book.query.filter_by(title=booktitle).first()
            assert new_book

            authors_ids_str = ','.join((str(a.id) for a in Author.query.all()[:3]))
            booktitle = u'Вторая тестовая книжка'
            resp = self.client.post(url_for('add_book'),
                                    data=dict(title=booktitle,
                                              authors=authors_ids_str))
            new_book = Book.query.filter_by(title=booktitle).first()
            assert new_book
            assert new_book.authors.count() == 3

    def test_author(self):
        with self.app.test_request_context():
            self.create_test_data()
            user = User.query.get(self.user_id)
            self.login(user)
            resp = self.client.get(url_for('add_author'))
            assert 'form' in resp.data
            name = u'Бильбо Беггинс'
            resp = self.client.post(url_for('add_author'), data=dict(name=name))
            new_author = Author.query.filter_by(name=name).first()
            assert new_author


if __name__ == '__main__':
    unittest.main()
