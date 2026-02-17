import os
import csv
from datetime import datetime
from flask import Flask, request, send_from_directory, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max size
app.config['CSV_FILE'] = 'submissions.csv'

# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Ensure CSV file exists with headers
# Note: If the file exists but has old headers, this won't update it automatically. 
# In a real app we'd migrate, but here appending new columns to new rows is acceptable for a hackathon.
if not os.path.exists(app.config['CSV_FILE']):
    with open(app.config['CSV_FILE'], 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Name', 'Email', 'Phone', 'College', 'Branch', 'RegNo', 'UPI_ID', 'Meme_Filename', 'Payment_Filename'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if files exist
    if 'meme_file' not in request.files or 'payment_file' not in request.files:
        return 'Missing files. Please upload both your Meme and Payment Screenshot.', 400
    
    meme_file = request.files['meme_file']
    payment_file = request.files['payment_file']
    
    # Text fields
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    college = request.form.get('college')
    branch = request.form.get('branch')
    regno = request.form.get('regno') # Keeping consistent with previous, though screenshot didn't explicitly show it
    upi_id = request.form.get('upi_id')
    consent = request.form.get('consent')

    # Basic Validation
    if not all([name, email, phone, college, branch, upi_id]):
         return 'Missing required fields. Please fill all details.', 400
    
    if not consent:
        return 'You must agree to the event rules to submit.', 400

    # File Validation & Saving
    if meme_file.filename == '' or payment_file.filename == '':
        return 'No selected file', 400
        
    if allowed_file(meme_file.filename) and allowed_file(payment_file.filename):
        # Secure filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = secure_filename(name).replace(' ', '_')
        
        meme_filename = f"MEME_{timestamp}_{safe_name}_{secure_filename(meme_file.filename)}"
        payment_filename = f"PAY_{timestamp}_{safe_name}_{secure_filename(payment_file.filename)}"
        
        meme_file.save(os.path.join(app.config['UPLOAD_FOLDER'], meme_filename))
        payment_file.save(os.path.join(app.config['UPLOAD_FOLDER'], payment_filename))
        
        # Log to CSV
        with open(app.config['CSV_FILE'], 'a', newline='') as f:
            writer = csv.writer(f)
            # Schema: Timestamp, Name, Email, Phone, College, Branch, RegNo, UPI_ID, Meme, Payment
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                name, email, phone, college, branch, regno, upi_id, 
                meme_filename, payment_filename
            ])
            
        return f'''
        <html>
            <body style="background: #05000a; color: #00FF00; font-family: 'Outfit', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; text-align: center;">
                <h1 style="font-size: 3rem; margin-bottom: 20px;">Registration Successful! 🚀</h1>
                <p style="font-size: 1.2rem; color: #B8A2C9;">Welcome to the Meme-verse, {name}.</p>
                <div style="background: rgba(255,0,255,0.1); padding: 20px; border-radius: 10px; margin-top: 30px; border: 1px solid #FF00FF;">
                    <p><strong>Meme:</strong> {meme_filename}</p>
                    <p><strong>Payment Proof:</strong> {payment_filename}</p>
                </div>
                <a href="/" style="color: #00FFFF; margin-top: 30px; text-decoration: none; font-size: 1.1rem; border-bottom: 1px solid #00FFFF;">Return to Home</a>
            </body>
        </html>
        '''
    
    return 'Invalid file type. Only PNG, JPG, and PDF allowed.', 400

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(debug=True, port=5000)
