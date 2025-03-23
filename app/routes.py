from flask import Blueprint, jsonify

# Define a blueprint named 'main'
main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def hello_world():
    return jsonify(message="Hello, world!")
