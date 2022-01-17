from flask import Blueprint

test_bp = Blueprint("test_bp", __name__)


@test_bp.route("/", methods=["GET"])
def test():
    return "It works!"
