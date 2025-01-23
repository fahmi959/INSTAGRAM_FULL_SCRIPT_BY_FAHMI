from flask import Flask, render_template, request, jsonify
from instagrapi import Client
import redis

app = Flask(__name__)

client = Client()
client.delay_range = [1, 3]

# Redis config
r = redis.Redis(
    host='alive-javelin-31193.upstash.io',
    port=6379,
    password='AXnZAAIjcDFiOGNmOTk0MTFhYTg0NDRjYjI1OWU5ODlmN2FiZmY5ZnAxMA',
    ssl=True
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Simpan status task sebagai 'pending' di Redis
    r.set('login_status', 'pending')
    
    try:
        # Proses login langsung
        client.login(username, password)
        
        # Cek challenge atau OTP
        challenge = client.last_json.get("challenge", {})
        if challenge:
            r.set('login_status', 'challenge_required')
            return jsonify({'status': 'challenge required'})
        
        r.set('login_status', 'success')
        return jsonify({'status': 'success'})
    except Exception as e:
        r.set('login_status', 'error')
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/check_login_status')
def check_status():
    status = r.get('login_status')
    if status:
        return jsonify({'status': status.decode()})
    return jsonify({'status': 'unknown'})

if __name__ == '__main__':
    app.run(debug=True)
