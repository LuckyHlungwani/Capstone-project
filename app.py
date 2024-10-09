import os
from PIL import Image
import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, g, jsonify
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.image import load_img # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array # type: ignore
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import secrets
import pytz
import random
import requests
from dotenv import load_dotenv

# Create Flask instance
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

BASE_URL = 'https://api.openweathermap.org/data/2.5/onecall'
OPENWEATHER_API_KEY = ['00711421e19e39edb250360e01c9704c']
API_KEYS = ['AIzaSyDJeHrcO2VcnhZJd6XEZLVjWlfXvRa1RzM']  # Replace with your actual API key
QUERIES = [
            'crop disease management',
            'agriculture disease control',
            'plant disease prevention',
            'crop protection techniques',
            'pest control in agriculture',
            'organic farming disease control',
            'soil health and disease prevention',
            'fungal disease in crops',
            'viral infections in plants',
            'crop rotation benefits',
            'integrated pest management',
            'biological control in agriculture',
            'sustainable farming practices',
            'remote sensing for crop disease',
            'how to prevent common rust in maize',
            'blight control in agriculture',
            'drone technology in agriculture',
            'AI in crop disease detection',
            'machine learning for pest management',
            'precision agriculture techniques',
            'smart farming solutions',
            'IoT applications in agriculture',
            'genetic engineering for disease resistance',
            'blockchain for agricultural supply chains',
            'data analytics in crop management',
            'mobile apps for pest identification',
            'satellite imaging for crop health monitoring',
            'automated disease forecasting systems',
            '3D printing in agricultural equipment',
            'nanotechnology in crop protection',
            'robotics in sustainable farming',
            'biopesticides and their application',
            'chemical-free crop disease solutions'
]

@app.route('/api/fetch_videos', methods=['GET'])
def fetch_videos():
    random_query = random.choice(QUERIES)
    api_key = random.choice(API_KEYS)
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={random_query}&type=video&maxResults=6&key={api_key}"
    
    print(f"Fetching from URL: {url}")  # Log the URL being requested
    
    try:
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")  # Log the status code
        response.raise_for_status()
        data = response.json()

        print(f"Response data: {data}")  # Log the response data
        
        if 'items' not in data or not data['items']:
            return jsonify({"error": "No videos found for the given query."}), 404
        
        videos = [
            {
                "title": item["snippet"]["title"],
                "videoId": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            }
            for item in data['items']
        ]
        
        return jsonify(videos=videos)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos: {str(e)}")  # Log the error
        return jsonify({"error": "Failed to fetch videos"}), 500
    except Exception as e:
        print(f"General error: {str(e)}")  # Log any other errors
        return jsonify({"error": "An error occurred"}), 500




DATABASE = 'classifications.db'
DATABASE = 'discussion.db'
DATABASE = 'comments.db'


def get_current_time():
    timezone = pytz.timezone('Africa/Johannesburg')  # Specify your desired time zone
    return datetime.now(timezone)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        
        # Initialize classifications table
        try:
            db.execute('SELECT * FROM classifications LIMIT 1')
        except sqlite3.OperationalError:
            with app.open_resource('schema.sql', mode='r') as f:
                db.executescript(f.read())
        db.commit()

        # Initialize discussions table
        try:
            db.execute('SELECT * FROM discussions LIMIT 1')
        except sqlite3.OperationalError:
            with app.open_resource('discussion.sql', mode='r') as f:
                db.executescript(f.read())
        db.commit()

        # Initialize comments table
        try:
            db.execute('SELECT * FROM comments LIMIT 1')
        except sqlite3.OperationalError:
            with app.open_resource('comments.sql', mode='r') as f:
                db.executescript(f.read())
        db.commit()

      # Initialize notifications table
        try:
            db.execute('SELECT * FROM notifications LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('''CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                read BOOLEAN DEFAULT FALSE
            )''')
        db.commit()

        # Initialize users table
        try:
            db.execute('SELECT * FROM users LIMIT 1')
        except sqlite3.OperationalError:
            db.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
                       
            )''')
        db.commit()

# Call this function to initialize the database
init_db()


# Function to add notifications
def add_notification(message):
    db = get_db()
    db.execute('INSERT INTO notifications (message) VALUES (?)', (message,))
    db.commit()

# Load model and define class labels
class_labels = [
    'Cercospora leaf spot (Gray leaf spot)',
    'Common rust',
    'Northern Leaf Blight',
    'Healthy'
]

class_preventive_measures = [
    'Apply fungicides containing strobilurins (e.g., azoxystrobin) or triazoles (e.g., propiconazole) at early stages of infection or as a preventive measure.',
    'Use fungicides containing active ingredients like mancozeb or copper oxychloride during early infection stages to manage rust.',
    'Apply fungicides (e.g., azoxystrobin, pyraclostrobin, or propiconazole) early in the growing season when conditions are favorable for disease development.',
    'Your crop is healthy! Practice crop rotation, maintain field cleanliness by removing crop residues, and sanitize tools to prevent disease outbreaks.'
]

img_rows, img_cols = 224, 224
image_size = [244, 244, 3]

def get_model():
    global model
    model = load_model('my_model.h5')
    print(" * Model loaded!")

# Set max size of file as 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check(path):
    # Prediction
    img = load_img(path, target_size=image_size)
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x.astype('float32') / 255
    z = model.predict(x)
    index = np.argmax(z)
    accuracy = int(np.array(z).max() * 100)
    return [index, accuracy]

get_model()

@app.route("/")
def index():
    return redirect(url_for('get_started'))

@app.route("/get_started")
def get_started():
    return render_template('get_started.html')

@app.route("/home")
def home():
    if 'user' in session:
        return render_template('home.html')
    else:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))


@app.route("/upload")
def upload():
    return render_template('upload.html')

@app.route("/more_treatments", methods=['POST'])
def more_treatments():
    disease = request.form['disease']
    
    # Sample data for more treatments (You can store this in a database)
    more_treatments_dict = {
        'Cercospora leaf spot (Gray leaf spot)': 'Use resistant hybrids, rotate crops, and apply fungicides like mancozeb.',
        'Common rust': 'Plant resistant hybrids, apply fungicides, and monitor environmental conditions.',
        'Northern Leaf Blight': 'Ensure proper irrigation, use resistant varieties, and apply fungicides early.',
        'Healthy': 'Keep monitoring the crops and ensure proper field hygiene to prevent future outbreaks.'
    }
    
    treatments = more_treatments_dict.get(disease, "No additional treatments available.")
    
    return jsonify(treatments=treatments)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user'] = username  # Store username in session
            add_notification(f'{username}, you have logged in successfully!')

            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        hashed_password = generate_password_hash(password)

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('register.html')

        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()
            add_notification(f"{username}, you have successfully registered!")  # Corrected here
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different username.', 'danger')

    return render_template('register.html')



@app.route("/logout")
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route("/classify", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # Generate a unique filename
            filename = f"{int(datetime.now().timestamp())}_{file.filename}"
            file_path = os.path.join('static/images', filename)
            file.save(file_path)
            result = check(file_path)
            disease_name = class_labels[result[0]]
            accuracy = result[1]
            preventive_measure = class_preventive_measures[result[0]]

            # Save result to database
            db = get_db()
            db.execute('INSERT INTO classifications (filename, disease_name, accuracy, preventive_measure, date) VALUES (?, ?, ?, ?, ?) ',
                       (filename, disease_name, accuracy, preventive_measure, datetime.now()))
            db.commit()

            return render_template('classify.html',
                                   disease_name=disease_name,
                                   user_image=file_path,
                                   accuracy=accuracy,
                                   preventive_measures=preventive_measure)
        else:
            flash("Please upload a valid image.", 'danger')
            return redirect(url_for('predict'))

    return render_template('classify.html')

@app.route('/download-image/<path:filename>')
def download(filename):
    return send_from_directory('static/images', filename, as_attachment=True)

@app.route("/activities")
def activities():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM classifications ORDER BY date DESC')
    classifications = cur.fetchall()
    return render_template('activities.html', classifications=classifications)

@app.route('/clear_table', methods=['POST'])
def clear_table():
    try:
        delete_all_classifications()
        return jsonify({'message': 'All records deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def delete_all_classifications():
    db = get_db()
    db.execute("DELETE FROM classifications")
    db.commit()

@app.route("/weather")
def weather():
    return render_template('weather.html')

@app.route("/learning")
def learning():
    return render_template('learning.html')

@app.route("/news")
def news():
    return render_template('news.html')

@app.route("/analytics")
def analytics():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT disease_name, COUNT(*) as count FROM classifications GROUP BY disease_name')
    data = cur.fetchall()

    # Prepare data for the graphs
    disease_labels = [row['disease_name'] for row in data]
    disease_data = [row['count'] for row in data]

    return render_template('analytics.html', classifications=data, disease_labels=disease_labels, disease_data=disease_data)

@app.route("/help")
def help():
    return render_template('help.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user' not in session:
        
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    username = session['user']  # Get the username from session
    return render_template('settings.html', username=username)



@app.route('/update_username', methods=['POST'])
def update_username():
    new_username = request.form['new_username']
    user = get_current_user()  # type: ignore # Fetch the logged-in user

    if user:
        user.username = new_username
        db.session.commit()  # type: ignore # Commit changes to the database
        session['username'] = new_username  # Update session
        flash('Username updated successfully!', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('login.html'))

@app.route('/change_password', methods=['POST'])
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    # Your logic to change the password
    return redirect(url_for('login.html'))  # Redirect or render a template as needed

@app.route('/delete_account', methods=['POST'])
def delete_account():
    # Your logic to delete the account
    flash('Your account has been deleted.')
    return redirect(url_for('login.html'))  # Redirect to a suitable page after deletion

@app.route("/intro")
def app_intro():
    return render_template('intro.html')

@app.route("/comment/<int:discussion_id>", methods=['POST'])
def post_comment(discussion_id):
    if 'user' not in session:
        flash('You need to log in to post a comment.', 'danger')
        return redirect(url_for('login'))
    
    content = request.form['content']
    username = session['user']
    current_time = get_current_time()
    
    # Save comment to the database
    db = get_db()
    db.execute('INSERT INTO comments (discussion_id, username, content) VALUES (?, ?, ?)', (discussion_id, username, content))
    db.commit()
    flash('Comment posted successfully!', 'success')
    
    return redirect(url_for('community'))


@app.route("/community", methods=['GET', 'POST'])
def community():
    if request.method == 'POST':
        if 'user' not in session:
            flash('You need to log in to post a discussion.', 'danger')
            return redirect(url_for('login'))
        
        content = request.form['content']
        username = session['user']

        # Save discussion to the database
        db = get_db()
        db.execute('INSERT INTO discussions (username, content) VALUES (?, ?)', (username, content))
        db.commit()
        flash('Discussion posted successfully!', 'success')
        return redirect(url_for('community'))

    # Fetch discussions from the database
    discussions = get_db().execute('SELECT * FROM discussions ORDER BY timestamp DESC').fetchall()
    
    # Fetch comments for each discussion
    comments = {}
    for discussion in discussions:
        discussion_id = discussion['id']  # Get the current discussion ID
        comments[discussion_id] = get_db().execute(
            'SELECT * FROM comments WHERE discussion_id = ? ORDER BY timestamp DESC', 
            (discussion_id,)
        ).fetchall()

    return render_template('community.html', discussions=discussions, comments=comments)


# Weather notification function
def get_weather_alerts():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=johannesburg&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    alerts = []
    if 'alerts' in data:
        for alert in data['alerts']:
            alerts.append({
                'type': alert['event'],
                'message': alert['description'],
                'timestamp': alert['date']  # Adjust as necessary
            })
            
    return alerts

@app.route('/notification')
def notification():
    notifications = get_weather_alerts()  # Call your function here
    return render_template('notification.html', notifications=notifications)

if __name__ == "__main__":
    app.run(debug=True)
