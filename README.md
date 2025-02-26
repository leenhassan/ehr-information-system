# EHR Information System  
An Electronic Health Records (EHR) system designed to help doctors manage patient records efficiently.  
This project ensures secure patient data management, GDPR compliance, and improved healthcare workflow.  

## 🚀 Features  
✔️ Secure Registration & Login – Doctors can register, log in, and manage their accounts.  
✔️ Patient Management – Add, edit, view, and delete patient records.  
✔️ ICD-10 Converter – Helps doctors quickly find medical codes.  
✔️ Appointment Scheduling – Doctors can schedule and manage appointments.  
✔️ PDF Report Generation – Export patient data and records.  
✔️ User Roles & Authentication – Only authorized doctors can access records.  
✔️ Security & GDPR Compliance – Data encryption and access control ensure patient privacy.  

## 🔧 Tech Stack  
🔹 **Frontend:** HTML5, CSS3, Bootstrap  
🔹 **Backend:** Python (Flask), Flask-Login, Flask-SQLAlchemy  
🔹 **Database:** MySQL  
🔹 **Security:** Flask-Login (for authentication), GDPR-compliant encryption  
🔹 **Additional Libraries:** Jinja2, PyMySQL, Flask-Mail (for email verification)  
## 🛠 Installation Guide  

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/leenhassan/ehr-information-system.git
cd ehr-information-system

### ⚠️ **Important Note**

To avoid dependency issues, it's recommended to use a **virtual environment** before installing requirements.

Run these commands:
```bash
python -m venv env
source env/bin/activate  # For macOS/Linux
env\Scripts\activate  # For Windows

2️⃣ Install dependencies

pip install -r backend/requirements.txt

3️⃣ Run the application

python backend/run.py

4️⃣ Open in browser

http://localhost:5000




