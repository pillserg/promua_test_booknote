from flask import request, current_app, json


def to_json(obj):
    """
    flask.jsonify converts everything to dict
    this is thinner
    """
    return current_app.response_class(
        json.dumps(obj, indent=None if request.is_xhr else 2),
        mimetype='application/json')


