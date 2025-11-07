from flask import Blueprint, jsonify

bp = Blueprint('api', __name__)

@bp.route('/')
def home():
    return jsonify({"message": "Welcome to Flask REST API!"})

@bp.route('/ping')
def ping():
    return jsonify({"status": "ok"})
