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

    # simploe caching here would be very usefull.
    # but simple db column based cache would change db schema
    # and some external caching seems like overhead
    # thus just left it as is 
    def authors_list(self):
        return self.authors.order_by('name')

    @property
    def authors_names(self):
        return [a.name for a in self.authors_list()]

    def __repr__(self):
        return u'<Book: {}>'.format(self.title)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    # still not shure about joins stuff here will review later 
    books = db.relationship('Book',
                            secondary=book2author,
#                            primaryjoin=(book2author.c.book_id == id),
#                            secondaryjoin=(book2author.c.author_id == id),
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
            authors = Author.get_authors_where_name_contains(unicode(q).capitalize())
        return authors


    def __repr__(self):
        return u'<Author: {}>'.format(self.name)

