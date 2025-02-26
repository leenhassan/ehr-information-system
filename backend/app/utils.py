from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message

# Function to generate a verification token
def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification-salt')

# Function to confirm the verification token
def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-verification-salt',
            max_age=expiration
        )
    except Exception:
        return None
    return email

# Function to send the verification email
def send_verification_email(email, verification_url):
    mail = current_app.extensions.get('mail')  # Access the initialized mail instance
    msg = Message(
        subject='Verify Your Email',
        sender='dija.aa1714@gmail.com',
        recipients=[email]
    )
    msg.body = f'Please click the link to verify your email: {verification_url}'
    mail.send(msg)

import requests

def get_icd_codes(search_term, max_results=7):
    base_url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
    params = {
        "terms": search_term,
        "sf": "code,name",
        "df": "code,name",
        "maxList": max_results,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        # Parse the response
        total_results = data[0]
        codes = data[1]
        descriptions = data[3]

        # Combine codes and descriptions
        icd_codes = [{"code": code, "description": desc[1]} for code, desc in zip(codes, descriptions)]

        return {"total_results": total_results, "icd_codes": icd_codes}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ICD codes: {e}")
        return None
