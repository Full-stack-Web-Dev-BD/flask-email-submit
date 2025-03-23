from flask import Blueprint, jsonify

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/user', methods=['GET'])
def hello_user():
    return jsonify(message="Hello, User!")
