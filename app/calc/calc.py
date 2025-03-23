from bson import ObjectId
import os
import uuid
import json
from app.calc.dxf.dxfparser import process_dxf_file
from utils.validators import validate_request  # Import the validator
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo import ReturnDocument
from bson.errors import InvalidId




# Load Environment Variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["trustifypro"]  # Database
orders_collection = db["orders"]  # Collection





calc_blueprint = Blueprint('calc', __name__, url_prefix='/calc')

UPLOAD_FOLDER = 'uploads/calc'
CONFIG_PATH = 'app/config/materials.json'  # Path to material pricing JSON
ALLOWED_EXTENSIONS = {'dxf'}


    

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Create Order (POST)
@calc_blueprint.route('/orders', methods=['POST'])
def create_order():
    data = request.json

    # Validate required fields
    if "email" not in data or not data["email"].strip():
        return jsonify({"error": "Email is required"}), 400

    # Insert order
    new_order = {
        "email": data["email"],
        "materialDetails":data.get("materialDetails", {}),
        "city": data.get("city", ""),
        "company": data.get("company", ""),
        "country": data.get("country", {}),
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "postalCode": data.get("postalCode", ""),
        "street": data.get("street", ""),
        "surname": data.get("surname", ""),
        "useVAT": data.get("useVAT", False),
        "vatNumber": data.get("vatNumber", ""),
        "finalized": False  # Order is not finalized yet
    }

    order_id = orders_collection.insert_one(new_order).inserted_id
    new_order["_id"] = str(order_id)

    return jsonify(new_order), 201

@calc_blueprint.route('/orders/finalize/<order_id>', methods=['PUT'])
def finalize_order(order_id):
    data = request.json

    try:
        order_id = ObjectId(order_id)  # Ensure valid ObjectId
    except InvalidId:
        return jsonify({"error": "Invalid Order ID"}), 400

    # Exclude both `_id` and `email` from the update
    update_data = {key: value for key, value in data.items() if key not in ["_id", "email"]}
    update_data["finalized"] = True  # Mark order as finalized

    updated_order = orders_collection.find_one_and_update(
        {"_id": order_id},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER  # Return updated document
    )

    if not updated_order:
        return jsonify({"error": "Order not found"}), 404

    updated_order["_id"] = str(updated_order["_id"])  # Convert ObjectId to string before returning
    return jsonify(updated_order), 200


# 🔹 Find order using both email and order_id
@calc_blueprint.route('/orders/find', methods=['GET'])
def find_order():
    email = request.args.get("email")
    order_id = request.args.get("order_id")

    if not email or not order_id:
        return jsonify({"error": "Both email and order_id are required"}), 400

    try:
        order = orders_collection.find_one({"_id": ObjectId(order_id), "email": email})
        if not order:
            return jsonify({"error": "Order not found"}), 404
        order["_id"] = str(order["_id"])  # Convert ObjectId to string
        return jsonify(order), 200
    except InvalidId:
        return jsonify({"error": "Invalid Order ID"}), 400

    
    
    
    

# Load material pricing from JSON file
def load_materials():
    with open(CONFIG_PATH, 'r') as file:
        return json.load(file)





def calculate_price(dxf_data, material_data_json):
    try:
        # Extract values
        cutting_line = dxf_data['cutting_line']
        closed_loops = dxf_data['closed_loops']
        quantity = int(dxf_data['quantity'])
        material_name = dxf_data['material_name']
        thickness = str(dxf_data['thickness'])
        
        # Get bounding box dimensions (Width, Height)
        width_m = dxf_data['dimensions'][0] / 1000  # Convert mm → meters
        height_m = dxf_data['dimensions'][1] / 1000  # Convert mm → meters
        surface_area_m2 = width_m * height_m  # Corrected surface area calculation
        
        # Fetch material parameters
        material = material_data_json.get(material_name, {})
        params = material.get(thickness, {})
        if not params:
            return {"error": "Invalid material name or thickness"}, 400

        # Convert units
        cutting_line_m = cutting_line / 1000  # Convert mm → meters

        # Extract original cost values
        cost_per_m2 = params['cost_per_m2']
        cost_factor = params['cost_factor']
        loop_cost_per_loop = params['loop_cost']
        setup_price = params['setup_price']


        # Price calculation (strictly as per PDF)

        area_cost = round(surface_area_m2 * cost_per_m2, 2)
        cutting_cost = round(cutting_line_m * cost_factor, 2)
        loop_cost = round(closed_loops * loop_cost_per_loop, 2)
        # Total price per unit
        unit_price = area_cost + cutting_cost + loop_cost
        total_price = round((unit_price * quantity)+setup_price, 2)  # Multiply by quantity

        # Return full cost breakdown
        return {
            "material_name": material_name,
            "thickness": thickness,
            "quantity": quantity,
            "cost_breakdown": {
                "cutting_cost": cutting_cost,
                "loop_cost": loop_cost,
                "surface_area_cost": area_cost,
                "total_price": total_price,
                "price_per_unit": unit_price,
                "setup_price": setup_price
            },
            "original_costs": {
                "cost_per_m2": cost_per_m2,
                "cost_factor": cost_factor,
                "loop_cost_per_loop": loop_cost_per_loop
            }
        }

    except KeyError as e:
        return {"error": f"Missing parameter: {str(e)}"}, 400
    except Exception as e:
        return {"error": str(e)}, 500



@calc_blueprint.route('/update-price', methods=['POST'])
@validate_request
def update_price():
    try:
        data = request.json
        dxf_data = {
            'cutting_line': data['cutting_line'],
            'surface_area': data['surface_area'],
            'dimensions': tuple(data['dimensions']),  # Convert list to tuple
            'closed_loops': data['closed_loops'],
            'quantity': data['quantity'],
            'material_name': data['material_name'],
            'thickness': data['thickness']
        }

        # Load pricing data & calculate price
        materials = load_materials()
        price = calculate_price(dxf_data, materials)

        # Get file URL
        file_url = data['file_url']

        # Return response
        response = {
            'success': True,
            'file_url': file_url,
            'data': dxf_data,
            'price': price
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'dxf'

def convert_dxf_to_svg(filename):
    """ Convert DXF file to SVG and save it in the same directory """
    folder_path = UPLOAD_FOLDER
    dxf_path = os.path.join(folder_path, filename)

    if not os.path.exists(dxf_path):
        raise FileNotFoundError(f"DXF file not found: {dxf_path}")

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    context = RenderContext(doc)
    backend = svg.SVGBackend()

    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.BLACK
    )

    frontend = Frontend(context, backend, config=cfg)
    frontend.draw_layout(msp)

    page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(10))
    svg_string = backend.get_string(page)

    svg_filename = filename.replace(".dxf", ".svg")
    svg_path = os.path.join(folder_path, svg_filename)

    with open(svg_path, "w", encoding="utf8") as svg_file:
        svg_file.write(svg_string)

    return svg_filename  # Return only the filename

@calc_blueprint.route('/upload_dxf', methods=['POST'])
def upload_dxf():
    # Verify request fields
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only DXF files are allowed.'}), 400

    # Extract additional parameters
    try:
        quantity = int(request.form.get('quantity'))
        material_name = request.form.get('material_name')
        thickness = request.form.get('thickness')
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid quantity, material, or thickness'}), 400

    # Generate unique file name
    file_id = str(uuid.uuid4())[:8]  # Generate short unique ID
    filename = secure_filename(file.filename)
    unique_filename = f"{filename.rsplit('.', 1)[0]}_{file_id}.dxf"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    file.save(file_path)

    try:
        # Process DXF file
        dxf_data = process_dxf_file(file_path)
        dxf_data.update({'quantity': quantity, 'material_name': material_name, 'thickness': thickness})

        # Load pricing data & calculate price
        materials = load_materials()
        price = calculate_price(dxf_data, materials)

        # Convert DXF to SVG
        svg_filename = convert_dxf_to_svg(unique_filename)

        # Generate file URLs
        file_url = f"/{UPLOAD_FOLDER}/{unique_filename}"
        svg_url = f"/{UPLOAD_FOLDER}/{svg_filename}"

        # Return response
        response = {
            'success': True,
            'file_url': file_url,
            'svg_url': svg_url,
            'data': dxf_data,
            'price': price
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@calc_blueprint.route('/upload_dxf_ref', methods=['POST'])
def upload_dxf_file():
    """Upload DXF file and return the file path."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only DXF files are allowed.'}), 400

    # Generate unique file name
    file_id = str(uuid.uuid4())[:8]  # Short unique ID
    filename = secure_filename(file.filename)
    unique_filename = f"{filename.rsplit('.', 1)[0]}_{file_id}.dxf"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    file.save(file_path)

    return jsonify({'success': True, 'file_path': file_path}), 200


@calc_blueprint.route('/process_dxf', methods=['POST'])
def processing_dxf_file():
    """Process the DXF file using file path and additional fields."""
    data = request.json
    file_path = data.get('file_path')
    quantity = data.get('quantity')
    material_name = data.get('material_name')
    thickness = data.get('thickness')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'Invalid or missing file path'}), 400

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid quantity'}), 400

    if not material_name or not thickness:
        return jsonify({'error': 'Missing material name or thickness'}), 400

    try:
        # Process DXF file
        dxf_data = process_dxf_file(file_path)
        print("dxf data :", dxf_data)
        dxf_data.update({'quantity': quantity, 'material_name': material_name, 'thickness': thickness})

        # Load pricing data & calculate price
        materials = load_materials()
        price = calculate_price(dxf_data, materials)

        # Convert DXF to SVG
        svg_filename = convert_dxf_to_svg(os.path.basename(file_path))

        # Generate file URLs
        file_url = f"/{UPLOAD_FOLDER}/{os.path.basename(file_path)}"
        svg_url = f"/{UPLOAD_FOLDER}/{svg_filename}"

        response = {
            'success': True,
            'file_url': file_url,
            'svg_url': svg_url,
            'data': dxf_data,
            'price': price
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
