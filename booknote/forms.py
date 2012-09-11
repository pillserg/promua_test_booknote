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
        self.need_m2m_save = False
        self.obj = None
        super(BookForm, self).__init__(*args, **kwargs)
        if not self.obj:
            self.need_m2m_save = True

    def _get_authors_ids(self):
        return self.authors.data.split(',')

    def save(self):
        if not self.obj:
            self.obj = Book(title=unicode(self.title.data))
            self.need_m2m_save = True
        else:
            self.obj.title = self.title.data
        return self.obj

    def save_m2m(self):
        if self.authors.data:
            ids = self._get_authors_ids()
            authors = Author.query.filter(Author.id.in_(ids)).all()
            for author in authors:
                self.obj.authors.append(author)
        return self.obj


class AuthorForm(Form):
    name = TextField('name', validators=[Required(), Length(min=5, max=256)])

    def save(self):
        author = Author(name=unicode(self.name.data))
        return author
