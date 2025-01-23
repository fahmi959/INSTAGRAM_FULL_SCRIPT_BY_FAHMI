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

# Fungsi login Instagram secara asinkron dengan error handling
def async_login(username, password):
    try:
        # Login ke Instagram
        client.login(username, password)

        # Jika ada tantangan (misal OTP atau verifikasi 2 faktor)
        challenge = client.last_json.get("challenge", {})
        if challenge:
            logging.info(f"Challenge detected for user: {username}")
            return {'status': 'challenge', 'username': username}

        # Ambil data followers dan following
        user_id = client.user_id
        followers = client.user_followers(user_id)
        following = client.user_following(user_id)

        # Ambil daftar followers dan following
        followers_ids = [f['username'] for f in followers]
        following_ids = [f['username'] for f in following]

        # Tentukan siapa yang tidak follow back
        not_following_back = [user for user in following_ids if user not in followers_ids]

        return {'status': 'success', 'username': username, 'not_following_back': not_following_back}

    except Exception as e:
        logging.error(f"Error during login process: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Fungsi untuk menambahkan retry jika terjadi status 429
def retry_login(username, password):
    attempt = 0
    while attempt < 3:  # Coba hingga 3 kali jika terjadi error 429 (Too Many Requests)
        result = async_login(username, password)
        if result.get('status') == 'success':
            return result
        elif '429' in result.get('message', ''):
            logging.info("Rate limit exceeded. Retrying after 30 seconds...")
            time.sleep(30)  # Tunggu selama 30 detik sebelum mencoba lagi
            attempt += 1
        else:
            break
    return result

# Endpoint untuk login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Panggil tugas RQ untuk login secara asinkron
    job = q.enqueue(retry_login, username, password)

    # Redirect ke halaman status untuk memeriksa task_id
    return redirect(url_for('check_login_status', task_id=job.id))

# Endpoint untuk memeriksa status login dan menampilkan not_following_back
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
    username = request.args.get('username')
    try:
        user_id = client.user_id_from_username(username)
        followers = client.user_followers(user_id)
        following = client.user_following(user_id)

        # Ambil daftar followers dan following
        followers_ids = [f['username'] for f in followers]
        following_ids = [f['username'] for f in following]

        # Tentukan siapa yang tidak follow back
        not_following_back = [user for user in following_ids if user not in followers_ids]

        return render_template('dashboard.html', not_following_back=not_following_back)
    except Exception as e:
        logging.error(f"Error saat mengambil data followers: {str(e)}")
        return f"Error saat mengambil data followers: {e}"

# Endpoint untuk logout
@app.route('/logout')
def logout():
    client.logout()
    return "Berhasil logout!"

if __name__ == '__main__':
    app.run(debug=True)
