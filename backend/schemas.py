from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from fastapi import UploadFile, File

# === 数据模型定义 ===
class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int

class UserInDB(User):
    password: str

class UserMeResponse(BaseModel):
    user_id: int
    username: str
    is_student: bool
    is_teacher: bool
    email: str

class StudentBase(BaseModel):
    grade: str
    major: str

class StudentCreate(StudentBase):
    user: UserCreate

class StudentOut(StudentBase):
    student_id: int
    user: User

class CourseStudentOut(BaseModel):
    student_id: int
    major: str
    grade: Optional[float]
    course_id: int
    course_name: str

class StudentDetail(StudentOut):
    classes: List[Dict[str, Any]] = []
    courses: List[Dict[str, Any]] = []

class StudentUpdate(BaseModel):
    grade: Optional[str] = None
    major: Optional[str] = None

class TeacherBase(BaseModel):
    title: str
    department: str

class TeacherCreate(TeacherBase):
    user: UserCreate

class TeacherOutBase(TeacherBase):
    teacher_id: int

class TeacherOut(TeacherOutBase):
    user: User

class CourseBase(BaseModel):
    course_name: str
    credit: int

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    course_id: int

class AssignmentBase(BaseModel):
    content: str
    deadline: datetime
    status: str

class AssignmentCreate(AssignmentBase):
    teacher_id: int

class AssignmentOut(AssignmentBase):
    assignment_id: int
    teacher_id: int

class SubmissionBase(BaseModel):
    student_id: int
    assignment_id: int
    submit_time: datetime

class SubmissionCreate(SubmissionBase):
    file: UploadFile = File(...)

class SubmissionOut(SubmissionBase):
    submission_id: int
    file_path: str

class ClassBase(BaseModel):
    class_name: str
    grade: str

class ClassCreate(ClassBase):
    pass

class ClassOut(ClassBase):
    class_id: int

class TeacherUpdate(BaseModel):
    title: Optional[str]
    department: Optional[str]

class ClassUpdate(BaseModel):
    class_name: Optional[str]
    grade: Optional[str]

class PermissionBase(BaseModel):
    permission_name: str
    description: str

class PermissionAssign(BaseModel):
    permission_id: int

class GradeUpdate(BaseModel):
    grade: float