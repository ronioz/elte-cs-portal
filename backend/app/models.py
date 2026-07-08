from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

# AUTHENTICATION SCHEMAS

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length = 8
    )

class Token(BaseModel):
    access_token: str
    token_type: str

# SEMESTERS & COURSES

class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1)
    credits: int = Field(..., gt=0)
    grade: int = Field(..., gt=1, le=5)

class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    credits: int = Field(..., gt=0)
    grade: int = Field(..., ge=1, le=5)

class CourseResponse(CourseCreate):
    id: str
    semester_id: str

    class Config:
        from_attributes = True

class SemesterCreate(BaseModel):
    name: str = Field(..., min_length=1)

class SemesterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)

class SemesterResponse(BaseModel):
    id: str
    name: str
    courses: List[CourseResponse] = []

    class Config:
        from_attributes = True

# GPA

class SemesterGPA(BaseModel):
    semester_id: str
    semester_name: str
    gpa: float
    credits: int

class GPASummary(BaseModel):
    cumulative_gpa: float
    total_credits: int
    semesters: List[SemesterGPA]