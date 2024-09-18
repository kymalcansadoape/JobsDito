import os

from flask import Flask, render_template, g, session, request
from .auth import applicant_middleware
from job_posting_app.db import get_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "job_posting_app.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return render_template('client/home/index.html')

    @app.route("/jobs", methods=["GET", "POST"])
    def jobs():
        db = get_db()

        search_query = request.args.get("search", "")
        job_level_filter = request.args.get("job_level", "")

        query = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if search_query:
            query += " AND (job_name LIKE ? OR job_description LIKE ?)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param])

        if job_level_filter:
            query += " AND job_level = ?"
            params.append(job_level_filter)

        query += " ORDER BY created_at DESC"
        jobs = db.execute(query, params).fetchall()

        if g.user:
            applied_jobs = db.execute(
                "SELECT job_id FROM applications WHERE applicant_id = ?",
                (session["user_id"],),
            ).fetchall()
            applied_job_ids = [job["job_id"] for job in applied_jobs]
            return render_template(
                "client/dashboard/index.html", jobs=jobs, applied_job_ids=applied_job_ids
            )
        else:
            return render_template("client/dashboard/index.html", jobs=jobs)

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import admin

    app.register_blueprint(admin.bp)

    from . import applicant

    app.register_blueprint(applicant.bp)

    return app
