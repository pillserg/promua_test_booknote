from flask import request, current_app, json


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
