from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from instagrapi import Client
from pydantic import BaseModel
import time

app = FastAPI()

client = Client()

# In-memory cache to store the not-following-back data (to avoid hitting Instagram API too frequently)
cache = {}

# Models for login and OTP data
class LoginData(BaseModel):
    username: str
    password: str

class OTPData(BaseModel):
    otp: str

# Serve the frontend HTML
@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("static/index.html") as f:
        return f.read()

# Background function for handling login to avoid timeout
def login_in_background(username: str, password: str):
    try:
        # Login to Instagram
        client.login(username, password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

@app.post("/login")
async def login(data: LoginData, background_tasks: BackgroundTasks):
    # Start the background task for login to avoid timeout issues (Vercel has a 10-second limit)
    background_tasks.add_task(login_in_background, data.username, data.password)
    
    return {"message": "Login is processing in the background. Please wait for a moment."}

@app.post("/verify_otp")
async def verify_otp(data: OTPData):
    try:
        # Verify OTP challenge for 2FA (two-factor authentication)
        if client.challenge_resolve(data.otp):
            return {"message": "OTP successfully verified."}
        else:
            raise HTTPException(status_code=400, detail="Invalid OTP.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OTP verification failed: {str(e)}")

def fetch_not_following_back():
    try:
        # Get the user ID for the logged-in user
        user_id = client.user_id

        # Get the lists of followers and following
        follower_usernames = client.user_followers(user_id).keys()
        following_usernames = client.user_following(user_id).keys()

        # Find users who you follow but they don't follow you back
        not_following_back = [user for user in following_usernames if user not in follower_usernames]

        # Save the data to the cache with a timestamp
        cache['not_following_back'] = {
            'data': not_following_back,
            'timestamp': time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch not-following-back users: {str(e)}")

@app.get("/not_following_back")
async def get_not_following_back(background_tasks: BackgroundTasks):
    # Check if we have cached data within the last 5 minutes (300 seconds)
    if 'not_following_back' in cache and time.time() - cache['not_following_back']['timestamp'] < 300:
        return {"not_following_back": cache['not_following_back']['data']}

    # If the cache is expired or not present, fetch the data in the background
    background_tasks.add_task(fetch_not_following_back)
    return {"message": "Fetching data in the background, please try again shortly."}
