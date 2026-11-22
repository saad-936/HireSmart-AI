
import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from werkzeug.utils import secure_filename

from app.database import get_db
from ai_engine.resume_parser import extract_resume_text
from ai_engine.resume_matcher import extract_skills, calculate_match


main = Blueprint("main", __name__)


# Dashboard
@main.route("/")
def home():
    connection = get_db()

    total_jobs = connection.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        total_jobs=total_jobs
    )


# Job Management
@main.route("/jobs", methods=["GET", "POST"])
def jobs():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        department = request.form.get("department", "").strip()
        location = request.form.get("location", "").strip()
        job_type = request.form.get("job_type", "").strip()
        description = request.form.get("description", "").strip()
        required_skills = request.form.get("required_skills", "").strip()
        qualification = request.form.get("qualification", "").strip()

        if not title or not description or not required_skills:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("main.jobs"))

        connection = get_db()

        connection.execute("""
            INSERT INTO jobs
            (title, department, location, job_type, description,
             required_skills, qualification)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            title, department, location, job_type,
            description, required_skills, qualification
        ))

        connection.commit()
        connection.close()

        flash("Job successfully created!", "success")
        return redirect(url_for("main.jobs"))

    connection = get_db()

    jobs_list = connection.execute(
        "SELECT * FROM jobs ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template("jobs.html", jobs=jobs_list)


# Resume Screening
@main.route("/resume-screening", methods=["GET", "POST"])
def resume_screening():

    connection = get_db()

    jobs_list = connection.execute(
        "SELECT * FROM jobs ORDER BY id DESC"
    ).fetchall()

    connection.close()

    if request.method == "POST":

        file = request.files.get("resume")
        job_id = request.form.get("job_id")

        if not file or file.filename == "":
            flash("Please select a PDF resume.", "error")
            return render_template(
                "resume_screening.html",
                jobs=jobs_list
            )

        if not file.filename.lower().endswith(".pdf"):
            flash("Only PDF files are allowed.", "error")
            return render_template(
                "resume_screening.html",
                jobs=jobs_list
            )

        # Vercel uses temporary storage; local app uses uploads/
        if os.getenv("VERCEL"):
            upload_folder = "/tmp/uploads"
        else:
            upload_folder = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "uploads"
            )

        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)

        file.save(file_path)

        extracted_text = extract_resume_text(file_path)

        if not extracted_text:
            flash("Could not extract text from this PDF.", "error")
            return render_template(
                "resume_screening.html",
                jobs=jobs_list
            )

        resume_skills = extract_skills(extracted_text)
        matching_result = None

        if job_id:

            connection = get_db()

            selected_job = connection.execute(
                "SELECT * FROM jobs WHERE id = ?",
                (job_id,)
            ).fetchone()

            connection.close()

            if selected_job:

                job_text = (
                    selected_job["title"] + " " +
                    selected_job["description"] + " " +
                    selected_job["required_skills"]
                )

                matching_result = calculate_match(
                    extracted_text,
                    job_text
                )

        flash(
            "Resume uploaded and analyzed successfully!",
            "success"
        )

        return render_template(
            "resume_screening.html",
            extracted_text=extracted_text,
            resume_skills=resume_skills,
            matching_result=matching_result,
            jobs=jobs_list,
            selected_job_id=job_id
        )

    return render_template(
        "resume_screening.html",
        jobs=jobs_list
    )
