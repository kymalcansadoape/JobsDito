import functools
import os
from flask import ( Blueprint, flash, g, redirect, render_template, request, session, url_for,)
from werkzeug.exceptions import abort
from fileinput import filename
from .auth import login_required, applicant_middleware
from job_posting_app.db import get_db

bp = Blueprint("applicant", __name__)


@bp.route("/profile/<int:id>", methods=("GET", "POST"))
@login_required
@applicant_middleware
def applicant_profile(id):

    applicant = get_applicant(id)

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']
        years_of_experience = request.form['years_of_experience']

        resume_file = request.files['resume']
        resume_folder = 'resumes'

        if not first_name or first_name == '':
            flash("First name required.")
        if not last_name or last_name == '':
            flash("Last name required.")
        if not location or location == '':
            flash("Location required.")
        if not years_of_experience or years_of_experience == '':
            flash("Experience level required.")
        if not resume_file or resume_file.filename == '':
            flash("Resume is required!", "error")
            return redirect(request.url)

        resume_name = os.path.join(resume_folder, resume_file.filename)
        
        if not os.path.exists(resume_folder):
            os.makedirs(resume_folder)
        if applicant['resume_path'] is None or applicant['resume_path'] == '':
            resume_file.save(resume_name)
        else:
            if os.path.exists(applicant['resume_path']):
                os.remove(applicant['resume_path'])
            resume_file.save(resume_name) 

        db = get_db()
        db.execute(
            """UPDATE applicant SET first_name = ?, last_name = ?, location = ?, resume_path = ?, years_of_experience = ? WHERE user_id = ?""",
            (first_name, last_name, location, resume_name, years_of_experience, id),
        )
        db.commit()
        flash("You successfully setup your profile!", "success")
        return redirect(url_for("applicant.applicant_profile", id=id))
    
    return render_template("client/applicant/index.html", applicant=applicant)


def get_applicant(id):
    applicant = (get_db().execute("SELECT * FROM applicant INNER JOIN users ON users.id = applicant.user_id WHERE user_id = ?",(id,),).fetchone())
    print(id)
    return applicant


@bp.route("/apply_job/<int:job_id>/applicant/<int:applicant_id>", methods=["GET", "POST"])
@login_required
@applicant_middleware
def apply_job(job_id, applicant_id):
    db = get_db()

    applicant = db.execute("SELECT * FROM applicant WHERE user_id = ?", (applicant_id,)).fetchone()

    if applicant['first_name'] == None or applicant['resume_path'] == None:
        flash("Need to setup profile.", "error")
    else:
        db.execute(
            "INSERT INTO applications (applicant_id, job_id) VALUES (?, ?)",
            (applicant_id, job_id),
        )
        db.commit()
        
        # flash('Applied Succesfully.' 'success')
    return redirect(url_for("jobs"))


@bp.route("/profile/application_list")
@login_required
@applicant_middleware
def application_list():
    id = session["user_id"]
    db = get_db()

    result = db.execute("SELECT COUNT(*) FROM applications WHERE applications.applicant_id = ?", (id,)).fetchone()

    number_of_applications = result[0]
    application_list = db.execute(
        """SELECT * FROM applications INNER JOIN jobs ON jobs.id = applications.job_id 
        INNER JOIN applicant ON applicant.id = applications.applicant_id WHERE applications.applicant_id = ?""",(id,),).fetchall()

    return render_template(
        "client/applicant/application_list.html", application_list=application_list, number_of_applications=number_of_applications)

