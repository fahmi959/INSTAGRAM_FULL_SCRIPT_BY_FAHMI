from flask import Flask, render_template, request, jsonify, redirect, url_for
from instagrapi import Client
import redis
from rq import Queue
from rq.job import Job
import logging
import time

# Inisialisasi Flask dan Redis
app = Flask(__name__)

# Konfigurasi Redis untuk Queue
r = redis.Redis(
    host='alive-javelin-31193.upstash.io', 
    port=6379, 
    password='AXnZAAIjcDFiOGNmOTk0MTFhYTg0NDRjYjI1OWU5ODlmN2FiZmY5ZnAxMA', 
    ssl=True
)
q = Queue(connection=r)  # Membuat Queue

# Inisialisasi Client Instagram
client = Client()

# Logger untuk debug
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

# Fungsi untuk login ke Instagram secara asinkron
def async_login(username, password):
    try:
        client.login(username, password)
        challenge = client.last_json.get("challenge", {})
        if challenge:
            logging.info(f"Challenge detected for user: {username}")
            return {'status': 'challenge', 'username': username}
        return {'status': 'success', 'username': username}
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Fungsi untuk mengambil followers dan following secara asinkron
def fetch_followers_and_following(username):
    try:
        user_id = client.user_id_from_username(username)
        followers = client.user_followers(user_id)
        following = client.user_following(user_id)
        
        followers_ids = [f['username'] for f in followers]
        following_ids = [f['username'] for f in following]

        # Tentukan siapa yang tidak follow back
        not_following_back = [user for user in following_ids if user not in followers_ids]

        return {'status': 'success', 'not_following_back': not_following_back}
    except Exception as e:
        logging.error(f"Error fetching followers/following: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Fungsi untuk menangani login dan mengambil data followers/following
def handle_user_data(username, password):
    login_result = async_login(username, password)
    
    if login_result['status'] == 'success':
        # Ambil followers dan following
        data_result = fetch_followers_and_following(username)
        return data_result
    else:
        return login_result

# Fungsi retry untuk login
def retry_login(username, password):
    attempt = 0
    while attempt < 3:
        result = async_login(username, password)
        if result.get('status') == 'success':
            return result
        elif '429' in result.get('message', ''):
            logging.info("Rate limit exceeded. Retrying after 30 seconds...")
            time.sleep(30)
            attempt += 1
        else:
            break
    return result

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Panggil tugas RQ untuk login secara asinkron
    job = q.enqueue(retry_login, username, password)

    # Redirect ke halaman status untuk memeriksa task_id
    return redirect(url_for('check_login_status', task_id=job.id))

@app.route('/check_login_status/<task_id>')
def check_login_status(task_id):
    job = Job.fetch(task_id, connection=r)

    if job.is_finished:
        result = job.result
        if result['status'] == 'success':
            # Redirect ke dashboard setelah login berhasil
            return render_template('dashboard.html', not_following_back=result['not_following_back'])
        else:
            return jsonify({'task_id': task_id, 'status': 'failed', 'result': result})
    elif job.is_failed:
        return jsonify({'task_id': task_id, 'status': 'failed', 'result': job.result})
    else:
        return jsonify({'task_id': task_id, 'status': 'pending'})

@app.route('/dashboard')
def dashboard():
    username = request.args.get('username')
    try:
        # Ambil data followers/following asinkron
        result = fetch_followers_and_following(username)
        if result['status'] == 'success':
            return render_template('dashboard.html', not_following_back=result['not_following_back'])
        else:
            return f"Error fetching data: {result.get('message')}"
    except Exception as e:
        logging.error(f"Error fetching dashboard data: {str(e)}")
        return f"Error fetching dashboard data: {e}"

if __name__ == '__main__':
    app.run(debug=True)
