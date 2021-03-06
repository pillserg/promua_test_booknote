# -*- coding: utf-8 -*-
import os
import unittest
from itertools import cycle, chain

from flask import Flask, url_for, g, request, session, current_app, json
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.login import LoginManager
from flask.ext.testing import TestCase
from flask.ext.sqlalchemy import SQLAlchemy

from config import basedir
from booknote import app, db
from booknote.models import User, Book, Author
from booknote.forms import BookForm, AuthorForm, SearchForm


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
        # But could not found normal way to test login related features
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

    def create_user(self, username='bazingus', email='bazingus@i.ua'):
        user = User(username='bazingus', email='john@example.com')
        db.session.add(user)
        db.session.commit()
        return user.id

    def create_test_data(self):
        self.user_id = self.create_user()
        booksiter = cycle(('book', u'книга', u'Журнал'))
        for title in [unicode(booksiter.next() + str(i)) for i in xrange(30)]:
            db.session.add(Book(title=title))
        authorsiter = cycle(('john dou', u'Барнабус', u'Рей Бредбери'))
        for name in [unicode(authorsiter.next() + str(i)) for i in xrange(5)]:
            db.session.add(Author(name=name))
        db.session.commit()
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
        response = c.get("/login",
                         query_string={"id": user.id, 'permanent': True})
        assert response.data == u"Logged in"
        resp = c.get('/')
        assert user.username in resp.data.decode('utf-8')

    def tests_main_views_responses(self):
        """ sanity check """
        with self.app.test_request_context():
            self.assert200(self.client.get(url_for('index')))
            self.assert200(self.client.get(url_for('books_list')))
            self.assertRedirects(self.client.get(url_for('add_book')),
                                 # not very generic
                                 url_for('login') + '?next=%2Fbooks%2Fadd%2F')
            self.assert200(self.client.get(url_for('authors_list')))
            self.assert200(self.client.get(url_for('search')))

    def test_book(self):
        with self.app.test_request_context():
            self.create_test_data()
            user = User.query.get(self.user_id)
            self.login(user)
            resp = self.client.get(url_for('add_book'))
            assert 'form' in resp.data

            # test add
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

            #test edit
            # change title and add authors
            booktitle = booktitle + '_upd'
            authors_ids_str = ','.join((str(a.id) for a in Author.query.all()[:4]))
            resp = self.client.post(url_for('edit_book', id=new_book.id),
                                    data=dict(title=booktitle,
                                              authors=authors_ids_str))
            book = Book.query.filter_by(title=booktitle).first()
            assert book
            assert book.id == new_book.id
            assert book.authors.count() == 4

            # remove some authors
            authors_ids_str = ','.join((str(a.id) for a in Author.query.all()[:2]))
            resp = self.client.post(url_for('edit_book', id=book.id),
                                    data=dict(title=booktitle,
                                              authors=authors_ids_str))
            book = Book.query.filter_by(title=booktitle).first()
            assert book
            assert book.authors.count() == 2

            # add and remove authors
            authors_ids_str = ','.join((str(a.id) for a in chain(Author.query.all()[:1], Author.query.all()[2:5])))
            resp = self.client.post(url_for('edit_book', id=book.id),
                                    data=dict(title=booktitle,
                                              authors=authors_ids_str))
            book = Book.query.filter_by(title=booktitle).first()
            assert book
            assert book.authors.count() == 4

            # test author removal from m2m on author delet
            # not logical place for it, but still
            id = book.authors_ids_list[0]
            resp = self.client.post(url_for('delete_author', id=id),)
            book = Book.query.filter_by(title=booktitle).first()
            assert id not in book.authors_ids_list
            new_author_with_same_id = Author(id=id, name='Stranger')
            db.session.add(new_author_with_same_id)
            db.session.commit()
            book = Book.query.filter_by(title=booktitle).first()
            assert id not in book.authors_ids_list

            # test delete book
            resp = self.client.post(url_for('delete_book', id=book.id),)
            assert resp.json['success']
            book = Book.query.filter_by(title=booktitle).first()
            assert not book

            resp = self.client.get(url_for('edit_book', id=999),)
            self.assert404(resp)

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

            name = name + u'_upd'
            resp = self.client.post(url_for('edit_author', id=new_author.id),
                                    data=dict(name=name))
            author = Author.query.filter_by(name=name).first()
            assert author
            assert author.id == new_author.id

    def test_autocomplite(self):
        with self.app.test_request_context():
            self.create_test_data()
            resp = self.client.get(url_for('authors_autocomplite'),
                                   query_string={'q': 'john'})
            assert len(json.loads(resp.data)) == 2

            # test case insensetive search
            resp = self.client.get(url_for('authors_autocomplite'),
                                   query_string={'q': u'Барна'})
            capital_res = resp.data
            assert len(json.loads(resp.data)) == 2
            resp = self.client.get(url_for('authors_autocomplite'),
                                   query_string={'q': u'барна'})
            assert len(json.loads(resp.data)) == 2
            assert capital_res == resp.data

    def test_search(self):
        with self.app.test_request_context():
            # init
            db.session.add_all([
                                Book(title=u'bAzInGus'),
                                Book(title=u'Туда и обратно'),
                                Book(title=u'туда и назад'),
                                Book(title=u'Война и мир')
                                ])

            db.session.add_all([
                                Author(name=u'Толстой Лев Николаевич'),
                                Author(name=u'Горький'),
                                Author(name=u'голохвостов'),
                                Author(name=u'Тудашкин')
                                ])
            db.session.commit()
            book1 = Book.query.filter_by(title=u'bAzInGus').first()
            book1.authors.append(Author.query.filter_by(name=u'Толстой Лев Николаевич').first())
            book1.authors.append(Author.query.filter_by(name=u'Горький').first())
            book1.authors.append(Author.query.filter_by(name=u'голохвостов').first())
            book1.authors.append(Author.query.filter_by(name=u'Тудашкин').first())

            db.session.commit()

            book2 = Book.query.filter_by(title=u'Война и мир').first()
            book2.authors.append(Author.query.filter_by(name=u'Толстой Лев Николаевич').first())

            # test search
            f = SearchForm()
            f.search_input.data = u'Война и мир'
            assert f.find_books().count() == 1

            f.search_input.data = u'война и мир'
            assert f.find_books().count() == 1

            f.search_input.data = u'Baz'
            assert f.find_books().count() == 1

            f.search_input.data = u'Туда'
            assert f.find_books().count() == 2

            f.search_input.data = u'Толстой'
            assert f.find_books().count() == 1

            f.search_input.data = u'Николаевич'
            assert f.find_books().count() == 1

            f.search_input.data = u'николаевич'
            assert f.find_books().count() == 1

            # test page
            resp = self.client.post(url_for('search'),
                                    data={'search_input': u'голо'})
            assert u'голо' in resp.data.decode('utf-8')


if __name__ == '__main__':
    unittest.main()
