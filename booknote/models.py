# -*- coding: utf-8 -*-
from flask.ext.login import UserMixin
from booknote import app, db


__all__ = ['User', 'Book', 'Author', ]


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

    @staticmethod
    def make_unique_username(username, version=2):
        if not User.query.filter_by(username=username).first():
            return username
        new_username = username + str(version)
        return User.make_unique_username(new_username, version + 1)

    def __repr__(self):
        return u'<User: {}>'.format(self.username)


book2author = db.Table('book2author',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id')))


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)

    @property
    def authors_names(self):
        # simple caching here would be usefull.
        # but simple db column based cache would change db schema
        # and external caching seems like overhead
        # thus just left it as is
        return [a.name for a in self.authors.order_by('name').all()]

    @property
    def authors_list(self):
        return self.authors.all()

    @property
    def authors_ids_list(self):
        return [a.id for a in self.authors_list]

    def get_authors_autocomplete_list(self):
        return [a.autocomplete_dict for a in self.authors.all()]

    def add_authors_by_ids(self, new_ids):
        ids_to_add = set(new_ids) - set(self.authors_ids_list)
        if ids_to_add:
            for author in Author.get_by_id(ids_to_add):
                self.authors.append(author)
        return len(ids_to_add)

    def remove_authors_by_ids(self, new_ids):
        ids_to_remove = set(self.authors_ids_list) - set(new_ids)
        if ids_to_remove:
            for author in Author.get_by_id(ids_to_remove):
                self.authors.remove(author)
        return len(ids_to_remove)

    def update_authors(self, ids):
        remove_count = self.remove_authors_by_ids(ids)
        add_count = self.add_authors_by_ids(ids)
        return remove_count + add_count

    def __repr__(self):
        return u'<Book: {}>'.format(self.title)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    books = db.relationship('Book',
                            secondary=book2author,
                            backref=db.backref('authors', lazy='dynamic'),
                            lazy='dynamic')

    @staticmethod
    def get_authors_where_name_contains(q):
        authors = Author.query.filter(Author.name.like(u'%{}%'.format(q)))
        return authors

    @staticmethod
    def case_insensetive_get_authors_where_name_contains(q):
        """
        Trys to cappitalize name
        It's really dull but i couldnt overcome
        unicode-casesensetive-insensetive-sqlite issues in apropriate time
        this method seems to do it's work
        """
        authors = Author.get_authors_where_name_contains(q)
        if not authors.count():
            authors = Author.get_authors_where_name_contains(
                                                    unicode(q).capitalize())
        return authors

    @property
    def books_count(self):
        # again - caching would be good.
        return self.books.count()

    @property
    def autocomplete_dict(self):
        return {'id': self.id, 'name': self.name}

    @staticmethod
    def get_by_id(ids):
        list(ids)
        return Author.query.filter(Author.id.in_(ids))

    def __repr__(self):
        return u'<Author: {}>'.format(self.name)
