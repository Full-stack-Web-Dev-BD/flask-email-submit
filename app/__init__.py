from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register the user and product blueprints
    from app.user.user import user_blueprint
    from app.calc.calc import calc_blueprint


    # routes
    app.register_blueprint(calc_blueprint)
    app.register_blueprint(user_blueprint)
    
    return app
