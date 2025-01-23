from flask import Flask, render_template, request, redirect, url_for
from instagrapi import Client
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)
client = Client()

# Set delay range for Instagram API requests
# client.delay_range = [1, 3]  # Adding delay between requests

# Function to fetch followers and following concurrently with reduced limits
def get_followers_and_following(user_id):
    with ThreadPoolExecutor() as executor:
        # Reduce the number of followers/following fetched to 50
        followers_future = executor.submit(client.user_followers, user_id, amount=50)  # Limit to 50 followers
        following_future = executor.submit(client.user_following, user_id, amount=50)  # Limit to 50 following
        followers = followers_future.result()
        following = following_future.result()
    return followers, following

# Home page route for username and password input
@app.route('/')
def index():
    return render_template('index.html')

# Login route to handle login and verification
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    try:
        # Login to Instagram
        client.login(username, password)

        # Check if there is a challenge (e.g., OTP)
        challenge = client.last_json.get("challenge", {})
        if challenge:
            return redirect(url_for('otp_verification', username=username))
        
        # If login is successful without challenge, redirect to dashboard
        return redirect(url_for('dashboard', username=username))
    except Exception as e:
        return f"Login failed: {e}"

# OTP verification page
@app.route('/otp', methods=['GET', 'POST'])
def otp_verification():
    username = request.args.get('username')
    if request.method == 'POST':
        otp = request.form['otp']
        try:
            # Resolve OTP
            if client.challenge_resolve(otp):
                return redirect(url_for('dashboard', username=username))
        except Exception as e:
            return f"OTP verification failed: {e}"
    return render_template('otp.html')

# Dashboard page after login
@app.route('/dashboard')
def dashboard():
    username = request.args.get('username')
    try:
        user_id = client.user_id_from_username(username)

        # Fetch followers and following concurrently with reduced amount
        followers, following = get_followers_and_following(user_id)

        # Compare followers and following to find users who don't follow back
        followers_ids = [f['username'] for f in followers]
        following_ids = [f['username'] for f in following]
        
        not_following_back = [user for user in following_ids if user not in followers_ids]
        
        return render_template('dashboard.html', not_following_back=not_following_back)
    except Exception as e:
        return f"Error fetching followers: {e}"

# Logout endpoint
@app.route('/logout')
def logout():
    client.logout()
    return "Successfully logged out!"

if __name__ == '__main__':
    app.run(debug=True)
