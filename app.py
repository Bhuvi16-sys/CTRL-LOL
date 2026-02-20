import os
import csv
from datetime import datetime
from flask import Flask, request, send_from_directory, render_template_string
from werkzeug.utils import secure_filename

import json
from flask import Flask, request, send_from_directory, jsonify, render_template

app = Flask(__name__, static_folder='.', template_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads/gallery'
app.config['LEADERBOARD_FILE'] = 'uploads/leaderboard.json'
ADMIN_PASSWORD = 'meme_lord_2026' # Simple password for admin

# Ensure gallery directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    if os.path.exists(app.config['LEADERBOARD_FILE']):
        with open(app.config['LEADERBOARD_FILE'], 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/admin/leaderboard', methods=['POST'])
def update_leaderboard():
    password = request.form.get('password')
    if password != ADMIN_PASSWORD:
        return 'Unauthorized', 401
    
    data = request.form.get('data')
    if data:
        try:
            leaderboard_data = json.loads(data)
            with open(app.config['LEADERBOARD_FILE'], 'w') as f:
                json.dump(leaderboard_data, f, indent=4)
            return 'Success'
        except Exception as e:
            return str(e), 400
    return 'No data provided', 400

@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    images = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(f"/uploads/gallery/{filename}")
    return jsonify(images)

@app.route('/api/admin/gallery/upload', methods=['POST'])
def upload_gallery_meme():
    password = request.form.get('password')
    if password != ADMIN_PASSWORD:
        return 'Unauthorized', 401
    
    if 'meme_file' not in request.files:
        return 'No file part', 400
    
    file = request.files['meme_file']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = f"GALLERY_{timestamp}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_filename))
        return 'Upload Success'
    
    return 'Invalid file', 400

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, port=5000)
