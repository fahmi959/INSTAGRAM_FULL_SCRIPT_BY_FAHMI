from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from instagrapi import Client
from pydantic import BaseModel
import time
import redis
import json
import uuid

app = FastAPI()

# Redis Client (For session storage)
r = redis.Redis(
    host='alive-javelin-31193.upstash.io',
    port=6379,
    db=0,
    password='AXnZAAIjcDFiOGNmOTk0MTFhYTg0NDRjYjI1OWU5ODlmN2FiZmY5ZnAxMA',
    ssl=True  # Ensure to use SSL connection since it's enabled
)

client = Client()

# In-memory cache for "not-following-back" data (Optional, might be redundant with Redis)
cache = {}

# Models for login and OTP data
class LoginData(BaseModel):
    username: str
    password: str

class OTPData(BaseModel):
    otp: str

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("static/index.html") as f:
        return f.read()

def login_in_background(session_id: str, username: str, password: str):
    try:
        client.login(username, password)
        # Save the login success state in Redis with session_id
        r.set(session_id, json.dumps({"status": "logged_in", "message": "Login successful."}))
    except Exception as e:
        r.set(session_id, json.dumps({"status": "error", "message": str(e)}))

@app.post("/login")
async def login(data: LoginData, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())  # Generate a unique session ID
    
    # Start background login task to avoid timeout
    background_tasks.add_task(login_in_background, session_id, data.username, data.password)
    
    # Save the session state as 'processing'
    r.set(session_id, json.dumps({"status": "processing", "message": "Login is processing in the background. Please wait."}))
    
    return {"session_id": session_id}

@app.post("/verify_otp")
async def verify_otp(data: OTPData):
    session_id = data.otp  # You may want to change this logic to store and retrieve the session_id differently
    try:
        if client.challenge_resolve(data.otp):
            r.set(session_id, json.dumps({"status": "logged_in", "message": "OTP successfully verified."}))
            return {"message": "OTP successfully verified."}
        else:
            raise HTTPException(status_code=400, detail="Invalid OTP.")
    except Exception as e:
        r.set(session_id, json.dumps({"status": "error", "message": f"OTP verification failed: {str(e)}"}))
        raise HTTPException(status_code=400, detail=f"OTP verification failed: {str(e)}")

def fetch_not_following_back(session_id: str):
    try:
        # Get the user ID for the logged-in user
        user_id = client.user_id

        # Get the lists of followers and following
        follower_usernames = client.user_followers(user_id).keys()
        following_usernames = client.user_following(user_id).keys()

        # Find users who you follow but they don't follow you back
        not_following_back = [user for user in following_usernames if user not in follower_usernames]

        # Save the data to Redis with session_id
        r.set(session_id, json.dumps({"status": "completed", "data": not_following_back}))
    except Exception as e:
        r.set(session_id, json.dumps({"status": "error", "message": f"Failed to fetch not-following-back users: {str(e)}"}))

@app.get("/not_following_back")
async def get_not_following_back(session_id: str, background_tasks: BackgroundTasks):
    # Check Redis for the current status of the task
    session_data = r.get(session_id)
    
    if session_data:
        session_info = json.loads(session_data)
        if session_info["status"] == "completed":
            return {"not_following_back": session_info["data"]}
        elif session_info["status"] == "error":
            raise HTTPException(status_code=400, detail=session_info["message"]}
    
    # If task is still processing, start the background task to fetch data
    background_tasks.add_task(fetch_not_following_back, session_id)
    return {"message": "Fetching data in the background, please try again shortly."}
