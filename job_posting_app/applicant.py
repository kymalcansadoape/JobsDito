import functools
import os
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.exceptions import abort
from fileinput import filename
from .auth import login_required
from job_posting_app.db import get_db

bp = Blueprint('applicant', __name__)


@bp.route('/profile/<int:id>', methods=('GET', 'POST'))
def applicant_profile(id):

    applicant = get_applicant(id)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']
        years_of_expercience = request.form['years_of_experience']


        resume_path = request.files['resume']
        resume_name = f'resumes/{resume_path.filename}'

        if applicant['resume_path'] is None or applicant['resume_path'] == '':
            resume_path.save(resume_name)
        else:
            os.remove(applicant['resume_path'])
            resume_path.save(resume_name)


        db = get_db()
        db.execute("""UPDATE applicant SET first_name = ?, last_name = ?, location = ?, resume_path = ? ,  years_of_experience = ?""",  
                    (first_name, last_name, location, resume_name , years_of_expercience))
        db.commit()
        return redirect(url_for('index'))
    return render_template('client/applicant/index.html', applicant=applicant)

def get_applicant(id):
    applicant = get_db().execute("SELECT * FROM applicant INNER JOIN users ON users.id = applicant.user_id WHERE user_id = ?", (id,)).fetchone()
    return applicant
