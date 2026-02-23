import os
import json
from datetime import datetime
from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from supabase import create_client, Client

app = Flask(__name__, static_folder='.', template_folder='.')
ADMIN_PASSWORD = 'meme_lord_2026'

# 🚨 Credentials strictly Environment Variables se aayenge
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ FATAL: Supabase credentials missing! Render mein environment variables check kar.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# ==========================================
# 🏆 LEADERBOARD LOGIC (PostgreSQL Based)
# ==========================================
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        # PostgreSQL table se rank ke hisaab se sorted data utha
        response = supabase.table('leaderboard_data').select('*').order('rank').execute()
        leaderboard = []
        for row in response.data:
            leaderboard.append({
                "rank": row['rank'],
                "team": row['team_name'],
                "score": row['score'],
                "memes": row['memes_count']
            })
        return jsonify(leaderboard)
    except Exception as e:
        print("Error fetching leaderboard:", e)
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
            
            # Pura purana data delete kar aur naya insert kar (Full Sync)
            supabase.table('leaderboard_data').delete().neq('id', 0).execute()
            
            for item in leaderboard_data:
                supabase.table('leaderboard_data').insert({
                    "team_name": item['team'],
                    "score": int(item['score']),
                    "memes_count": int(item['memes']),
                    "rank": int(item['rank'])
                }).execute()
                
            return 'Success'
        except Exception as e:
            return f'Database Error: {str(e)}', 400
    return 'No data provided', 400

# ==========================================
# 🖼️ GALLERY LOGIC (Storage Bucket + PostgreSQL)
# ==========================================
@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    try:
        # Sirf public URLs ko database se fetch kar, bucket ko pura scan mat kar
        response = supabase.table('gallery_urls').select('image_url').order('created_at', desc=True).execute()
        images = [item['image_url'] for item in response.data]
        return jsonify(images)
    except Exception as e:
        print("Error fetching gallery:", e)
        return jsonify([])

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
        
        try:
            file_bytes = file.read()
            
            # 1. Bucket mein image dal
            supabase.storage.from_('gallery_images').upload(
                file=file_bytes,
                path=final_filename,
                file_options={"content-type": file.content_type}
            )
            
            # 2. Permanent Public URL nikal
            public_url = supabase.storage.from_('gallery_images').get_public_url(final_filename)
            
            # 3. URL ko PostgreSQL DB mein permanently lock kar de
            supabase.table('gallery_urls').insert({"image_url": public_url}).execute()
            
            return 'Upload Success'
        except Exception as e:
            return f"Upload failed: {str(e)}", 500
            
    return 'Invalid file', 400

if __name__ == '__main__':
    print("Starting Bulletproof Flask server...")
    app.run(debug=True, port=5000)