import os

from flask import Flask, render_template
from job_posting_app.db import get_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'job_posting_app.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():

        return render_template('client/dashboard/index.html')
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import applicant
    app.register_blueprint(applicant.bp)
    
    return app