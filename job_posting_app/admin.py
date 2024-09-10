import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.exceptions import abort

from .auth import login_required

from job_posting_app.db import get_db

bp = Blueprint('admin', __name__)


@bp.route("/admin",)
@login_required
def admin():
    user_id = int(session['user_id'])
    db = get_db()
    result = db.execute("SELECT COUNT(*) FROM jobs").fetchone()
    number_of_jobs = result[0]
    jobs = db.execute("SELECT * FROM jobs WHERE company_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    db.close()
    return render_template('admin/index.html', jobs=jobs, number_of_jobs=number_of_jobs)



@bp.route("/admin/jobs", methods=['GET', 'POST'])
@login_required
def add_job():
    if request.method == 'POST':
        job_name = request.form['job_name']
        job_level = request.form['job_level']
        job_description = request.form['job_description']
        company_id = session['user_id']
        db = get_db()

        try:
            db.execute(
                """INSERT INTO jobs (job_name, job_level, job_description, company_id) VALUES (?, ?, ?, ?)""",
                (job_name, job_level, job_description, company_id))
            db.commit()
        except:
            pass
        else:
            return redirect(url_for('admin.admin'))
        
    return render_template('admin/add_form.html')
    
        
def get_job(id):
    job = get_db().execute("SELECT * FROM jobs INNER JOIN users ON users.id = jobs.company_id WHERE jobs.company_id = ?", (id,)).fetchone()

    return job


@bp.route("/admin/job/<int:id>/edit", methods=('GET', 'POST'))
def update(id):
    job = get_job(id)

    if request.method == 'POST':
        job_name = request.form['job_name']
        job_level = request.form['job_level']
        job_description = request.form['job_description']
        error = None


        if not job_name:
            error = 'Job name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("UPDATE jobs SET job_name = ?, job_level = ?, job_description = ? WHERE company_id = ?", (job_name, job_level, job_description, id))
            db.commit()
            # return str(id)
            return redirect(url_for('admin.admin'))

    return render_template('/admin/edit_form.html', job=job)



@bp.route("/admin/<int:id>/delete", methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    db.execute("DELETE FROM jobs WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('admin.admin'))

