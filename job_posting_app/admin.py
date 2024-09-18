import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)

from werkzeug.exceptions import abort

from .auth import login_required, admin_middleware

from job_posting_app.db import get_db

bp = Blueprint('admin', __name__)


@bp.route("/admin",)
@login_required
@admin_middleware
def admin():
    user_id = int(session['user_id'])
    db = get_db()
    result = db.execute("SELECT COUNT(*) FROM jobs").fetchone()
    number_of_jobs = result[0]
    jobs = db.execute("SELECT * FROM jobs WHERE company_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    number_of_applicants_result = db.execute("""SELECT COUNT(*) FROM applications INNER JOIN jobs ON jobs.id = applications.job_id  INNER JOIN company ON company.id = jobs.company_id WHERE company.user_id = ?""", (user_id,)).fetchone()
    number_of_applicants = number_of_applicants_result[0]
    recent_applicants = db.execute("""SELECT * FROM applications
                                    LEFT JOIN applicant ON applications.applicant_id = applicant.id
                                    LEFT JOIN jobs ON applications.job_id = jobs.id
                                    LEFT JOIN company ON jobs.company_id = company.id WHERE company.id = ? ORDER BY created_at DESC""", (user_id,)).fetchall()
    db.close()

    return render_template('admin/index.html', jobs=jobs, number_of_jobs=number_of_jobs, number_of_applicants=number_of_applicants)


@bp.route("/admin_profile")
@login_required
def admin_profile():
    return render_template('admin/profile.html')



@bp.route("/admin/jobs", methods=['GET', 'POST'])
@login_required
@admin_middleware
def add_job():
    if request.method == 'POST':
        job_name = request.form['job_name']
        job_location = request.form['job_location']
        job_level = request.form['job_level']
        job_description = request.form['job_description']
        company_id = session['user_id']
        db = get_db()

        try:
            db.execute(
                """INSERT INTO jobs (job_name, job_location,job_level, job_description, company_id) VALUES (?, ?, ?, ?, ?)""",
                (job_name, job_location, job_level, job_description, company_id))
            db.commit()
        except:
            pass
        else:
            return redirect(url_for('admin.admin'))
        
    return render_template('admin/add_form.html')
    
        
def get_job(id):
    job = get_db().execute("SELECT * FROM jobs INNER JOIN users ON users.id = jobs.company_id WHERE jobs.id = ?", (id,)).fetchone()

    return job


@bp.route("/admin/job/<int:id>/edit", methods=('GET', 'POST'))
@login_required
@admin_middleware
def update(id):
    job = get_job(id)

    if request.method == 'POST':
        job_name = request.form['job_name']
        job_level = request.form['job_level']
        job_location = request.form['job_location']
        job_description = request.form['job_description']
        error = None


        if not job_name:
            error = 'Job name is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("UPDATE jobs SET job_name = ?, job_level = ?, job_description = ?, job_location = ? WHERE id = ?", (job_name, job_level, job_description, job_location, id))
            db.commit()
            # return str(id)
            return redirect(url_for('admin.admin'))

    return render_template('/admin/edit_form.html', job=job)

@bp.route("/admin/<int:id>/delete", methods=('POST',))
@login_required
@admin_middleware
def delete(id):
    db = get_db()
    db.execute("DELETE FROM jobs WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('admin.admin'))

@bp.route('/admin/job/<int:id>')
@login_required
@admin_middleware
def job(id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (id,)).fetchone()
    result = db.execute("SELECT COUNT('applicants') FROM applications WHERE job_id = ?", (id,)).fetchone()
    number_of_applicants = result[0]
    application = db.execute("SELECT * FROM applications WHERE applicant_id = ?", (id,)).fetchone()
    job_applicants = db.execute("SELECT * FROM applications INNER JOIN jobs ON jobs.id = applications.job_id INNER JOIN applicant ON applicant.id = applications.applicant_id WHERE applications.job_id = ?", (id,))
    db.commit()


    return render_template('/admin/job.html', job=job, job_applicants=job_applicants, number_of_applicants=number_of_applicants, application=application)

@bp.route('/update_status/<int:id>/job/<int:job_id>', methods=['GET', 'POST'])
def update_status(id, job_id):
    db = get_db()
    status = request.form['application_status']
    db.execute("UPDATE applications SET status = ? WHERE applicant_id = ?", (status, id))
    db.commit()
    return redirect(url_for('admin.job', id=job_id))

@bp.route("/job/download_resume/<int:id>", methods=['GET', 'POST'])
def download_resume(id):
    db = get_db()
    result = db.execute("SELECT resume_path FROM applicant WHERE id = ?", (id,)).fetchone()  
    resume = f"../{result[0]}"
    return send_file(resume, as_attachment=True)

def get_company(id):
    company = get_db().execute("SELECT * FROM company INNER JOIN users ON users.id = company.user_id WHERE company.user_id = ?", (id,)).fetchone()
    print(id)
    return company

@bp.route('/admin/company_profile/<int:id>', methods=['GET', 'POST'])
def company_profile(id):
    company = get_company(id) 

    if request.method == "POST":
        # Collect form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        company_name = request.form['company_name']
        contact_number = request.form['contact_number']
        email = request.form['email']
        website_url = request.form['website_url']
        description = request.form['description']

        logo_file = request.files['company_logo']
        logo_folder = 'company_logos'

        if not first_name or first_name == '':
            flash("First name required.")
        if not last_name or last_name == '':
            flash("Last name required.")
        if not company_name or company_name == '':
            flash("Company name required.")
        if not contact_number or contact_number == '':
            flash("Contact number required.")
        if not email or email == '':
            flash("Email required.")
        if not website_url or website_url == '':
            flash("Website URL required.")
        if not description or description == '':
            flash("Description required.")
        if not logo_file or logo_file.filename == '':
            flash("Company logo is required!", "error")
            return redirect(request.url)

        logo_name = os.path.join(logo_folder, logo_file.filename)

        if not os.path.exists(logo_folder):
            os.makedirs(logo_folder)

        if company['company_logo'] is None or company['company_logo'] == '':
            logo_file.save(logo_name)
        else:
            if os.path.exists(company['company_logo']):
                os.remove(company['company_logo'])
            logo_file.save(logo_name)

        db = get_db()
        db.execute(
            """UPDATE company SET first_name = ?, last_name = ?, company_name = ?, contact_number = ?, email = ?, website_url = ?, company_logo = ?, description = ? WHERE id = ?""",
            (first_name, last_name, company_name, contact_number, email, website_url, logo_name, description, id),
        )
        db.commit()

        flash("You successfully updated the company profile!", "success")
        return redirect(url_for("admin.company_profile", id=id, company=company))


    return render_template('admin/profile.html', company=company)



