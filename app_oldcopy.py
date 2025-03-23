import os
from app import create_app
from flask_cors import CORS
from flask import send_from_directory, Flask, render_template

app = create_app()

# Enable CORS for all routes
CORS(app)

# Set absolute path for the upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route to serve uploaded files
@app.route('/')
def index():
    return '<h3 >Welcome to FastCNC! </h3>'

@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# API Route to return server status with HTML templating
@app.route('/api', methods=['GET'])
def api_status():
    # You can include more details here like server health check or uptime
    status = "Server is running smoothly"
    return render_template('status.html', status=status)

if __name__ == '__main__':
    print(f"Serving files from: {UPLOAD_FOLDER}")  # Debugging
    app.run(debug=True)
