import fastapi
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import json
from pathlib import Path
import uuid
from passlib.context import CryptContext
from database import load_db, save_db

# SETTING UP APP AND DATABASE

app = fastapi.FastAPI(title="ELTE CS Portal", description="Portal for ELTE Faculty of informatics")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AUTHENTICATION SCHEMAS

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length = 8
    )

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# SEMESTERS & COURSES

class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1)
    credits: int = Field(..., gt=0)
    grade: int = Field(..., gt=1, le=5)

class CourseResponse(CourseCreate):
    id: str
    semester_id: str

    class Config:
        from_attributes = True

class SemesterCreate(BaseModel):
    name: str = Field(..., min_length=1)

class SemesterResponse(BaseModel):
    id: str
    name: str
    courses: List[CourseResponse] = []

    class Config:
        from_attributes = True

# API ENDPOINTS

@app.post("/api/v1/auth/signup")
def signup(user_data: UserSignup):
    users_db = load_db()

    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash(user_data.password)

    new_user_profile = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "semesters": {}
    }

    users_db[user_data.email] = new_user_profile
    save_db(users_db)
    
    return {"message": "Successfully registered user", "user_id": user_id}

@app.post("/api/v1/auth/login")
def login(user_data: UserLogin):
    users_db = load_db()
    user_profile = users_db.get(user_data.email)

    if not user_profile or not pwd_context.verify(user_data.password, user_profile["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    
    return {"message": "successfully logged in user"}

@app.get("/api/v1/semesters", response_model=List[SemesterResponse])
def get_semesters():
    return []

@app.post("/api/v1/semesters", response_model=SemesterResponse)
def add_semesters(semester_data: SemesterCreate):
    pass

@app.delete("/api/v1/semesters/{semester_id}")
def delete_semester(semester_id: str):
    pass

@app.post("/api/v1/courses", response_model=CourseResponse)
def append_course_to_semester(course_data: CourseCreate, semester_id: str):
    pass

@app.get("/api/v1/gpa/summary")
def get_calculations():
    pass