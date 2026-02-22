import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
import json
from flask import Flask, request, send_from_directory, jsonify, render_template
from supabase import create_client, Client

app = Flask(__name__, static_folder='.', template_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads/gallery'
app.config['LEADERBOARD_FILE'] = 'uploads/leaderboard.json'
app.config['SUPABASE_CONFIG_FILE'] = 'supabase_config.json'
ADMIN_PASSWORD = 'meme_lord_2026' # Simple password for admin

# Supabase Initialization
supabase: Client = None

def get_supabase_client():
    global supabase
    if supabase is None:
        if os.path.exists(app.config['SUPABASE_CONFIG_FILE']):
            try:
                with open(app.config['SUPABASE_CONFIG_FILE'], 'r') as f:
                    config = json.load(f)
                    if config.get('url') and config.get('key'):
                        supabase = create_client(config['url'], config['key'])
            except Exception as e:
                print(f"Error initializing Supabase: {e}")
    return supabase

def get_supabase_bucket():
    if os.path.exists(app.config['SUPABASE_CONFIG_FILE']):
        with open(app.config['SUPABASE_CONFIG_FILE'], 'r') as f:
            return json.load(f).get('bucket', 'memes')
    return 'memes'

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
    # Local images
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(f"/uploads/gallery/{filename}")
    
    # Supabase images
    try:
        sb = get_supabase_client()
        if sb:
            bucket = get_supabase_bucket()
            res = sb.storage.from_(bucket).list()
            for file in res:
                # Assuming public bucket, get public URL
                public_url = sb.storage.from_(bucket).get_public_url(file['name'])
                images.append(public_url)
    except Exception as e:
        print(f"Supabase gallery error: {e}")

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
        
        # Try Supabase upload first
        try:
            sb = get_supabase_client()
            if sb:
                bucket = get_supabase_bucket()
                file_content = file.read()
                sb.storage.from_(bucket).upload(final_filename, file_content)
                return 'Upload Success (Supabase)'
        except Exception as e:
            print(f"Supabase upload error: {e}")
            # Fallback to local if Supabase fails (optional, or just return error)
            # file.seek(0) # Reset file pointer if we want to fallback
        
        # Local fallback if Supabase is not configured
        file.seek(0)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_filename))
        return 'Upload Success (Local)'
    
    return 'Invalid file', 400

@app.route('/api/admin/supabase/config', methods=['GET', 'POST'])
def manage_supabase_config():
    password = request.form.get('password') if request.method == 'POST' else request.args.get('password')
    if password != ADMIN_PASSWORD:
        return 'Unauthorized', 401

    if request.method == 'POST':
        try:
            config = {
                'url': request.form.get('url'),
                'key': request.form.get('key'),
                'bucket': request.form.get('bucket')
            }
            with open(app.config['SUPABASE_CONFIG_FILE'], 'w') as f:
                json.dump(config, f, indent=4)
            
            # Reset global client to refresh with new config
            global supabase
            supabase = None
            
            return 'Success'
        except Exception as e:
            return str(e), 400
    else:
        if os.path.exists(app.config['SUPABASE_CONFIG_FILE']):
            with open(app.config['SUPABASE_CONFIG_FILE'], 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'url': '', 'key': '', 'bucket': ''})

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, port=5000)
