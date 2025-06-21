from fastapi import UploadFile
from typing import List, Optional, Dict, Any, Union
from contextlib import contextmanager
from sqlalchemy.orm import Session
import os
import uuid
import shutil
from typing import Generator

from models import (
    Student, Teacher, Class, Permission, Course, Assignment, Submission,
    UserPermission, StudentClass, TeacherClass, TeacherCourse, StudentCourse
)
from models import User as model_user
from db import SessionLocal
from schemas import *

# === 数据存储抽象层 ===
class DataStore:

    def __init__(self):
        # 文件存储目录
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # === 用户相关方法 ===
    def get_user(self, username: str) -> Optional[Dict]:
        with self.get_db_session() as db:
            user = db.query(model_user).filter(model_user.username == username).first()
            if user:
                return {
                    "user_id": user.user_id,
                    "username": user.username,
                    "password": user.password,
                    "email": user.email,
                    "disabled": False
                }
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        with self.get_db_session() as db:
            user = db.query(model_user).filter(model_user.user_id == user_id).first()
            if user:
                return {
                    "user_id": user.user_id,
                    "username": user.username,
                    "password": user.password,
                    "email": user.email,
                    "disabled": False
                }
            return None
    
    def authenticate_user(self, username: str, password: str) -> Union[Dict, bool]:
        user = self.get_user(username)
        if not user or user["password"] != password:
            return False
        return user
    
    def create_user(self, user_data) -> Dict:
        with self.get_db_session() as db:
            new_user = model_user(
                username=user_data.username,
                password=user_data.password,
                email=user_data.email
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return {
                "user_id": new_user.user_id,
                "username": new_user.username,
                "password": new_user.password,
                "email": new_user.email,
                "disabled": False
            }
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """通过用户名获取用户 - 这是你代码中已有的方法"""
        return self.get_user(username)
    
    # === 学生相关方法 ===
    def get_student(self, student_id: int) -> Optional[Dict]:
        with self.get_db_session() as db:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if student:
                return {
                    "student_id": student.student_id,
                    "grade": student.grade,
                    "major": student.major,
                    "user_id": student.user_id
                }
            return None
    
    def get_students(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        with self.get_db_session() as db:
            students = db.query(Student).offset(skip).limit(limit).all()
            return [{
                "student_id": s.student_id,
                "grade": s.grade,
                "major": s.major,
                "user_id": s.user_id
            } for s in students]
    
    def create_student(self, student_data) -> Dict:
        # 创建用户
        user_data = student_data.user
        new_user = self.create_user(user_data)
        
        with self.get_db_session() as db:
            # 创建学生
            student = Student(
                grade=student_data.grade,
                major=student_data.major,
                user_id=new_user["user_id"]
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            
            return {
                "student_id": student.student_id,
                "grade": student.grade,
                "major": student.major,
                "user_id": student.user_id
            }
    
    def update_student(self, student_id: int, update_data) -> Dict:
        with self.get_db_session() as db:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return None
            
            if update_data.grade:
                student.grade = update_data.grade
            if update_data.major:
                student.major = update_data.major
            
            db.commit()
            db.refresh(student)
            
            return {
                "student_id": student.student_id,
                "grade": student.grade,
                "major": student.major,
                "user_id": student.user_id
            }
    
    def get_student_by_user_id(self, user_id: int) -> Optional[Dict]:
        """通过用户ID获取学生信息"""
        with self.get_db_session() as db:
            student = db.query(Student).filter(Student.user_id == user_id).first()
            if student:
                return {
                    "student_id": student.student_id,
                    "grade": student.grade,
                    "major": student.major,
                    "user_id": student.user_id
                }
            return None
    
    # === 教师相关方法 ===
    def get_teacher(self, teacher_id: int) -> Optional[Dict]:
        with self.get_db_session() as db:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if teacher:
                return {
                    "teacher_id": teacher.teacher_id,
                    "title": teacher.title,
                    "department": teacher.department,
                    "user_id": teacher.user_id
                }
            return None
    
    def get_teachers(self) -> List[Dict]:
        with self.get_db_session() as db:
            teachers = db.query(Teacher).all()
            return [{
                "teacher_id": t.teacher_id,
                "title": t.title,
                "department": t.department,
                "user_id": t.user_id
            } for t in teachers]
    
    def create_teacher(self, teacher_data) -> Dict:
        # 创建用户
        user_data = teacher_data.user
        new_user = self.create_user(user_data)
        
        with self.get_db_session() as db:
            # 创建教师
            teacher = Teacher(
                title=teacher_data.title,
                department=teacher_data.department,
                user_id=new_user["user_id"]
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            
            return {
                "teacher_id": teacher.teacher_id,
                "title": teacher.title,
                "department": teacher.department,
                "user_id": teacher.user_id
            }
    
    def get_teacher_by_user_id(self, user_id: int) -> Optional[Dict]:
        """通过用户ID获取教师信息"""
        with self.get_db_session() as db:
            teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
            if teacher:
                return {
                    "teacher_id": teacher.teacher_id,
                    "title": teacher.title,
                    "department": teacher.department,
                    "user_id": teacher.user_id
                }
            return None
    
    # === 课程相关方法 ===
    def get_course(self, course_id: int) -> Optional[Dict]:
        with self.get_db_session() as db:
            course = db.query(Course).filter(Course.course_id == course_id).first()
            if course:
                return {
                    "course_id": course.course_id,
                    "course_name": course.course_name,
                    "credit": course.credit
                }
            return None
    
    def get_courses(self) -> List[Dict]:
        with self.get_db_session() as db:
            courses = db.query(Course).all()
            return [{
                "course_id": c.course_id,
                "course_name": c.course_name,
                "credit": c.credit
            } for c in courses]
    
    def create_course(self, course_data, teacher_id) -> Dict:
        with self.get_db_session() as db:
            course = Course(
                course_name=course_data.course_name,
                credit=course_data.credit
            )
            db.add(course)
            db.commit()
            db.refresh(course)

            teachercourse = TeacherCourse(
                teacher_id = teacher_id,
                course_id = course.course_id
            )
            db.add(teachercourse)
            db.commit()
            db.refresh(teachercourse)

            return {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "credit": course.credit
            }
    
    # === 作业相关方法 ===
    def get_assignment(self, assignment_id: int) -> Optional[Dict]:
        with self.get_db_session() as db:
            assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
            if assignment:
                return {
                    "assignment_id": assignment.assignment_id,
                    "content": assignment.content,
                    "deadline": assignment.deadline,
                    "status": assignment.status,
                    "teacher_id": assignment.teacher_id
                }
            return None
    
    def create_assignment(self, assignment_data) -> Dict:
        with self.get_db_session() as db:
            assignment = Assignment(
                content=assignment_data.content,
                deadline=assignment_data.deadline,
                status=assignment_data.status,
                teacher_id=assignment_data.teacher_id
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            return {
                "assignment_id": assignment.assignment_id,
                "content": assignment.content,
                "deadline": assignment.deadline,
                "status": assignment.status,
                "teacher_id": assignment.teacher_id
            }
    
    def create_submission(self, submission_data: Dict) -> Dict:
        with self.get_db_session() as db:
            submission = Submission(
                student_id=submission_data["student_id"],
                assignment_id=submission_data["assignment_id"],
                submit_time=submission_data["submit_time"],
                file_path=submission_data["file_path"]
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)
            return {
                "submission_id": submission.submission_id,
                "student_id": submission.student_id,
                "assignment_id": submission.assignment_id,
                "submit_time": submission.submit_time,
                "file_path": submission.file_path
            }
    
    # === 文件处理方法 ===
    def save_upload_file(self, file: UploadFile) -> str:
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, file_name)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return f"/uploads/{file_name}"
    
    # === 关系操作方法 ===
    def get_student_classes(self, student_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return []
            
            return [{
                "class_id": c.class_id,
                "class_name": c.class_name,
                "grade": c.grade
            } for c in student.classes]
    
    def get_student_courses(self, student_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            # 直接查询关联表和课程表
            results = db.query(
                Course.course_id,
                Course.course_name,
                Course.credit,
                StudentCourse.grade
            ).join(
                StudentCourse, 
                StudentCourse.course_id == Course.course_id
            ).filter(
                StudentCourse.student_id == student_id
            ).all()
            
            return [{
                "course_id": r.course_id,
                "course_name": r.course_name,
                "credit": r.credit,
                "grade": r.grade
            } for r in results]
    
    def get_teacher_classes(self, teacher_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return []
            
            return [{
                "class_id": c.class_id,
                "class_name": c.class_name,
                "grade": c.grade
            } for c in teacher.classes]
    
    def get_course_students(self, course_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            # 查询课程信息
            course = db.query(Course).filter(Course.course_id == course_id).first()
            if not course:
                return []
            
            # 查询选课学生及成绩
            results = db.query(
                Student.student_id,
                Student.major,
                StudentCourse.grade,
                Course.course_id,  
                Course.course_name 
            ).join(
                StudentCourse, StudentCourse.student_id == Student.student_id
            ).join(
                model_user, Student.user_id == model_user.user_id
            ).join(
                Course, StudentCourse.course_id == Course.course_id
            ).filter(
                StudentCourse.course_id == course_id
            ).all()
            
            return [{
                "student_id": r.student_id,
                "major": r.major,
                "grade": r.grade,
                "course_id": r.course_id,
                "course_name": r.course_name
            } for r in results]
    
    def get_class_students(self, class_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            class_ = db.query(Class).filter(Class.class_id == class_id).first()
            if not class_:
                return []
            
            return [{
                "student_id": s.student_id,
                "grade": s.grade,
                "major": s.major,
                "user_id": s.user_id
            } for s in class_.students]
    
    def get_user_permissions(self, user_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            user = db.query(model_user).filter(model_user.user_id == user_id).first()
            if not user:
                return []
            
            return [{
                "permission_id": p.permission_id,
                "permission_name": p.permission_name,
                "description": p.description
            } for p in user.permissions]
    
    def get_submissions_by_student(self, student_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return []
            
            return [{
                "submission_id": s.submission_id,
                "student_id": s.student_id,
                "assignment_id": s.assignment_id,
                "submit_time": s.submit_time,
                "file_path": s.file_path
            } for s in student.submissions]
    
    def get_all_submissions(self) -> List[Dict]:
        with self.get_db_session() as db:
            submissions = db.query(Submission).all()
            return [{
                "submission_id": s.submission_id,
                "student_id": s.student_id,
                "assignment_id": s.assignment_id,
                "submit_time": s.submit_time,
                "file_path": s.file_path
            } for s in submissions]
    
    def get_submission_by_id(self, submission_id: int) -> Optional[Dict]:
        with self.get_db_session() as db:
            submission = db.query(Submission).filter(Submission.submission_id == submission_id).first()
            if submission:
                return {
                    "submission_id": submission.submission_id,
                    "student_id": submission.student_id,
                    "assignment_id": submission.assignment_id,
                    "submit_time": submission.submit_time,
                    "file_path": submission.file_path
                }
            return None
    
    def delete_submission(self, submission_id: int) -> bool:
        with self.get_db_session() as db:
            submission = db.query(Submission).filter(Submission.submission_id == submission_id).first()
            if not submission:
                return False
            
            db.delete(submission)
            db.commit()
            return True

    def enroll_student_in_course(self, student_id: int, course_id: int, grade: float = None):
        with self.get_db_session() as db:
            # 检查是否已选课
            existing = db.query(StudentCourse).filter(
                StudentCourse.student_id == student_id,
                StudentCourse.course_id == course_id
            ).first()
            
            if existing:
                return False
            
            enrollment = StudentCourse(
                student_id=student_id,
                course_id=course_id,
                grade=grade
            )
            db.add(enrollment)
            db.commit()
            return True

    def add_student_to_class(self, student_id: int, class_id: int):
        with self.get_db_session() as db:
            # 检查是否已在班级中
            existing = db.query(StudentClass).filter(
                StudentClass.student_id == student_id,
                StudentClass.class_id == class_id
            ).first()
            
            if existing:
                return False
            
            enrollment = StudentClass(
                student_id=student_id,
                class_id=class_id
            )
            db.add(enrollment)
            db.commit()
            return True

    def assign_permission_to_user(self, user_id: int, permission_id: int):
        with self.get_db_session() as db:
            # 检查是否已分配
            existing = db.query(UserPermission).filter(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission_id
            ).first()
            
            if existing:
                return False
            
            assignment = UserPermission(
                user_id=user_id,
                permission_id=permission_id
            )
            db.add(assignment)
            db.commit()
            return True

    def record_grade(self, student_id: int, course_id: int, grade: float):
        with self.get_db_session() as db:
            # 查找选课记录
            enrollment = db.query(StudentCourse).filter(
                StudentCourse.student_id == student_id,
                StudentCourse.course_id == course_id
            ).first()
            
            if enrollment:
                enrollment.grade = grade
                db.commit()
                return True
            
            # 如果找不到，创建新记录
            new_enrollment = StudentCourse(
                student_id=student_id,
                course_id=course_id,
                grade=grade
            )
            db.add(new_enrollment)
            db.commit()
            return True
    
    def get_class(self, class_id: int) -> Optional[Dict]:
        with self.get_db_session() as db:
            class_ = db.query(Class).filter(Class.class_id == class_id).first()
            if class_:
                return {
                    "class_id": class_.class_id,
                    "class_name": class_.class_name,
                    "grade": class_.grade
                }
            return None
    
    def create_class(self, class_data: ClassCreate) -> Dict:
        with self.get_db_session() as db:
            new_class = Class(
                class_name=class_data.class_name,
                grade=class_data.grade
            )
            db.add(new_class)
            db.commit()
            db.refresh(new_class)
            return {
                "class_id": new_class.class_id,
                "class_name": new_class.class_name,
                "grade": new_class.grade
            }
    
    def get_assignments_by_course(self, course_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            assignments = db.query(Assignment).join(Teacher).join(TeacherCourse).filter(
                TeacherCourse.course_id == course_id
            ).all()
            
            return [{
                "assignment_id": a.assignment_id,
                "content": a.content,
                "deadline": a.deadline,
                "status": a.status,
                "teacher_id": a.teacher_id
            } for a in assignments]
    
    def get_submissions_by_assignment(self, assignment_id: int) -> List[Dict]:
        with self.get_db_session() as db:
            submissions = db.query(Submission).filter(
                Submission.assignment_id == assignment_id
            ).all()
            
            return [{
                "submission_id": s.submission_id,
                "student_id": s.student_id,
                "assignment_id": s.assignment_id,
                "submit_time": s.submit_time,
                "file_path": s.file_path
            } for s in submissions]

    def update_teacher(self, teacher_id: int, update_data: TeacherUpdate) -> Optional[Dict]:
        with self.get_db_session() as db:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return None
            
            # 更新教师信息
            if update_data.title:
                teacher.title = update_data.title
            if update_data.department:
                teacher.department = update_data.department
            
            db.commit()
            db.refresh(teacher)
            
            return {
                "teacher_id": teacher.teacher_id,
                "title": teacher.title,
                "department": teacher.department,
                "user_id": teacher.user_id
            }

    def delete_teacher(self, teacher_id: int) -> bool:
        with self.get_db_session() as db:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                return False
            
            # 删除关联关系
            # 1. 删除教师-班级关联
            db.query(TeacherClass).filter(TeacherClass.teacher_id == teacher_id).delete()
            
            # 2. 删除教师-课程关联
            db.query(TeacherCourse).filter(TeacherCourse.teacher_id == teacher_id).delete()
            
            # 3. 删除教师创建的作业（可选，根据业务需求决定）
            # 如果需要保留作业，可以设置 teacher_id 为 NULL 或转移给其他教师
            # 这里选择删除作业及其提交记录
            assignment_ids = [a.assignment_id for a in db.query(Assignment).filter(
                Assignment.teacher_id == teacher_id
            ).all()]
            
            # 删除作业相关的提交
            db.query(Submission).filter(
                Submission.assignment_id.in_(assignment_ids)
            ).delete()
            
            # 删除作业
            db.query(Assignment).filter(
                Assignment.teacher_id == teacher_id
            ).delete()
            
            # 获取用户ID以便后续删除用户
            user_id = teacher.user_id
            
            # 删除教师记录
            db.delete(teacher)
            db.commit()
            
            # 删除关联的用户（可选，根据业务需求）
            # 如果需要保留用户账号，可以跳过此步骤
            user = db.query(model_user).filter(model_user.user_id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
            
            return True

    # === 新增班级管理方法 ===
    def update_class(self, class_id: int, update_data: ClassUpdate) -> Optional[Dict]:
        with self.get_db_session() as db:
            class_ = db.query(Class).filter(Class.class_id == class_id).first()
            if not class_:
                return None
            
            # 更新班级信息
            if update_data.class_name:
                class_.class_name = update_data.class_name
            if update_data.grade:
                class_.grade = update_data.grade
            
            db.commit()
            db.refresh(class_)
            
            return {
                "class_id": class_.class_id,
                "class_name": class_.class_name,
                "grade": class_.grade
            }

    def delete_class(self, class_id: int) -> bool:
        with self.get_db_session() as db:
            class_ = db.query(Class).filter(Class.class_id == class_id).first()
            if not class_:
                return False
            
            # 删除关联关系
            # 1. 删除学生-班级关联
            db.query(StudentClass).filter(StudentClass.class_id == class_id).delete()
            
            # 2. 删除教师-班级关联
            db.query(TeacherClass).filter(TeacherClass.class_id == class_id).delete()
            
            # 删除班级记录
            db.delete(class_)
            db.commit()
            return True

    def remove_student_from_class(self, student_id: int, class_id: int) -> bool:
        with self.get_db_session() as db:
            # 检查学生是否在班级中
            enrollment = db.query(StudentClass).filter(
                StudentClass.student_id == student_id,
                StudentClass.class_id == class_id
            ).first()
            
            if not enrollment:
                return False
            
            # 删除关联记录
            db.delete(enrollment)
            db.commit()
            return True

    def get_assignments(self) -> List[Dict]:
        with self.get_db_session() as db:
            assignments = db.query(Assignment).all()
            return [{
                "assignment_id": a.assignment_id,
                "content": a.content,
                "deadline": a.deadline,
                "status": a.status,
                "teacher_id": a.teacher_id
            } for a in assignments]