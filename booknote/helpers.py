from flask import request, current_app, json, url_for
from booknote import app


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
