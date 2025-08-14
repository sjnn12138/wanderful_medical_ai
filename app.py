from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/process_files', methods=['POST'])
def process_files():
    # Check if files were uploaded
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No files uploaded"}), 400
        
    files = request.files.getlist('files')
    if not files:
        return jsonify({"success": False, "message": "No files provided"}), 400
    
    try:
        # Create upload directory
        upload_dir = os.path.join('uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save files to upload directory
        saved_files = []
        for file in files:
            if file.filename == '':
                continue
            # Sanitize filename
            filename = os.path.join(upload_dir, file.filename.replace(' ', '_'))
            file.save(filename)
            saved_files.append(filename)
        
        # Convert Excel files to SQLite
        excel_files = [f for f in saved_files if f.lower().endswith(('.xlsx', '.xls'))]
        sqlite_files = []
        
        for excel_file in excel_files:
            output_name = os.path.splitext(os.path.basename(excel_file))[0] + '.db'
            sqlite_path = os.path.join('MSchema', output_name)
            
            # Run excel_to_sqlite.py with error capturing
            result = subprocess.run([
                'python', 'app/tool/excel_to_sqlite.py',
                '--input', excel_file,
                '--output', sqlite_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"excel_to_sqlite.py failed for {excel_file}: {result.stderr}"
                return jsonify({"success": False, "message": error_msg}), 500
            
            sqlite_files.append(sqlite_path)
        
        # Generate m-schema for each SQLite file
        for sqlite_file in sqlite_files:
            output_name = os.path.splitext(os.path.basename(sqlite_file))[0] + '_mschema.json'
            output_path = os.path.join('MSchema', output_name)
            
            # Run generate_mschema_tool.py with error capturing
            result = subprocess.run([
                'python', 'app/tool/generate_mschema_tool.py',
                '--db', sqlite_file,
                '--output', output_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"generate_mschema_tool.py failed for {sqlite_file}: {result.stderr}"
                return jsonify({"success": False, "message": error_msg}), 500
        
        return jsonify({"success": True, "message": "Files processed successfully"})
    
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": f"Script execution failed: {str(e)}"}), 500
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing files: {str(e)}"}), 500

if __name__ == '__main__':
    # Create MSchema directory if it doesn't exist
    app.run(host='0.0.0.0', port=5000, debug=True)