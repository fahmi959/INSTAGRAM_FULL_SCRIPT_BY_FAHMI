from flask import Flask, render_template, request, redirect, url_for, jsonify
from instagrapi import Client
from celery import Celery
import redis

# Konfigurasi Celery dengan Redis sebagai broker
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['REDIS_URL'],
        broker=app.config['REDIS_URL']
    )
    celery.conf.update(app.config)
    return celery

# Inisialisasi Flask dan Redis
app = Flask(__name__)
app.config['REDIS_URL'] = "redis://localhost:6379/0"  # Sesuaikan dengan URL Redis Anda
celery = make_celery(app)

client = Client()
client.delay_range = [1, 3]  # Delay antara 1-3 detik antara permintaan

# Halaman utama untuk input username dan password
@app.route('/')
def index():
    return render_template('index.html')

# Fungsi untuk login Instagram secara asynchronous
@celery.task
def async_login(username, password):
    try:
        client.login(username, password)
        challenge = client.last_json.get("challenge", {})
        if challenge:
            return {'status': 'challenge', 'username': username}
        return {'status': 'success', 'username': username}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Endpoint untuk menangani login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Panggil task Celery untuk login secara asynchronous
    task = async_login.apply_async(args=[username, password])

    # Simpan task ID di Redis agar bisa memeriksa status di kemudian hari
    r = redis.Redis(host='alive-javelin-31193.upstash.io', port=6379, password='AXnZAAIjcDFiOGNmOTk0MTFhYTg0NDRjYjI1OWU5ODlmN2FiZmY5ZnAxMA', ssl=True)
    r.set(f'login_task_{task.id}', 'pending')

    # Mengembalikan response segera setelah task dimulai
    return jsonify({'task_id': task.id, 'status': 'Task started'})

# Endpoint untuk memeriksa status login
@app.route('/check_login_status/<task_id>')
def check_login_status(task_id):
    r = redis.Redis(host='alive-javelin-31193.upstash.io', port=6379, password='AXnZAAIjcDFiOGNmOTk0MTFhYTg0NDRjYjI1OWU5ODlmN2FiZmY5ZnAxMA', ssl=True)
    
    # Periksa status task di Redis
    status = r.get(f'login_task_{task_id}')
    
    if status:
        return jsonify({'task_id': task_id, 'status': status.decode()})
    return jsonify({'task_id': task_id, 'status': 'not found'})

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

        followers_ids = [f['username'] for f in followers]
        following_ids = [f['username'] for f in following]

        not_following_back = [user for user in following_ids if user not in followers_ids]

        return render_template('dashboard.html', not_following_back=not_following_back)
    except Exception as e:
        return f"Error saat mengambil data followers: {e}"

# Endpoint untuk logout
@app.route('/logout')
def logout():
    client.logout()
    return "Berhasil logout!"

# Jika Anda menjalankan aplikasi secara lokal untuk pengembangan
if __name__ == '__main__':
    app.run(debug=True)
