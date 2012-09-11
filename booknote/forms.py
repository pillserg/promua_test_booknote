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
        super(BookForm, self).__init__(*args, **kwargs)
        if 'obj' in kwargs:
            obj = kwargs.pop('obj')
            self.instance = obj
        super(BookForm, self).__init__(*args, **kwargs)

    def save(self):
        if not self.instance:
            book = Book(title=self.title.data)
        else:
            self.instance.titile = self.title.data
            book = self.instance
        return book


class AuthorForm(Form):
    name = TextField('name', validators=[Required(), Length(min=5, max=256)])
    def save(self):
        author = Author(name=self.name.data)
        return author
