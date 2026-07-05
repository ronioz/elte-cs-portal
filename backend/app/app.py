import fastapi
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

app = fastapi.FastAPI(title="ELTE CS Portal", description="Portal for ELTE Faculty of informatics")

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
    return {"message": f"Successfully registered user: {user_data.email}"}

@app.post("/api/v1/auth/login")
def login(user_data: UserLogin):
    return {"message": f"Successfully logged in user: {user_data.email}"}

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