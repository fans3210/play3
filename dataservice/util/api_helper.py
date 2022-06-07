from app.errs import ApiError
from flask import jsonify


def register_errors(app):
    # err handlers
    @app.errorhandler(ApiError)
    def handle_api_err(err):
        return make_res(err.code, err.msg)


def make_res(code, msg=None, payload=None):
    result = {
        "status_code": code
    }
    if msg:
        result["message"] = msg
    if payload:
        result["data"] = payload
    res = jsonify(result)
    return res, code
