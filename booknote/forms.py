from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required, Length

from booknote.models import Book, Author

class LoginForm(Form):
    openid = TextField('openid', validators=[Required(), ])
    remember_me = BooleanField('remember_me', default=False)


class BookForm(Form):
    title = TextField('title', validators=[Required(), Length(min=5, max=256)])
    authors = TextField('authors')

    def save(self):
        book = Book(title=self.title.data)
        return book
