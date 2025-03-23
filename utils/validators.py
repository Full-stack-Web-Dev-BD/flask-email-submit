from functools import wraps
from flask import request, jsonify

def validate_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        required_fields = [
            'cutting_line', 'surface_area', 'dimensions', 'closed_loops', 
            'quantity', 'material_name', 'thickness', 'file_url'
        ]
        data = request.json

        # Check if data is provided
        if not data:
            return jsonify({'error': 'Missing JSON payload'}), 400

        # Validate required fields
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return jsonify({'error': f"Missing required fields: {', '.join(missing_fields)}"}), 400

        return f(*args, **kwargs)
    return decorated_function
