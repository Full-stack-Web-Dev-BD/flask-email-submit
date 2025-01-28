from flask import Flask, request, jsonify,render_template
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

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
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# SQLite database configuration
DATABASE = 'registrations.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL;')  # Enable WAL mode
    return conn

def close_db(conn):
    if conn:
        conn.close()

def init_db():
    with app.app_context():
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                businessType TEXT NOT NULL,
                companyName TEXT NOT NULL,
                dbaName TEXT,
                gln TEXT,
                shippingAddress TEXT NOT NULL,
                shippingSuite TEXT,
                shippingCity TEXT NOT NULL,
                shippingState TEXT NOT NULL,
                shippingZip TEXT NOT NULL,
                phone TEXT NOT NULL,
                fax TEXT,
                email TEXT NOT NULL,
                billingSameAsShipping TEXT,
                billingAddress TEXT,
                billingSuite TEXT,
                billingCity TEXT,
                billingState TEXT,
                billingZip TEXT,
                ownerName TEXT NOT NULL,
                secondOwnerName TEXT,
                npiNumber TEXT NOT NULL,
                picDriverLicense TEXT NOT NULL,
                stateLicenseNumber TEXT NOT NULL,
                deaLicenseNumber TEXT NOT NULL,
                stateLicenseUpload TEXT NOT NULL,
                deaLicenseUpload TEXT NOT NULL,
                formImage TEXT,
                formPdf TEXT,
                agreeTerms INTEGER NOT NULL,
                agreeText INTEGER NOT NULL,
                signature TEXT NOT NULL,
                signatureDate TEXT NOT NULL
            )
        ''')
        conn.commit()
        close_db(conn)

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit-registration', methods=['POST'])
def submit_registration():
    conn = None
    try:
        # Handle form data and files
        form_data = {key: request.form.get(key) for key in request.form}
        files = {key: request.files.get(key) for key in request.files}

        # Save files and get their paths
        file_paths = {}
        for key, file in files.items():
            if file and allowed_file(file.filename):
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
                filename = f"{timestamp}_{secure_filename(file.filename)}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths[key] = file_path

        # Ensure both attachments are uploaded
        if 'formImage' not in file_paths or 'formPdf' not in file_paths:
            return jsonify({"error": "Both formImage and formPdf files are required"}), 400

        # Insert data into the database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO registrations (
                businessType, companyName, dbaName, gln, shippingAddress, shippingSuite, shippingCity,
                shippingState, shippingZip, phone, fax, email, billingSameAsShipping, billingAddress,
                billingSuite, billingCity, billingState, billingZip, ownerName, secondOwnerName, npiNumber,
                picDriverLicense, stateLicenseNumber, deaLicenseNumber, stateLicenseUpload, deaLicenseUpload,
                formImage, formPdf, agreeTerms, agreeText, signature, signatureDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            form_data['businessType'], form_data['companyName'], form_data['dbaName'], form_data['gln'],
            form_data['shippingAddress'], form_data['shippingSuite'], form_data['shippingCity'],
            form_data['shippingState'], form_data['shippingZip'], form_data['phone'], form_data['fax'],
            form_data['email'], form_data['billingSameAsShipping'], form_data['billingAddress'],
            form_data['billingSuite'], form_data['billingCity'], form_data['billingState'],
            form_data['billingZip'], form_data['ownerName'], form_data['secondOwnerName'],
            form_data['npiNumber'], file_paths.get('picDriverLicense'), form_data['stateLicenseNumber'],
            form_data['deaLicenseNumber'], file_paths.get('stateLicenseUpload'), file_paths.get('deaLicenseUpload'),
            file_paths['formImage'], file_paths['formPdf'],
            1 if form_data.get('agreeTerms') == 'on' else 0,
            1 if form_data.get('agreeText') == 'on' else 0,
            form_data['signature'], form_data['signatureDate']
        ))
        conn.commit()

        # Email the form data
        email_body = f"""
        <h2>Registration Form Submission</h2>
        <ul>
            {''.join([f"<li><strong>{key}:</strong> {value}</li>" for key, value in form_data.items()])}
        </ul>
        """
        msg = Message("New Registration Submission", sender=os.getenv('MAIL_USERNAME'), recipients=[form_data['email']])
        msg.html = email_body

        # Attach the formImage and formPdf files to the email
        with open(file_paths['formImage'], 'rb') as img_file:
            msg.attach(filename="formImage.jpg", content_type="image/jpeg", data=img_file.read())

        with open(file_paths['formPdf'], 'rb') as pdf_file:
            msg.attach(filename="formPdf.pdf", content_type="application/pdf", data=pdf_file.read())

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
    app.run(debug=True)