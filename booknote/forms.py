from flask.ext.wtf import Form, TextField, BooleanField, Field, TextInput
from flask.ext.wtf import Required, Length
from flask import json

from booknote.models import Book, Author


NEW_ID_STR = 'new'


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []
        if NEW_ID_STR in self.data:
            pass


class AuthorsTagListField(TagListField):
    json_data = ''
    def process_data(self, authors_q):
        self.data = ''
        if authors_q:
            authors = authors_q.order_by('name').all()
            self.data = ', '.join([a.name for a in authors])
            self.json_data = json.dumps([a.autocomplete_dict for a in authors])


class LoginForm(Form):
    openid = TextField('openid', validators=[Required(), ])
    remember_me = BooleanField('remember_me', default=False)


class BookForm(Form):
    title = TextField('title', validators=[Required(), Length(min=5, max=256)])
    authors = AuthorsTagListField('authors')

    def __init__(self, *args, **kwargs):
        self.obj = kwargs.get('obj', None)
        super(BookForm, self).__init__(*args, **kwargs)

    def get_instance(self):
        return self.obj

    def save(self):
        if not self.obj:
            self.obj = Book(title=unicode(self.title.data))
        else:
            self.obj.title = self.title.data
        return self.obj

    def save_m2m(self):
        if self.authors.data:
            ids = set(self.authors.data)
            return self.obj.update_authors(ids)
        return False


class AuthorForm(Form):
    name = TextField('name', validators=[Required(), Length(min=5, max=256)])

    def __init__(self, *args, **kwargs):
        self.obj = kwargs.get('obj', None)
        super(AuthorForm, self).__init__(*args, **kwargs)

    def save(self):
        if not self.obj:
            author = Author(name=unicode(self.name.data))
        else:
            self.populate_obj(self.obj)
            author = self.obj
        return author
