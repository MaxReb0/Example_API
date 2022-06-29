import json
from flask import Blueprint, make_response

health_blueprint = Blueprint("health", __name__, url_prefix="/health")

@health_blueprint.route("/", methods=['GET'])
def health_handler():
    return make_response(json.dumps({"hello": "world"}))