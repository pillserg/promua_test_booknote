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

    def __repr__(self):
        return u'<Author: {}>'.format(self.name)

