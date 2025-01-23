from flask import Flask, render_template, request, redirect, url_for, jsonify
from instagrapi import Client

app = Flask(name)
client = Client()

# Halaman utama untuk input username dan password
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint untuk menangani login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    try:
        client.login(username, password)
        return redirect(url_for('otp_verification'))
    except Exception as e:
        return f"Gagal login: {e}"

# Halaman OTP jika perlu verifikasi
@app.route('/otp', methods=['GET', 'POST'])
def otp_verification():
    if request.method == 'POST':
        otp = request.form['otp']
        try:
            if client.challenge_resolve(otp):
                return redirect(url_for('dashboard'))
        except Exception as e:
            return f"OTP salah atau verifikasi gagal: {e}"
    return render_template('otp.html')

# Halaman Dashboard setelah login berhasil
@app.route('/dashboard')
def dashboard():
    try:
        user_id = client.user_id
        followers = client.user_followers(user_id)
        following = client.user_following(user_id)
        
        not_following_back = [user for user in following if user not in followers]
        
        return render_template('dashboard.html', not_following_back=not_following_back)
    except Exception as e:
        return f"Error saat mengambil data followers: {e}"

# Endpoint untuk logout
@app.route('/logout')
def logout():
    client.logout()
    return "Berhasil logout!"

if name == 'main':
    app.run(debug=True)
