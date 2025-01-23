from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from instagrapi import Client
from pydantic import BaseModel

app = FastAPI()

client = Client()

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

@app.get("/not_following_back")
async def get_not_following_back():
    # Ambil user_id untuk akun yang login
    user_id = client.user_id

    # Ambil daftar followers dan following
    follower_usernames = client.user_followers(user_id).keys()
    following_usernames = client.user_following(user_id).keys()

    # Temukan pengguna yang Anda follow tapi tidak follow back
    not_following_back = [user for user in following_usernames if user not in follower_usernames]

    return {"not_following_back": not_following_back}

