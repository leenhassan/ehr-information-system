from app import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    doctor_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    hospital_name = db.Column(db.String(100), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    patients = db.relationship('Patient', back_populates='doctor', cascade='all, delete-orphan')



class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    medical_history = db.Column(db.Text, nullable=False)
    icd_title = db.Column(db.Text, nullable=True)
    ops_title = db.Column(db.Text, nullable=True)
    symptoms = db.Column(db.Text, nullable=False)
    signs = db.Column(db.Text, nullable=False)
    days_of_hospitalization = db.Column(db.Integer, nullable=False)
    radiology_image = db.Column(db.String(200), nullable=True)
        # Foreign key to link each patient to a specific doctor
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    # Relationship to the Doctor model
    doctor = relationship('Doctor', back_populates='patients')

from datetime import datetime
from app import db

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)


    def __repr__(self):
        return f"<Appointment {self.title} on {self.date} at {self.time}>"
