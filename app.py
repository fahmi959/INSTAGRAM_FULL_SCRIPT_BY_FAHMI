from flask import Flask, render_template, request, redirect, url_for, jsonify
from instagrapi import Client

app = Flask(__name__)
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
        # Login Instagram
        client.login(username, password)

        # Cek apakah ada challenge (OTP)
        challenge = client.last_json.get("challenge", {})
        if challenge:
            return redirect(url_for('otp_verification', username=username))
        
        # Jika login sukses tanpa challenge, arahkan ke dashboard
        return redirect(url_for('dashboard', username=username))
    except Exception as e:
        return f"Gagal login: {e}"

# Halaman OTP jika perlu verifikasi
@app.route('/otp', methods=['GET', 'POST'])
def otp_verification():
    username = request.args.get('username')
    if request.method == 'POST':
        otp = request.form['otp']
        try:
            # Kirim OTP dan verifikasi
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
        
        # Ambil ID dari followers dan following untuk membandingkan siapa yang tidak follow back
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

if __name__ == '__main__':
    app.run(debug=True)
