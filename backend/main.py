from fastapi import APIRouter, FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi import Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import List, Optional, Dict, Any, Union
from contextlib import contextmanager
from sqlalchemy.orm import Session
import os
import uuid
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
from schemas import *
from sqlalchemy.exc import IntegrityError

from datastore import DataStore;

# 创建数据存储实例
data_store = DataStore()

# JWT 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# === 路由定义 ===
# 主路由
api_router = APIRouter()

# 学生路由
stu_router = APIRouter()

# 教师路由
tea_router = APIRouter()

# 课程路由
course_router = APIRouter()

# 作业路由
assign_router = APIRouter()

# 文件路由
file_router = APIRouter()

# 班级路由
class_router = APIRouter()

# 用户管理
user_router = APIRouter()

# 认证路由
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# === 认证相关函数 ===
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 使用 get_user_by_username 方法
    user = data_store.get_user(username)
    if user is None:
        raise credentials_exception
    
    # 添加角色信息
    user["is_student"] = data_store.get_student_by_user_id(user["user_id"]) is not None
    user["is_teacher"] = data_store.get_teacher_by_user_id(user["user_id"]) is not None
    
    return user

async def get_current_student(current_user: User = Depends(get_current_user)):
    """获取当前学生用户"""
    # 检查学生身份
    if not current_user.get("is_student", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要学生权限"
        )
    return current_user

async def get_current_teacher(current_user: User = Depends(get_current_user)):
    """获取当前教师用户"""
    # 检查教师身份
    if not current_user.get("is_teacher", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要教师权限"
        )
    return current_user

# === 认证路由 ===
@api_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = data_store.get_user(form_data.username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if form_data.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 添加角色信息
    user["is_student"] = data_store.get_student_by_user_id(user["user_id"]) is not None
    user["is_teacher"] = data_store.get_teacher_by_user_id(user["user_id"]) is not None
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# === 教师管理端点 ===
@tea_router.post("/teachers/", response_model=TeacherOut)
async def create_teacher(teacher: TeacherCreate):
    new_teacher = data_store.create_teacher(teacher)
    user = data_store.get_user_by_id(new_teacher["user_id"])
    return {**new_teacher, "user": user}

@tea_router.get("/teachers/", response_model=List[TeacherOutBase])
async def get_teachers():
    return data_store.get_teachers()

@tea_router.get("/teachers/{teacher_id}")
async def get_teacher(teacher_id: int):
    teacher = data_store.get_teacher(teacher_id)
    if teacher is None:
        return {}
    user = data_store.get_user_by_id(teacher["user_id"])
    return {**teacher, "user": user}

@tea_router.get("/teachers/{teacher_id}/classes", response_model=List[ClassOut])
async def get_teacher_classes(teacher_id: int):
    return data_store.get_teacher_classes(teacher_id)

@tea_router.put("/teachers/{teacher_id}", response_model=TeacherOutBase)
async def update_teacher(
    teacher_id: int, 
    update_data: TeacherUpdate,
    current_user: Dict = Depends(get_current_teacher)
):
    # 权限检查：只有教师本人可以更新
    if current_user["teacher_id"] != teacher_id:
        raise HTTPException(status_code=403, detail="只有老师自己可以更新自己的信息")
    
    updated_teacher = data_store.update_teacher(teacher_id, update_data)
    if not updated_teacher:
        raise HTTPException(status_code=404, detail="教师不存在")
    
    return updated_teacher

@tea_router.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: int,
    current_user: Dict = Depends(get_current_teacher)
):  
    if not data_store.delete_teacher(teacher_id):
        raise HTTPException(status_code=404, detail="教师不存在")
    
    return {"message": "删除老师成功"}

# === 学生管理端点 ===
@stu_router.post("/students/", response_model=StudentOut)
async def create_student(student: StudentCreate):
    new_student = data_store.create_student(student)
    user = data_store.get_user_by_id(new_student["user_id"])
    return {**new_student, "user": user}

@stu_router.get("/students/", response_model=List[StudentOut])
async def get_students(skip: int = 0, limit: int = 100):
    students = data_store.get_students(skip, limit)
    result = []
    for student in students:
        user = data_store.get_user_by_id(student["user_id"])
        result.append({**student, "user": user})
    return result

@stu_router.get("/students/{student_id}", response_model=StudentDetail)
async def get_student(student_id: int):
    student = data_store.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    user = data_store.get_user_by_id(student["user_id"])
    
    # 获取学生所属班级
    classes = data_store.get_student_classes(student_id)
    
    # 获取学生课程成绩
    courses = data_store.get_student_courses(student_id)
    
    return {**student, "user": user, "classes": classes, "courses": courses}

@stu_router.put("/students/{student_id}", response_model=StudentOut)
async def update_student(student_id: int, student: StudentUpdate):
    updated_student = data_store.update_student(student_id, student)
    if not updated_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    user = data_store.get_user_by_id(updated_student["user_id"])
    return {**updated_student, "user": user}

# === 课程管理端点 ===
@course_router.post("/courses/", response_model=CourseOut)
async def create_course(course: CourseCreate, current_user: Dict = Depends(get_current_teacher)):
    teacher = data_store.get_teacher_by_user_id(current_user["user_id"])
    new_course = data_store.create_course(course, teacher["teacher_id"])
    return new_course

@course_router.get("/courses/", response_model=List[CourseOut])
async def get_courses():
    return data_store.get_courses()

@course_router.post("/courses/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_course(course_id: int, current_user: Dict = Depends(get_current_student)):
    """学生选课"""
    # 获取学生信息
    student = data_store.get_student_by_user_id(current_user["user_id"])
    if not student:
        raise HTTPException(status_code=404, detail="学生信息不存在")

    student_id = student["student_id"]

    # 检查是否已选课
    courses = data_store.get_student_courses(student_id)
    if any(course["course_id"] == course_id for course in courses):
        raise HTTPException(status_code=400, detail="已选过该课程")
    
    # 添加选课记录
    if not data_store.enroll_student_in_course(student_id, course_id):
        raise HTTPException(status_code=500, detail="选课失败")
    
    return {"message": "选课成功"}

@course_router.get("/courses/{course_id}/students", response_model=List[CourseStudentOut])
async def get_course_students(course_id: int, current_user: Dict = Depends(get_current_teacher)):
    return data_store.get_course_students(course_id)

# === 作业管理端点 === 
@assign_router.get("/assignments/", response_model=List[AssignmentOut])
async def get_assignments():
    return data_store.get_assignments()

@assign_router.post("/assignments/", response_model=AssignmentOut)
async def create_assignment(
    assignment: AssignmentCreate, 
    current_user: Dict = Depends(get_current_teacher),
):
    try:
        new_assignment = data_store.create_assignment(assignment)
        return new_assignment
    except ValueError as e:
        # 处理预检查错误
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError as e:
        # 处理数据库约束错误
        if "foreign key" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail="关联的教师不存在"
            )
        raise HTTPException(
            status_code=400,
            detail="数据完整性错误"
        )

@assign_router.get("/courses/{course_id}/assignments", response_model=List[AssignmentOut])
async def get_course_assignments(course_id: int):
    return data_store.get_assignments_by_course(course_id)

@assign_router.post("/assignments/{assignment_id}/submit", response_model=SubmissionOut)
async def submit_assignment(
    assignment_id: int, 
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_student)
):
    # 获取学生信息
    student = data_store.get_student_by_user_id(current_user["user_id"])
    if not student:
        raise HTTPException(status_code=404, detail="学生信息不存在")
    
    student_id = student["student_id"]
    
    # 检查作业是否存在
    assignment = data_store.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    # 如果时间晚于截止日期就拒收
    if datetime.utcnow() > assignment["deadline"]:
        raise HTTPException(status_code=400, detail="作业已截止")
    
    # 保存文件
    file_path = data_store.save_upload_file(file)
     
    # 创建提交记录
    new_submission = data_store.create_submission({
        "student_id": student_id,
        "assignment_id": assignment_id,
        "submit_time": datetime.utcnow(),
        "file_path": file_path
    })
    
    return new_submission

@assign_router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionOut])
async def get_assignment_submissions(assignment_id: int, current_user: Dict = Depends(get_current_teacher)):
    submissions = data_store.get_submissions_by_assignment(assignment_id)
    return submissions

# === 班级管理端点 ===
@class_router.post("/", response_model=ClassOut)
async def create_class(class_data: ClassCreate):
    new_class = data_store.create_class(class_data)
    return new_class

@class_router.get("/{class_id}/students", response_model=List[StudentOut])
async def get_class_students(class_id: int):
    students = data_store.get_class_students(class_id)
    
    result = []
    for student in students:
        user = data_store.get_user_by_id(student["user_id"])
        result.append({**student, "user": user})
    return result

@class_router.post("/{class_id}/add-student/{student_id}", status_code=status.HTTP_201_CREATED)
async def add_student_to_class(class_id: int, student_id: int):
    # 检查班级是否存在
    if not data_store.get_class(class_id):
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 检查学生是否存在
    if not data_store.get_student(student_id):
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 添加学生到班级
    if not data_store.add_student_to_class(student_id, class_id):
        raise HTTPException(status_code=400, detail="学生已在班级中或添加失败")
    
    return {"message": "学生添加成功"}

@class_router.put("/{class_id}", response_model=ClassOut)
async def update_class(
    class_id: int, 
    update_data: ClassUpdate,
    current_user: Dict = Depends(get_current_teacher)
):
    
    updated_class = data_store.update_class(class_id, update_data)
    if not updated_class:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    return updated_class

@class_router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    current_user: Dict = Depends(get_current_teacher)
):
      
    if not data_store.delete_class(class_id):
        raise HTTPException(status_code=404, detail="班级不存在")
    
    return {"message": "删除班级成功"}

@class_router.delete("/{class_id}/removestudent/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_student_from_class(
    class_id: int, 
    student_id: int,
    current_user: Dict = Depends(get_current_teacher)
):    
    # 检查班级是否存在
    if not data_store.get_class(class_id):
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 检查学生是否存在
    if not data_store.get_student(student_id):
        raise HTTPException(status_code=404, detail="学生不存在")

    # 从班级中删除学生
    if not data_store.remove_student_from_class(student_id, class_id):
        raise HTTPException(status_code=400, detail="学生不在班级中")

    return {"message": "删除学生成功"}

# === 权限管理端点 ===
@api_router.get("/users/{user_id}/permissions", response_model=List[PermissionBase])
async def get_user_permissions(user_id: int):
    permissions = data_store.get_user_permissions(user_id)
    return permissions

@api_router.post("/users/{user_id}/permissions", status_code=status.HTTP_201_CREATED)
async def assign_permission(user_id: int, permission: PermissionAssign):
    # 检查用户是否存在
    if not data_store.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="用户不存在")

    # 分配权限
    if not data_store.assign_permission_to_user(user_id, permission.permission_id):
        raise HTTPException(status_code=400, detail="权限已分配或分配失败")
    
    return {"message": "权限分配成功"}

# === 成绩管理端点 ===
@api_router.put("/courses/{course_id}/grades/{student_id}", status_code=status.HTTP_200_OK)
async def record_grade(
    course_id: int, 
    student_id: int, 
    grade: GradeUpdate,
    current_user: Dict = Depends(get_current_teacher)
):
    # 更新成绩
    if not data_store.record_grade(student_id, course_id, grade.grade):
        raise HTTPException(status_code=500, detail="成绩更新失败")
    
    return {"message": "成绩更新成功"}

@api_router.get("/students/{student_id}/transcript", response_model=List[Dict])
async def get_student_transcript(student_id: int):
    # 检查学生是否存在
    if not data_store.get_student(student_id):
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 获取学生成绩单
    transcript = data_store.get_student_courses(student_id)
    
    # 添加课程信息
    result = []
    for course in transcript:
        course_info = data_store.get_course(course["course_id"])
        if course_info:
            result.append({
                "course_id": course_info["course_id"],
                "course_name": course_info["course_name"],
                "credit": course_info["credit"],
                "grade": course["grade"]
            })
    
    return result

# === 文件管理端点 ===
@file_router.post("/submissions/upload", response_model=SubmissionOut)
async def upload_submission(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_student)
):
    """
    学生提交作业文件
    - 保存文件到上传目录
    - 创建提交记录到数据库
    - 返回提交信息
    """
    # 获取学生信息
    student = data_store.get_student_by_user_id(current_user["user_id"])
    if not student:
        raise HTTPException(status_code=404, detail="学生信息不存在")
    
    student_id = student["student_id"]
    
    # 检查作业是否存在
    assignment = data_store.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"assignment_{assignment_id}_student_{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
    file_path = os.path.join(data_store.upload_dir, unique_filename)
    
    # 保存文件
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    finally:
        await file.close()
    
    # 创建提交记录
    submission_data = {
        "student_id": student_id,
        "assignment_id": assignment_id,
        "submit_time": datetime.now(),
        "file_path": file_path
    }
    
    try:
        submission = data_store.create_submission(submission_data)
        return {
            "submission_id": submission["submission_id"],
            "student_id": submission["student_id"],
            "assignment_id": submission["assignment_id"],
            "submit_time": submission["submit_time"],
            "file_path": os.path.basename(submission["file_path"])
        }
    except Exception as e:
        # 如果数据库操作失败，删除已保存的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"创建提交记录失败: {str(e)}")

@file_router.get("/submissions/my", response_model=List[SubmissionOut])
async def get_my_submissions(
    current_user: Dict = Depends(get_current_student)
):
    """学生查看自己所有的作业提交"""
    # 获取学生信息
    student = data_store.get_student_by_user_id(current_user["user_id"])
    if not student:
        raise HTTPException(status_code=404, detail="学生信息不存在")
    
    student_id = student["student_id"]
    
    submissions = data_store.get_submissions_by_student(student_id)
    
    # 只返回文件名
    for sub in submissions:
        sub["file_path"] = os.path.basename(sub["file_path"])
    
    return submissions

@file_router.get("/submissions/all", response_model=List[SubmissionOut])
async def get_all_submissions(
    current_user: Dict = Depends(get_current_teacher)
):
    """教师查看所有学生的作业提交"""
    submissions = data_store.get_all_submissions()
    
    # 只返回文件名
    for sub in submissions:
        sub["file_path"] = os.path.basename(sub["file_path"])
    
    return submissions

@file_router.get("/submissions/download/{submission_id}")
async def download_submission(
    submission_id: int,
    current_user: Dict = Depends(get_current_user)
):
    """
    下载提交的文件
    - 学生只能下载自己的文件
    - 教师可以下载所有文件
    """
    # 获取提交记录
    submission = data_store.get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    
    # 权限检查
    student = data_store.get_student_by_user_id(current_user["user_id"])
    teacher = data_store.get_teacher_by_user_id(current_user["user_id"])
    
    if student:
        if student["student_id"] != submission["student_id"]:
            raise HTTPException(status_code=403, detail="无权访问此文件")
    elif not teacher:
        raise HTTPException(status_code=403, detail="无权访问此文件")
    
    file_path = submission["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )

@file_router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: int,
    current_user: Dict = Depends(get_current_user)
):
    """
    删除提交记录及对应文件
    - 学生只能删除自己的提交
    - 教师可以删除任何提交
    """
    # 获取提交记录
    submission = data_store.get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    
    # 权限检查
    student = data_store.get_student_by_user_id(current_user["user_id"])
    teacher = data_store.get_teacher_by_user_id(current_user["user_id"])
    
    if student:
        # 学生只能删除自己的提交
        if student["student_id"] != submission["student_id"]:
            raise HTTPException(status_code=403, detail="无权删除此提交")
    elif not teacher:
        # 既不是学生也不是教师
        raise HTTPException(status_code=403, detail="无权删除此提交")
    
    # 删除文件
    file_path = submission["file_path"]
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")
    
    # 删除数据库记录
    if not data_store.delete_submission(submission_id):
        raise HTTPException(status_code=500, detail="删除提交记录失败")
    
    return {"message": "提交记录及文件已成功删除"}

# === 其他端点 ===
@api_router.get("/api")
def api_status():
    """API 状态检查"""
    return {"message": "API 工作正常"}

@api_router.get("/")
def root():
    """根端点"""
    return {"message": "欢迎使用学生管理系统 API"}

@api_router.get("/users/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    student = data_store.get_student_by_user_id(user_id)
    teacher = data_store.get_teacher_by_user_id(user_id)
    is_student = student is not None
    is_teacher = teacher is not None
    return {
        "user_id": user_id,
        "username": current_user["username"],
        "is_student": is_student,
        "is_teacher": is_teacher,
        "student_id": student["student_id"] if student else None,
        "teacher_id": teacher["teacher_id"] if teacher else None
    }

# === 应用实例 ===
app = FastAPI(
    title="学生管理系统 API",
    description="学生信息及汇报管理",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi.middleware.cors import CORSMiddleware

# 添加CORS中间件 - 允许所有源访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

app.include_router(api_router)
app.include_router(stu_router, prefix="/stu", tags=["学生管理"])
app.include_router(tea_router, prefix="/tea", tags=["教师管理"])
app.include_router(course_router, prefix="/course", tags=["课程管理"])
app.include_router(assign_router, prefix="/assign", tags=["作业管理"])
app.include_router(file_router, prefix="/files", tags=["文件管理"])
app.include_router(class_router, prefix='/classes', tags=["班级管理"])
app.include_router(user_router, prefix='/user', tags=["用户管理"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# === 运行入口 ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)