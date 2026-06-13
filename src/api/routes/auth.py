from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.core.security import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(login_data: LoginRequest):
    # احراز هویت ساده (در تولید به دیتابیس متصل شود)
    if login_data.username == "admin" and login_data.password == "admin":
        token = create_access_token(data={"sub": login_data.username, "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
