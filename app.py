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

# Halaman utama untuk input username dan password
@app.route('/')
def index():
    return render_template('index.html')

# Fungsi login Instagram secara asinkron
def async_login(username, password):
    try:
        # Login ke Instagram
        client.login(username, password)

        # Jika ada tantangan (misal OTP atau verifikasi 2 faktor)
        challenge = client.last_json.get("challenge", {})
        if challenge:
            logging.info(f"Challenge detected for user: {username}")
            return {'status': 'challenge', 'username': username}

        return {'status': 'success', 'username': username}

    except Exception as e:
        logging.error(f"Error during login process: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Fungsi untuk mengambil followers secara asinkron
def fetch_followers(username):
    try:
        user_id = client.user_id_from_username(username)
        followers = client.user_followers(user_id)
        followers_ids = [f['username'] for f in followers]
        return {'status': 'success', 'followers': followers_ids}
    except Exception as e:
        logging.error(f"Error fetching followers for {username}: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Fungsi untuk mengambil following secara asinkron
def fetch_following(username):
    try:
        user_id = client.user_id_from_username(username)
        following = client.user_following(user_id)
        following_ids = [f['username'] for f in following]
        return {'status': 'success', 'following': following_ids}
    except Exception as e:
        logging.error(f"Error fetching following for {username}: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Fungsi untuk membandingkan followers dan following
def compare_followers_following(following, followers):
    not_following_back = [user for user in following if user not in followers]
    return {'status': 'success', 'not_following_back': not_following_back}

# Endpoint untuk login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Panggil tugas RQ untuk login secara asinkron
    job = q.enqueue(async_login, username, password)

    # Redirect ke halaman status untuk memeriksa task_id
    return redirect(url_for('check_login_status', task_id=job.id))

# Endpoint untuk memeriksa status login dan melanjutkan mengambil followers
@app.route('/check_login_status/<task_id>')
def check_login_status(task_id):
    job = Job.fetch(task_id, connection=r)

    if job.is_finished:
        result = job.result
        if result['status'] == 'success':
            # Panggil tugas untuk mengambil followers secara asinkron
            job_followers = q.enqueue(fetch_followers, result['username'])
            return redirect(url_for('check_followers_status', task_id=job_followers.id))
        else:
            return jsonify({'task_id': task_id, 'status': 'failed', 'result': result})
    elif job.is_failed:
        return jsonify({'task_id': task_id, 'status': 'failed', 'result': job.result})
    else:
        return jsonify({'task_id': task_id, 'status': 'pending'})

# Endpoint untuk memeriksa status followers dan melanjutkan mengambil following
@app.route('/check_followers_status/<task_id>')
def check_followers_status(task_id):
    job = Job.fetch(task_id, connection=r)

    if job.is_finished:
        followers_result = job.result
        if followers_result['status'] == 'success':
            # Panggil tugas untuk mengambil following secara asinkron
            job_following = q.enqueue(fetch_following, followers_result['followers'])
            return redirect(url_for('check_following_status', task_id=job_following.id))
        else:
            return jsonify({'task_id': task_id, 'status': 'failed', 'result': followers_result})
    elif job.is_failed:
        return jsonify({'task_id': task_id, 'status': 'failed', 'result': job.result})
    else:
        return jsonify({'task_id': task_id, 'status': 'pending'})

# Endpoint untuk memeriksa status following dan melanjutkan perbandingan
@app.route('/check_following_status/<task_id>')
def check_following_status(task_id):
    job = Job.fetch(task_id, connection=r)

    if job.is_finished:
        following_result = job.result
        if following_result['status'] == 'success':
            # Panggil tugas untuk membandingkan followers dan following secara asinkron
            comparison_result = compare_followers_following(following_result['following'], following_result['followers'])
            return render_template('dashboard.html', not_following_back=comparison_result['not_following_back'])
        else:
            return jsonify({'task_id': task_id, 'status': 'failed', 'result': following_result})
    elif job.is_failed:
        return jsonify({'task_id': task_id, 'status': 'failed', 'result': job.result})
    else:
        return jsonify({'task_id': task_id, 'status': 'pending'})

# Halaman OTP jika perlu verifikasi
@app.route('/otp', methods=['GET', 'POST'])
def otp_verification():
    username = request.args.get('username')
    if request.method == 'POST':
        otp = request.form['otp']
        try:
            if client.challenge_resolve(otp):
                return redirect(url_for('dashboard', username=username))
        except Exception as e:
            logging.error(f"OTP verification failed: {str(e)}")
            return f"OTP salah atau verifikasi gagal: {e}"
    return render_template('otp.html')

# Halaman Dashboard setelah login berhasil
@app.route('/dashboard')
def dashboard():
    # Data akan dikirimkan melalui template dari `check_following_status` setelah perbandingan dilakukan
    return render_template('dashboard.html')

# Endpoint untuk logout
@app.route('/logout')
def logout():
    client.logout()
    return "Berhasil logout!"

if __name__ == '__main__':
    app.run(debug=True)
