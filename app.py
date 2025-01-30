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
from PIL import Image  # For image processing

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

# customize the PDF
def generate_pdf(form_data, file_paths):
    print("Generating PDF...")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set font for the entire document
    pdf.set_font("Arial", size=12)
    
    # Add logo with specific width and height, centered
    logo_width = 70
    logo_height = 30
    pdf.image('logoc.png', x=(pdf.w - logo_width) / 2, y=10, w=logo_width, h=logo_height)
    
    # Add section with company information (left-aligned)
    pdf.ln(30)  # Move below the logo (reduced spacing)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, txt="American Pharmaceutical Distributors", ln=True, align='L')  # Reduced cell height
    pdf.cell(0, 5, txt="123 Main Street, Suite 456", ln=True, align='L')
    pdf.cell(0, 5, txt="City, State, ZIP Code", ln=True, align='L')
    pdf.cell(0, 5, txt="Email: info@americanapd.com", ln=True, align='L')
    pdf.cell(0, 5, txt="Phone: (123) 456-7890", ln=True, align='L')
    
    # Add PDF title (centered and bold)
    pdf.ln(8)  # Reduced spacing
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(0, 10, txt="Registration Form Details", ln=True, align='C')
    
    # Add section with submission details (left-aligned)
    pdf.ln(8)  # Reduced spacing
    pdf.set_font("Arial", size=10)
    submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pdf.cell(0, 5, txt=f"Submitted on: {submission_time}", ln=True, align='L')
    pdf.cell(0, 5, txt=f"Submitted from IP Address: {request.remote_addr}", ln=True, align='L')
    
    # Add table with 2 columns (Field, Value)
    pdf.ln(8)  # Reduced spacing
    pdf.set_fill_color(200, 220, 255)  # Light blue background for header
    pdf.set_font("Arial", 'B', size=10)
    pdf.cell(95, 8, "Field", border=1, fill=True)  # Reduced cell height
    pdf.cell(95, 8, "Value", border=1, fill=True, ln=1)
    
    # Table body
    pdf.set_font("Arial", size=10)
    pdf.set_fill_color(240, 240, 240)  # Light gray background for body
    items = list(form_data.items()) + [(k, os.path.basename(v)) for k, v in file_paths.items()]
    for key, value in items:
        pdf.cell(95, 8, txt=key.capitalize(), border=1, fill=True)  # Reduced cell height
        pdf.cell(95, 8, txt=str(value).capitalize(), border=1, fill=True, ln=1)
    
    # Add footer (left-aligned)
    pdf.ln(8)  # Reduced spacing
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, txt="Uploaded Files:", ln=True, align='L')
    for file_path in file_paths.values():
        pdf.cell(0, 5, txt=os.path.basename(file_path), ln=True, align='L')
    
    # Add signature and copyright
    pdf.ln(8)  # Reduced spacing
    owner_name = form_data.get("ownerName")  # Get the name from form_data
    pdf.cell(0, 5, txt=f"I, {owner_name}, agree to the terms and conditions set forth in this document.", ln=True, align='L')
    pdf.set_font("Arial", 'I', size=10)  # Set font to italic for signature
    pdf.cell(0, 5, txt=f"Signature: {owner_name}", ln=True, align='L')
    pdf.set_font("Arial", size=10)  # Reset font to regular
    pdf.cell(0, 5, txt="Date: 01/21/2025", ln=True, align='L')
    pdf.cell(0, 5, txt="© 2025 American Pharmaceutical Distributors. All rights reserved.", ln=True, align='L')
    
    # Save the PDF
    pdf_filename = f"uploads/registration_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(pdf_filename)
    print(f"PDF saved to: {pdf_filename}")
    return pdf_filename


@app.route('/')
def home():
    return render_template('index.html')


# Function to convert an image to PDF
def convert_image_to_pdf(image_path, pdf_path):
    img = Image.open(image_path)
    pdf = FPDF(unit="pt", format=[img.width, img.height])
    pdf.add_page()
    pdf.image(image_path, 0, 0, img.width, img.height)
    pdf.output(pdf_path)

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
        pdf_paths = []  # To store paths of all PDFs (main + image-converted PDFs)
        
        # Save uploaded files and convert images to PDFs
        for key, file in files.items():
            # Generate a unique filename using UUID
            unique_id = str(uuid.uuid4())[:8]  # Use the first 8 characters of a UUID
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{unique_id}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_paths[key] = file_path
            
            # Convert image to PDF if the file is an image
            if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                convert_image_to_pdf(file_path, pdf_path)
                pdf_paths.append(pdf_path)
        
        # Generate the main registration PDF
        main_pdf_path = generate_pdf(form_data, file_paths)
        pdf_paths.append(main_pdf_path)
        
        # Save registration data to the database
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
        
        # Send email with all PDFs attached
        msg = Message(
            "New Registration Submission", 
            sender=os.getenv('MAIL_USERNAME'), 
            recipients=["softdev.alamin@gmail.com", "alaminprogramerr@gmail.com"]
            # recipients=["info@americanapd.com", "aramouni@americanapd.com"]
        )
        msg.body = "A new customer has submitted their registration form. The details are attached."

        # Attach all PDFs
        for pdf_path in pdf_paths:
            with open(pdf_path, 'rb') as pdf_file:
                msg.attach(filename=os.path.basename(pdf_path), content_type="application/pdf", data=pdf_file.read())
        
        mail.send(msg)
        
        return jsonify({"message": "Registration successful and email sent"}), 200
    except Exception as e:
        print(e)
        print(str(e))
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
