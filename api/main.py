from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from instagrapi import Client
from pydantic import BaseModel
import time

app = FastAPI()

client = Client()

# In-memory cache to store the not-following-back data (to avoid hitting Instagram API too frequently)
cache = {}

# Model untuk input data login dan OTP
class LoginData(BaseModel):
    username: str
    password: str

class OTPData(BaseModel):
    otp: str

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("static/index.html") as f:
        return f.read()

@app.post("/login")
async def login(data: LoginData):
    try:
        client.login(data.username, data.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Login berhasil."}

@app.post("/verify_otp")
async def verify_otp(data: OTPData):
    try:
        if client.challenge_resolve(data.otp):
            return {"message": "OTP berhasil diverifikasi."}
        else:
            raise HTTPException(status_code=400, detail="OTP salah.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def fetch_not_following_back():
    # Ambil user_id untuk akun yang login
    user_id = client.user_id

    # Ambil daftar followers dan following
    follower_usernames = client.user_followers(user_id).keys()
    following_usernames = client.user_following(user_id).keys()

    # Temukan pengguna yang Anda follow tapi tidak follow back
    not_following_back = [user for user in following_usernames if user not in follower_usernames]

    # Save to cache with timestamp
    cache['not_following_back'] = {
        'data': not_following_back,
        'timestamp': time.time()
    }

@app.get("/not_following_back")
async def get_not_following_back(background_tasks: BackgroundTasks):
    # Check if we have cached data within the last 5 minutes
    if 'not_following_back' in cache and time.time() - cache['not_following_back']['timestamp'] < 300:
        return {"not_following_back": cache['not_following_back']['data']}

    # If no cache or cache is outdated, start a background task to fetch data
    background_tasks.add_task(fetch_not_following_back)
    return {"message": "Fetching data in the background, please try again shortly."}
