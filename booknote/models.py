from booknote import app, db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return u'<User: {}'.format(self.username)


book2author = db.Table('book2author',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id')))


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)

    def __repr__(self):
        return u'<Book: {}'.format(self.title)

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    # still not shure about joins stuff here will review later 
    books = db.relationship('Book',
                            secondary=book2author,
                            primaryjoin=(book2author.c.book_id == id),
                            secondaryjoin=(book2author.c.author_id == id),
                            backref=db.backref('authors', lazy='dynamic'),
                            lazy='dynamic')

    def __repr__(self):
        return u'<Author: {}'.format(self.name)

