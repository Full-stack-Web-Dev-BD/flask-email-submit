<!-- -api:{'cutting_line': 1783.3097909768544, 'surface_area': 45084.83465613809, 'dimensions': (293.3000000000001, 153.71576766497807), 'closed_loops': 19}
cmd:{"cutting_line": 1783.3097909768544, "surface_area": 45084.83465613809, "dimensions": [293.3000000000001, 153.71576766497807], "closed_loops": 19} -->
# DXF File Upload & Processing API

## Overview
This Flask API allows users to upload DXF files for processing. The API assigns a **unique ID** to each file, saves it, processes it using `dxfparser.py`, and returns the computed data along with the file URL.

## Features
- Upload DXF files
- Assign a unique ID to each file (`filename_ID.dxf`)
- Process the DXF file and return calculated results
- Provide a file download URL

## Installation & Setup

### 1️⃣ Clone the Repository
```bash
 git clone https://github.com/your-repo/flask-dxf-api.git
 cd flask-dxf-api
```

### 2️⃣ Install Dependencies
```bash
 pip install -r requirements.txt
```

### 3️⃣ Run the Flask Application
```bash
 python app.py
```
The API will run on `http://127.0.0.1:5000/`

---

## API Endpoints

### **1. Upload DXF File**
**Endpoint:**
```http
POST /calc/upload_dxf
```

**Description:**
Uploads a DXF file, assigns a unique filename, processes the file, and returns results with a file URL.

**Headers:**
```json
Content-Type: multipart/form-data
```

**Request Example (Postman/File Upload):**
```bash
curl -X POST http://127.0.0.1:5000/calc/upload_dxf \
  -F "file=@path/to/sample.dxf"
```

**Response Example (Success):**
```json
{
  "success": true,
  "data": {
    "cutting_line": 123.45,
    "surface_area": 678.90,
    "dimensions": [100, 200],
    "closed_loops": 5
  },
  "file_url": "http://127.0.0.1:5000/uploads/calc/sample_abc123.dxf"
}
```

**Response Example (Error - No File Provided):**
```json
{
  "error": "No file part in the request"
}
```

**Response Example (Error - Invalid File Type):**
```json
{
  "error": "Invalid file type. Only DXF files are allowed."
}
```

---

## File Storage
- Uploaded files are stored in `uploads/calc/`
- Each file gets a unique name format: `filename_UUID.dxf`
- Files are temporarily stored and deleted after processing (unless changed in the code).

---

## Development Notes
- Ensure `ezdxf` is installed for parsing DXF files.
- Modify `process_dxf_file(file_path)` in `dxfparser.py` if needed.
- To keep files permanently, remove the `os.remove(file_path)` line in `calc.py`.

---

## Future Improvements
- Add authentication for secure uploads.
- Store files in AWS S3 or a cloud storage solution.
- Implement rate limiting to prevent excessive API calls.

### 🔥 Happy Coding! 🚀

