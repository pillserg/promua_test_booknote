from itertools import chain
import os

from flask import request, current_app, json, url_for
from booknote import app, db
from config import basedir


DELIMITER = '|||'
FILENAME = 'dumpdata.csv'


def to_json(obj):
    """
    flask.jsonify converts everything to dict
    this is thinner
    """
    # I really think there are something built in like this,
    # but unfortunately i couldn't find it.
    return current_app.response_class(
        json.dumps(obj, indent=None if request.is_xhr else 2),
        mimetype='application/json')


def url_for_different_page(page):
    """References a different page."""
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_different_page'] = url_for_different_page


def capfirst(s):
    if len(s) == 1:
        return s.upper()
    else:
        return ''.join((s[0].upper(), s[1:]))


def export_books(books=None, path=None):
    """
    this to functions are really simple and silly, but they work as expected )
    """
    if not books:
        from booknote.models import Book
        books = Book.query.all()

    lst = []
    for book in books:
        lst.append(DELIMITER.join(chain([book.title, ],
                                        [a.name for a in book.authors.all()])))
    data = '\n'.join(lst)

    if not path:
        path = os.path.join(basedir, FILENAME)
    with open(path, 'w') as f:
        f.write(data)


def import_books(path=None):
    """
    imports data from file
    better use only on newly created db
    dublicated names are overrided
    """
    from booknote.models import Book, Author
    if not path:
        path = os.path.join(basedir, FILENAME)
    with open(path, 'r') as f:
        raw_data = [line.decode('utf-8') for line in f.readlines()]
    for line in raw_data:
        line = line.split(DELIMITER)
        title = line[0]
        authors = line[1:]
        book = Book.query.filter_by(title=title).first()
        if not book:
            book = Book(title=title)
            db.session.add(book)
        if authors:
            db.session.commit()
            for author_name in authors:
                author = Author.query.filter_by(name=author_name).first()
                if not author:
                    author = Author(name=author_name)
                book.authors.append(author)
            db.session.add(book)
            db.session.commit()
    db.session.commit()
