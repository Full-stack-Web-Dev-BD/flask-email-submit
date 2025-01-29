from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import uuid
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS
from fpdf import FPDF

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'

mail = Mail(app)

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# SQLite database configuration
DATABASE = 'registrations.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def close_db(conn):
    if conn:
        conn.close()

def generate_pdf(form_data, file_paths):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Registration Form Details", ln=True, align='C')
    
    items = list(form_data.items()) + [(k, os.path.basename(v)) for k, v in file_paths.items()]
    half = len(items) // 2
    col1, col2 = items[:half], items[half:]
    
    pdf.set_font("Arial", size=10)
    pdf.cell(95, 10, "Field Name", border=1)
    pdf.cell(95, 10, "Value", border=1, ln=1)
    
    for left, right in zip(col1, col2):
        pdf.cell(95, 10, f"{left[0]}: {left[1]}", border=1)
        pdf.cell(95, 10, f"{right[0]}: {right[1]}", border=1, ln=1)
    
    if len(col1) > len(col2):
        pdf.cell(95, 10, f"{col1[-1][0]}: {col1[-1][1]}", border=1, ln=1)
    
    pdf_filename = f"uploads/registration_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit-registration', methods=['POST'])
def submit_registration():
    conn = None
    try:
        form_data = {key: request.form.get(key, '') for key in request.form}
        files = {key: request.files.get(key) for key in request.files if request.files.get(key) and request.files.get(key).filename}
        
        # Process checkbox fields
        agree_terms = 1 if form_data.get('agreeTerms') == 'on' else 0
        agree_text = 1 if form_data.get('agreeText') == 'on' else 0
        
        file_paths = {}
        for key, file in files.items():
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_paths[key] = file_path
        
        pdf_path = generate_pdf(form_data, file_paths)
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO registrations (
                businessType, companyName, dbaName, gln, shippingAddress, shippingSuite, shippingCity,
                shippingState, shippingZip, phone, fax, email, billingSameAsShipping, billingAddress,
                billingSuite, billingCity, billingState, billingZip, ownerName, secondOwnerName, npiNumber,
                picDriverLicense, stateLicenseNumber, deaLicenseNumber, stateLicenseUpload, deaLicenseUpload,
                agreeTerms, agreeText, signature, signatureDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            form_data.get('businessType', ''), form_data.get('companyName', ''), form_data.get('dbaName', ''),
            form_data.get('gln', ''), form_data.get('shippingAddress', ''), form_data.get('shippingSuite', ''),
            form_data.get('shippingCity', ''), form_data.get('shippingState', ''), form_data.get('shippingZip', ''),
            form_data.get('phone', ''), form_data.get('fax', ''), form_data.get('email', ''),
            form_data.get('billingSameAsShipping', ''), form_data.get('billingAddress', ''), form_data.get('billingSuite', ''),
            form_data.get('billingCity', ''), form_data.get('billingState', ''), form_data.get('billingZip', ''),
            form_data.get('ownerName', ''), form_data.get('secondOwnerName', ''), form_data.get('npiNumber', ''),
            file_paths.get('picDriverLicense', ''), form_data.get('stateLicenseNumber', ''),
            form_data.get('deaLicenseNumber', ''), file_paths.get('stateLicenseUpload', ''), file_paths.get('deaLicenseUpload', ''),
            agree_terms, agree_text,
            form_data.get('signature', ''), form_data.get('signatureDate', '')
        ))
        conn.commit()
        
        msg = Message("New Registration Submission", sender=os.getenv('MAIL_USERNAME'), recipients=[form_data['email']])
        msg.body = "Please find the attached registration details."
        with open(pdf_path, 'rb') as pdf_file:
            msg.attach(filename="registragittion_details.pdf", content_type="application/pdf", data=pdf_file.read())
        mail.send(msg)
        
        return jsonify({"message": "Registration successful and email sent"}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            close_db(conn)


if __name__ == '__main__':
    # Use Heroku's dynamically assigned port
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 for local testing
    app.run(host='0.0.0.0', port=port, debug=True)
