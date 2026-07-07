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

# LOGIN AND REGISTRATION

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



# SEMESTERS AND COURSES

@app.get("/api/v1/semesters", response_model=List[SemesterResponse])
def get_semesters(email: str):
    users_db = load_db()

    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    semesters_data = []

    for info in users_db[email]["semesters"].values():
        semester_info = {
            "id": info["id"],
            "name": info["name"],
            "courses": list(info["courses".values()])
        }

        semesters_data.append(semester_info)

    return semesters_data

@app.post("/api/v1/semesters", response_model=SemesterResponse)
def add_semesters(email: str, data: SemesterCreate):
    users_db = load_db()
    
    semester_id = str(uuid.uuid4())
    semester_name = data.name

    for info in users_db[email]["semesters"].values():
        if info["name"] == semester_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Semester already exists"
            )

    semester_data = {
        "id": semester_id,
        "name": semester_name,
        "courses": {}
    }

    users_db[email]["semesters"][semester_id] = semester_data
    save_db(users_db)

    response_payload = {
        **semester_data,
        "courses": list(semester_data["courses"].values())
    }

    return response_payload

@app.delete("/api/v1/semesters/{semester_id}")
def delete_semester(email: str, semester_id: str):
    users_db = load_db()

    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found."
        )

    if semester_id not in users_db[email]["semesters"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found."
        )
    
    del users_db[email]["semesters"][semester_id]

    save_db(users_db)

    return None

@app.post("/api/v1/courses", response_model=CourseResponse)
def append_course_to_semester(email: str, course_data: CourseCreate, semester_id: str):
    users_db = load_db()

    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No email"
        )
    
    if semester_id not in users_db[email]["semesters"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    course_id = str(uuid.uuid4())

    new_course = {
        "id": course_id,
        "name": course_data.name,
        "credits": course_data.credits,
        "grade": course_data.grade
    }

    users_db[email]["semesters"]["courses"][course_id] = new_course

    save_db(users_db)

    return new_course
    


# GPA CALCULATION

@app.get("/api/v1/gpa/summary")
def get_calculations():
    pass