import os
from flask import Flask, current_app

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    """
    directory = os.path.join(app.instance_path, 'images')
    if not os.path.exists(directory):
        os.mkdir(directory)
    """

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER = os.path.join(app.instance_path, 'images'),
        STATIC_FOLDER = "anigen/static/"
    )

    image_dir = os.path.join(app.config['STATIC_FOLDER'],"images/")
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup stable diffusion stuff now, so that it doesn't have to start-up every time someone wants to post

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
