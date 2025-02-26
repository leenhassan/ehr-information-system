from io import BytesIO
from tkinter import Image
from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash, current_app
from flask_login import current_user
from app.models import db, Doctor, Patient  # Import your models
from app.utils import generate_verification_token, send_verification_email, confirm_verification_token
import os
import logging
from flask_mail import Message
from app import mail
from app.utils import get_icd_codes
from flask import jsonify
from flask_login import login_user
from flask_login import login_required
from flask import make_response
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.pdfgen import canvas # type: ignore
import os
from PIL import Image




from app.models import Doctor
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(int(user_id))  # Assuming `id` is the primary key for `Doctor`

main = Blueprint('main', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            # Get form data
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            doctor_id = request.form.get("doctor_id")
            department = request.form.get("department")
            status = request.form.get("status")
            email = request.form.get("email")
            password = request.form.get("password")
            hospital_name = request.form.get("hospital_name")

            logger.debug("Received registration data.")

            # Validate required fields
            if not all([first_name, last_name, doctor_id, department, status, email, password, hospital_name]):
                flash("All fields are required.", "danger")
                return redirect(url_for("main.register"))

            # Check for existing doctor_id or email
            if Doctor.query.filter_by(doctor_id=doctor_id).first():
                flash("Doctor ID already exists. Please use a different ID.", "danger")
                return redirect(url_for("main.register"))

            if Doctor.query.filter_by(email=email).first():
                flash("Email already registered. Please use a different email.", "danger")
                return redirect(url_for("main.register"))
            logger.debug("Attempting to add new doctor to the database.")
            # Create new doctor object
            new_doctor = Doctor(
                first_name=first_name,
                last_name=last_name,
                doctor_id=doctor_id,
                department=department,
                status=status,
                email=email,
                password=password,
                hospital_name=hospital_name
            )

            # Save to the database
            logger.debug("Adding doctor to the database.")
            db.session.add(new_doctor)
            db.session.flush() 
            logger.debug("Committing the session.")
            db.session.commit()

            # Send verification email
            logger.debug("Attempting to send verification email.")
            token = generate_verification_token(email)
            verification_url = url_for('main.verify_email', token=token, _external=True)
            logger.debug(f"Verification URL: {verification_url}")

            send_verification_email(email, verification_url)

            flash("Registration successful! Please check your email for verification.", "success")
            return redirect(url_for("main.verification_sent"))
        

        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for("main.verification_error"))

    return render_template("register.html")

@main.route('/verify_email/<token>')
def verify_email(token):
    try:
        logger.debug(f"Token received: {token}")
        email = confirm_verification_token(token)
        logger.debug(f"Email decoded from token: {email}")
        if not email:
            flash("The verification link is invalid or has expired.", "danger")
            return redirect(url_for("main.register"))

        doctor = Doctor.query.filter_by(email=email).first()
        if doctor:
            doctor.is_verified = True
            db.session.commit()
            flash("Your email has been verified. You can now log in.", "success")
            return redirect(url_for("main.login"))
        else:
            flash("Verification failed. Doctor not found.", "danger")
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        flash("An error occurred during email verification.", "danger")

    return redirect(url_for("main.register"))

@main.route("/verification_sent")
def verification_sent():
    return render_template("verification_sent.html")

@main.route("/verification_error")
def verification_error():
    return render_template("verification_error.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if the doctor exists
        doctor = Doctor.query.filter_by(email=email).first()

        if doctor and doctor.password == password:
            login_user(doctor)  # Simple password check for now
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))  # Redirect to dashboard
        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")
from flask_login import logout_user

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/help")
def help_page():
    return render_template("help.html")

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_authenticated:
        flash("Please log in to access your profile.", "danger")
        return redirect(url_for('main.login'))

    doctor = Doctor.query.filter_by(email=current_user.email).first()

    if request.method == 'POST':
        # Update doctor data from form inputs
        doctor.first_name = request.form['first_name']
        doctor.last_name = request.form['last_name']
        doctor.department = request.form['department']
        doctor.status = request.form['status']
        doctor.hospital_name = request.form['hospital_name']

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")

    return render_template('profile.html', doctor=doctor)

@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if not current_user.is_authenticated:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('main.login'))

    doctor = Doctor.query.filter_by(email=current_user.email).first()

    if request.method == 'POST':
        # Update the doctor's data from the form
        doctor.first_name = request.form['first_name']
        doctor.last_name = request.form['last_name']
        doctor.department = request.form['department']
        doctor.status = request.form['status']
        doctor.hospital_name = request.form['hospital_name']

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating your profile: {str(e)}", "danger")

    return render_template('edit_profile.html', doctor=doctor)

# Manage Patients route

# Add Patient route
@main.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        nationality = request.form['nationality']
        gender = request.form['gender']
        medical_history = request.form.get('medical_history', '')
        ops_title = request.form.get('ops_title', '')
        symptoms = request.form.get('symptoms', '')
        signs = request.form.get('signs', '')
        days_of_hospitalization = request.form.get('days_of_hospitalization', None)

        # Handle radiology image upload
        radiology_image = request.files.get('radiology_image')
        radiology_image_path = None
        if radiology_image and radiology_image.filename:
            upload_dir = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
            saved_path = os.path.join(upload_dir, radiology_image.filename)
            radiology_image.save(saved_path)
            radiology_image_path = f'uploads/{radiology_image.filename}'  # Save relative path

        # Create new patient
        new_patient = Patient(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            nationality=nationality,
            gender=gender,
            medical_history=medical_history,
            ops_title=ops_title,
            symptoms=symptoms,
            signs=signs,
            days_of_hospitalization=days_of_hospitalization,
            radiology_image=radiology_image_path,
            doctor_id=current_user.id
        )

        try:
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('main.manage_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding patient: {str(e)}', 'danger')

    return render_template('add_patient.html')


    # Render the form to add a patient
    return render_template('add_patient.html', icd_codes=icd_codes)
@main.route('/manage_patients', methods=['GET', 'POST'])
@login_required
def manage_patients():
    search_query = request.args.get('search', '')
    if search_query:
        patients = Patient.query.filter(
            (Patient.first_name.ilike(f"%{search_query}%")) |
            (Patient.last_name.ilike(f"%{search_query}%")),
            Patient.doctor_id == current_user.id  # Fetch only current doctor's patients
        ).all()
    else:
        patients = Patient.query.filter_by(doctor_id=current_user.id).all()  # Fetch all patients for the doctor

    return render_template('manage_patients.html', patients=patients)

@main.route('/search_patients', methods=['GET'])
@login_required
def search_patients():
    search_query = request.args.get('search', '')
    return redirect(url_for('main.manage_patients', search=search_query))

@main.route('/icd_converter', methods=['GET', 'POST'])
def icd_converter():
    icd_codes = []
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        if search_term:
            result = get_icd_codes(search_term, max_results=10)
            if result:
                icd_codes = result['icd_codes']
    return render_template('icd_converter.html', icd_codes=icd_codes)

@main.route('/get_icd_suggestions', methods=['GET'])
def get_icd_suggestions():
    search_term = request.args.get('search_term', '').strip()
    if not search_term:
        return jsonify([])  # Return empty list if no search term

    result = get_icd_codes(search_term, max_results=10)
    if result:
        return jsonify(result['icd_codes'])  # Return the list of ICD codes
    return jsonify([])

# Delete Patient route
@main.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    try:
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting patient: {str(e)}', 'danger')
    return redirect(url_for('main.manage_patients'))

@main.route('/view_patient/<int:patient_id>', methods=['GET'])
@login_required
def view_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id, doctor_id=current_user.id).first()
    if not patient:
        flash('You do not have permission to view this patient.', 'danger')
    # Split the ICD codes into a list for display
    icd_codes = patient.icd_title.split(',') if patient.icd_title else []
    return render_template('view_patient.html', patient=patient, icd_codes=icd_codes)

# Edit Patient route
@main.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    icd_codes = []

    if request.method == 'POST':
        # Update patient data from the form
        patient.first_name = request.form['first_name']
        patient.last_name = request.form['last_name']
        patient.dob = request.form['dob']
        patient.nationality = request.form['nationality']
        patient.gender = request.form['gender']
        patient.medical_history = request.form.get('medical_history', '')
        patient.ops_title = request.form.get('ops_title', '')
        patient.symptoms = request.form.get('symptoms', '')
        patient.signs = request.form.get('signs', '')
        patient.days_of_hospitalization = request.form.get('days_of_hospitalization', None)

        # Handle selected ICD codes
        previous_icds = request.form.get('previous_icds', '')  # Retrieve previous ICDs from hidden input
        selected_icds = request.form.getlist('selected_icds')  # Get new ICD codes from checkboxes
        all_icds = set(previous_icds.split(',')) | set(selected_icds)  # Merge old and new codes
        patient.icd_title = ','.join(filter(None, all_icds))  # Save as comma-separated values

        radiology_image = request.files.get('radiology_image', None)
        if radiology_image:
            upload_dir = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
            radiology_image_path = os.path.join('static/uploads', radiology_image.filename)
            radiology_image.save(os.path.join(current_app.root_path, radiology_image_path))
            patient.radiology_image = radiology_image_path

        try:
            db.session.commit()
            flash('Patient updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')

        return redirect(url_for('main.manage_patients'))

    # Fetch ICD recommendations if a search term is provided
    search_term = request.args.get('icd_search', '').strip()
    if search_term:
        result = get_icd_codes(search_term, max_results=10)
        if result:
            icd_codes = result['icd_codes']

    # Pass existing ICD codes to the template
    previous_icds = patient.icd_title if patient.icd_title else ''

    # Pass patient and ICD codes to the template
    return render_template('edit_patient.html', patient=patient, icd_codes=icd_codes, previous_icds=previous_icds)

@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Collect form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        
        # Validate and process the data
        if not name or not email or not message:
            flash("All fields are required!", "danger")
            return redirect(url_for("main.contact"))
        
        # Send email using Flask-Mail
        try:
            msg = Message(
                subject=f"New Contact Form Submission from {name}",
                sender=email,
                recipients=["dija.aa1714@gmail.com"],  # Replace with your receiving email
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            print(f"Error sending email: {e}")
            flash("There was an error sending your message. Please try again later.", "danger")
            return redirect(url_for("main.contact"))
        
        return redirect(url_for("main.contact"))

    # Render the contact page
    return render_template("contact.html")
from flask import render_template, session, flash, redirect, url_for, jsonify, request
from app.models import Appointment
from datetime import datetime
from app import db



@main.route('/schedule')
@login_required
def schedule():
    """
    Render the schedule page where doctors can view and manage their appointments.
    """
    return render_template('schedule.html')


@main.route('/appointments', methods=['GET'])
def get_appointments():
    """
    Fetch appointments for the selected year and month.
    """
    year = request.args.get('year')
    month = request.args.get('month')

    if not year or not month:
        return jsonify({'error': 'Year and month are required parameters.'}), 400

    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return jsonify({'error': 'Year and month must be integers.'}), 400

    appointments = Appointment.query.filter(
        db.extract('year', Appointment.date) == year,
        db.extract('month', Appointment.date) == month
    ).all()

    return jsonify([{
        'id': a.id,
        'title': a.title,
        'day': a.date.day,
        'time': a.time.strftime('%H:%M') if a.time else None
    } for a in appointments])


@main.route('/appointments/add', methods=['POST'])
def add_appointment():
    """
    Add a new appointment for the schedule.
    """
    data = request.json
    try:
        appointment = Appointment(
            title=data['title'],
            date=datetime.strptime(f"{data['year']}-{data['month']}-{data['day']}", '%Y-%m-%d'),
            time=datetime.strptime(data['time'], '%H:%M').time()
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment added successfully', 'id': appointment.id}), 201
    except KeyError as e:
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'Invalid date or time format: {str(e)}'}), 400


@main.route('/appointments/edit/<int:appointment_id>', methods=['POST'])
def edit_appointment(appointment_id):
    """
    Edit an existing appointment.
    """
    data = request.json
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    try:
        appointment.title = data['title']
        appointment.time = datetime.strptime(data['time'], '%H:%M').time()
        db.session.commit()
        return jsonify({'message': 'Appointment updated successfully'})
    except ValueError as e:
        return jsonify({'error': f'Invalid time format: {str(e)}'}), 400


@main.route('/appointments/delete/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    """
    Delete an appointment.
    """
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted successfully'})

@main.route('/download_patient_data/<int:patient_id>', methods=['GET'])
def download_patient_data(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Create a BytesIO object to save the PDF in memory
    pdf_buffer = BytesIO()

    # Create a canvas object and set the page size
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setTitle(f"Patient Data - {patient.first_name} {patient.last_name}")

    # Write patient data into the PDF
    y_position = 750  # Starting Y position for text
    line_spacing = 20  # Space between lines

    pdf.drawString(50, y_position, f"Patient Details:")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"First Name: {patient.first_name}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Last Name: {patient.last_name}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Date of Birth: {patient.dob}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Nationality: {patient.nationality}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Gender: {patient.gender}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Medical History: {patient.medical_history}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"ICD Codes: {patient.icd_title}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Procedures: {patient.ops_title or 'N/A'}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Symptoms: {patient.symptoms}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Signs: {patient.signs}")
    y_position -= line_spacing
    pdf.drawString(50, y_position, f"Days of Hospitalization: {patient.days_of_hospitalization}")
    y_position -= line_spacing

    # Add radiology image if available
    if patient.radiology_image:
        image_path = os.path.join(current_app.root_path, 'static', patient.radiology_image)
        if os.path.exists(image_path):
            y_position -= 40  # Add extra space before displaying the image
            try:
                img = Image.open(image_path)
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width
                img_display_width = 200  # Fixed display width
                img_display_height = img_display_width * aspect_ratio

                # Check if there's enough space to display the image on the current page
                if y_position - img_display_height < 50:  # Minimum space from the bottom
                    pdf.showPage()  # Move to a new page
                    y_position = 750  # Reset Y position for the new page

                pdf.drawImage(
                    image_path, 50, y_position - img_display_height,
                    width=img_display_width, height=img_display_height
                )
                y_position -= img_display_height + 10  # Adjust position after displaying the image
            except Exception as e:
                pdf.drawString(50, y_position, f"Error loading image: {str(e)}")
                y_position -= line_spacing
        else:
            pdf.drawString(50, y_position, "Radiology Image: Not Found")
            y_position -= line_spacing
    else:
        pdf.drawString(50, y_position, "Radiology Image: Not Available")
        y_position -= line_spacing

    # Save the PDF to the BytesIO buffer
    pdf.save()

    # Set the buffer's position to the beginning
    pdf_buffer.seek(0)

    # Send the PDF file as a response
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Patient_{patient.first_name}_{patient.last_name}.pdf",
        mimetype="application/pdf"
    )

@main.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if doctor.id != current_user.id:
        flash("You are not authorized to delete this account.", "danger")
        return redirect(url_for('main.profile'))

    try:
        db.session.delete(doctor)
        db.session.commit()
        logout_user()
        flash("Your account has been deleted successfully.", "success")
        return redirect(url_for('main.home'))
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting your account: {e}", "danger")
        return redirect(url_for('main.profile'))
