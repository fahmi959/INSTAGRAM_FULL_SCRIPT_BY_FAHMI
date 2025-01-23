from flask import Flask, render_template, request, redirect, url_for, jsonify
from instagrapi import Client
import redis
from rq import Queue
from rq.job import Job

# Inisialisasi Flask dan Redis
app = Flask(__name__)

# Menghubungkan ke Redis dan membuat Queue
r = redis.Redis(host='alive-javelin-31193.upstash.io', port=6379, password='AXnZAAIjcDFiOGNmOTk0MTFhYTg0NDRjYjI1OWU5ODlmN2FiZmY5ZnAxMA', ssl=True)
q = Queue(connection=r)  # Membuat Queue

client = Client()
client.delay_range = [1, 3]  # Delay antara 1-3 detik antara permintaan

# Halaman utama untuk input username dan password
@app.route('/')
def index():
    return render_template('index.html')

# Fungsi untuk login Instagram secara asynchronous
def async_login(username, password):
    try:
        client.login(username, password)
        challenge = client.last_json.get("challenge", {})
        if challenge:
            return {'status': 'challenge', 'username': username}
        
        # Mengambil data followers dan following
        user_id = client.user_id
        followers = client.user_followers(user_id)
        following = client.user_following(user_id)

        followers_ids = [f['username'] for f in followers]
        following_ids = [f['username'] for f in following]

        # Menentukan siapa yang tidak follow back
        not_following_back = [user for user in following_ids if user not in followers_ids]

        return {'status': 'success', 'username': username, 'not_following_back': not_following_back}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Endpoint untuk menangani login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Panggil task RQ untuk login secara asynchronous
    job = q.enqueue(async_login, username, password)

    # Kembalikan task_id sebagai response
    return jsonify({'task_id': job.id, 'status': 'Task started'})

# Endpoint untuk memeriksa status login dan menampilkan not_following_back
@app.route('/check_login_status/<task_id>')
def check_login_status(task_id):
    job = Job.fetch(task_id, connection=r)

    if job.is_finished:
        result = job.result
        if result['status'] == 'success':
            return render_template('dashboard.html', not_following_back=result['not_following_back'])
        else:
            return jsonify({'task_id': task_id, 'status': 'failed', 'result': result})
    elif job.is_failed:
        return jsonify({'task_id': task_id, 'status': 'failed', 'result': job.result})
    else:
        return jsonify({'task_id': task_id, 'status': 'pending'})

# Halaman Dashboard setelah login berhasil
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', not_following_back=[])

# Endpoint untuk logout
@app.route('/logout')
def logout():
    client.logout()
    return "Berhasil logout!"

if __name__ == '__main__':
    app.run(debug=True)
