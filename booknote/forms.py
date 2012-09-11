from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required, Length

from booknote.models import Book, Author

class LoginForm(Form):
    openid = TextField('openid', validators=[Required(), ])
    remember_me = BooleanField('remember_me', default=False)


class BookForm(Form):
    title = TextField('title', validators=[Required(), Length(min=5, max=256)])
    authors = TextField('authors')

    def __init__(self, *args, **kwargs):
        self.instance = None
        self.need_m2m_save = False

        if 'obj' in kwargs:
            obj = kwargs.pop('obj')
            self.instance = obj
        super(BookForm, self).__init__(*args, **kwargs)

    def _get_authors_ids(self):
        return self.authors.data.split(',')

    def save(self):
        if not self.instance:
            self.instance = Book(title=unicode(self.title.data))
            self.need_m2m_save = True
        else:
            self.instance.title = self.title.data

        print '------------'
        print 'instance: ', self.instance.title
        print '------------'
        return self.instance

    def save_m2m(self):
        print '------------'
        print 'save m2m called'
        print '------------'
        if self.authors.data:
            print '------------'
            print 'self.authors.data: ', self.authors.data
            print '------------'
            ids = self._get_authors_ids()
            authors = Author.query.filter(Author.id.in_(ids)).all()
            print '------------'
            print 'ids: ', ids
            print 'authors: ', authors
            print '------------'
            for author in authors:
                self.instance.authors.append(author)
        return self.instance


class AuthorForm(Form):
    name = TextField('name', validators=[Required(), Length(min=5, max=256)])
    def save(self):
        author = Author(name=unicode(self.name.data))
        return author
