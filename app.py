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
from werkzeug.security import generate_password_hash


# Create Flask instance
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

BASE_URL = 'https://api.openweathermap.org/data/2.5/onecall'
OPENWEATHER_API_KEY = ['00711421e19e39edb250360e01c9704c']
API_KEYS = ['AIzaSyDJeHrcO2VcnhZJd6XEZLVjWlfXvRa1RzM']  
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


def get_current_time():
    timezone = pytz.timezone('Africa/Johannesburg')  # Specify your desired time zone
    return datetime.now(timezone)


DATABASE = 'database.db'
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


# Application Backend
@app.route("/")
def index():
    return redirect(url_for('get_started'))

@app.route("/get_started")
def get_started():
    return render_template('get_started.html')

@app.route('/home')
def home():
    if 'username' in session:
        user_id = session.get('user_id')  # Ensure you have user_id stored in the session
        unread_count = get_unread_notifications_count(user_id) if user_id else 0
        return render_template('home.html', username=session['username'], unread_count=unread_count)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = username
            # flash('You have logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password)

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user:
            db.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, username))
            db.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username not found. Please try again.', 'danger')

    return render_template('forgot_password.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Simple validation
        if not username or not password:
            flash('Username and password are required!', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save the new user to the database
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    session.pop('username', None)  # Remove username from session
    session.clear()  # Clear the entire session including flashed messages

    flash('You have logged out successfully!', 'success')
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




datetime

@app.route("/classify", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = f"{int(datetime.now().timestamp())}_{file.filename}"
            file_path = os.path.join('static/images', filename)
            file.save(file_path)
            result = check(file_path)
            disease_name = class_labels[result[0]]
            accuracy = result[1]
            preventive_measure = class_preventive_measures[result[0]]

            user_id = session.get('user_id')
            if user_id:
                db = get_db()
                db.execute('INSERT INTO classifications (user_id, file_name, disease_name, confidence_score, recommendation,timestamp) VALUES (?, ?, ?, ?, ?, ?)', 
                           (user_id, filename, disease_name, accuracy, preventive_measure,datetime.now()))
                db.commit()
                flash('Classification saved successfully!', 'success')
            else:
                flash('You must be logged in to save classifications.', 'danger')

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

@app.route("/recent_activities")
def activities():
    # Get the user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view your activities.', 'danger')
        return redirect(url_for('login'))

    db = get_db()  # Function to get the database connection
    try:
        cur = db.cursor()
        # Query the classifications table for the current user
        cur.execute('SELECT * FROM classifications WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
        classifications = cur.fetchall()  # Fetch all records for the user

        # Check if there are any classifications
        if not classifications:
            flash('No activities found.', 'info')

    except Exception as e:
        flash(f'An error occurred while retrieving activities: {str(e)}', 'danger')
        return redirect(url_for('home'))
    finally:
        cur.close()  # Ensure the cursor is closed after the operation

    # Render the recent activities template with the fetched classifications
    return render_template('recent_activities.html', classifications=classifications)



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
    news_api_key = '4caefdce549744848b356bc80b12aef3'  # Use your NewsAPI key here
    try:
        response = requests.get(f'https://newsapi.org/v2/everything?q=agriculture&apiKey={news_api_key}')
        news_data = response.json()  # Parse the JSON response
        articles = news_data.get('articles', [])  # Extract articles
        return render_template('news.html', articles=articles)  # Pass articles to the template
    except Exception as e:
        print(f"Error fetching news: {e}")
        return render_template('news.html', articles=[], error="Failed to fetch news.")


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



@app.route("/intro")
def app_intro():
    return render_template('intro.html')


@app.route('/community')
def community():
    db = get_db()
    discussions = db.execute('''
        SELECT discussions.*, users.username 
        FROM discussions 
        JOIN users ON discussions.user_id = users.id 
        ORDER BY timestamp DESC
    ''').fetchall()

    discussion_list = []
    for discussion in discussions:
        comments = db.execute('''
            SELECT comments.*, users.username 
            FROM comments 
            JOIN users ON comments.user_id = users.id 
            WHERE discussion_id = ? 
            ORDER BY timestamp DESC
        ''', (discussion['id'],)).fetchall()
        
        discussion_list.append({
            'id': discussion['id'],
            'username': discussion['username'],
            'topic': discussion['topic'],
            'discussion': discussion['discussion'],
            'timestamp': discussion['timestamp'],
            'comments': comments
        })

    return render_template('community.html', discussions=discussion_list)

@app.route('/add_discussion', methods=['POST'])
def add_discussion():
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        topic = request.form['topic']
        discussion = request.form['discussion']
        timestamp = datetime.now()

        db = get_db()
        db.execute('INSERT INTO discussions (user_id, topic, discussion, timestamp) VALUES (?, ?, ?, ?)', 
                   (user_id, topic, discussion, timestamp))
        db.commit()

        # Notify all users
        users = db.execute('SELECT id FROM users WHERE id != ?', (user_id,)).fetchall()
        for user in users:
            add_notification(user['id'], f'New discussion "{topic}" posted by {username}')
        
        # flash('Discussion posted successfully!', 'success')
    else:
        flash('You must be logged in to post a discussion.', 'danger')
    return redirect(url_for('community'))

@app.route('/add_comment/<int:discussion_id>', methods=['POST'])
def add_comment(discussion_id):
    if 'user_id' in session:
        user_id = session['user_id']
        comment = request.form['comment']
        timestamp = datetime.now()

        db = get_db()
        db.execute('INSERT INTO comments (user_id, discussion_id, comment, timestamp) VALUES (?, ?, ?, ?)', 
                   (user_id, discussion_id, comment, timestamp))
        db.commit()

        # flash('Comment added successfully!', 'success')
    else:
        flash('You must be logged in to comment.', 'danger')
    return redirect(url_for('community'))


@app.route('/settings')
def settings():
    if 'user_id' in session:
        username = session['username']
        return render_template('settings.html', username=username)
    else:
        flash('You need to be logged in to access settings.', 'danger')
        return redirect(url_for('login'))

@app.route('/update_username', methods=['POST'])
def update_username():
    if 'user_id' in session:
        new_username = request.form['username']
        user_id = session['user_id']
        db = get_db()
        try:
            db.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
            db.commit()
            session['username'] = new_username
            flash('Username updated successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another one.', 'danger')
    else:
        flash('You need to be logged in to update your username.', 'danger')
    return redirect(url_for('settings'))

@app.route('/update_password', methods=['POST'])
def update_password():
    if 'user_id' in session:
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password)
        user_id = session['user_id']
        db = get_db()
        db.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
        db.commit()
        flash('Password updated successfully!', 'success')
    else:
        flash('You need to be logged in to update your password.', 'danger')
    return redirect(url_for('settings'))


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.execute('DELETE FROM classifications WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM classifications WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM discussions WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM comments WHERE user_id = ?', (user_id,))
        db.commit()
        session.clear()
        flash('Account deleted successfully!', 'success')
        return redirect(url_for('login'))
    else:
        flash('You need to be logged in to delete your account.', 'danger')
        return redirect(url_for('login'))


# Add a function to add a notification
def add_notification(user_id, message):
    db = get_db()
    timestamp = datetime.now()  # Get the current datetime
    db.execute('INSERT INTO notifications (user_id, message, timestamp) VALUES (?, ?, ?)', (user_id, message, timestamp))
    db.commit()

# Fetch notifications for a user
# Fetch notifications for a user
@app.route('/notifications')
def notifications():
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        notifications = db.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10', (user_id,)).fetchall()
        return render_template('notifications.html', notifications=notifications)
    else:
        flash('You need to be logged in to view notifications.', 'danger')
        return redirect(url_for('login'))

def get_unread_notifications_count(user_id):
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM notifications WHERE user_id = ? AND read = 0', (user_id,)).fetchone()[0]
    return count

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

