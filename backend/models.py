from datetime import datetime
from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, Text, ForeignKey, String
from sqlalchemy import Float
from sqlalchemy.orm import relationship

from db import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    # 关系定义
    permissions = relationship("Permission", secondary="user_permission", back_populates="users")
    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = "student"
    
    student_id = Column(Integer, primary_key=True)
    grade = Column(String(20), nullable=False)
    major = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # 关系定义
    user = relationship("User", back_populates="student")
    classes = relationship("Class", secondary="student_class", back_populates="students")
    courses = relationship("Course", secondary="student_course", back_populates="students")
    submissions = relationship("Submission", back_populates="student")

class Teacher(Base):
    __tablename__ = "teacher"
    
    teacher_id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    department = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # 关系定义
    user = relationship("User", back_populates="teacher")
    classes = relationship("Class", secondary="teacher_class", back_populates="teachers")
    courses = relationship("Course", secondary="teacher_course", back_populates="teachers")
    assignments = relationship("Assignment", back_populates="teacher")

class Class(Base):
    __tablename__ = "class"
    
    class_id = Column(Integer, primary_key=True)
    class_name = Column(String(50), nullable=False)
    grade = Column(String(20), nullable=False)
    
    # 关系定义
    students = relationship("Student", secondary="student_class", back_populates="classes")
    teachers = relationship("Teacher", secondary="teacher_class", back_populates="classes")

class Permission(Base):
    __tablename__ = "permission"
    
    permission_id = Column(Integer, primary_key=True)
    permission_name = Column(String(50), nullable=False)
    description = Column(Text)
    
    # 关系定义
    users = relationship("User", secondary="user_permission", back_populates="permissions")

class Course(Base):
    __tablename__ = "course"
    
    course_id = Column(Integer, primary_key=True)
    course_name = Column(String(100), nullable=False)
    credit = Column(Integer, nullable=False)
    
    # 关系定义
    students = relationship("Student", secondary="student_course", back_populates="courses")
    teachers = relationship("Teacher", secondary="teacher_course", back_populates="courses")

class Assignment(Base):
    __tablename__ = "assignment"
    
    assignment_id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    deadline = Column(TIMESTAMP, nullable=False)
    status = Column(String(20), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"))
    
    # 关系定义
    teacher = relationship("Teacher", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submission"
    
    submission_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student.student_id"))
    assignment_id = Column(Integer, ForeignKey("assignment.assignment_id"))
    submit_time = Column(TIMESTAMP, default=datetime.utcnow)
    file_path = Column(String(200), nullable=False)
    
    # 关系定义
    student = relationship("Student", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")

# 关联表模型（用于多对多关系）
class UserPermission(Base):
    __tablename__ = "user_permission"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permission.permission_id"), primary_key=True)

class StudentClass(Base):
    __tablename__ = "student_class"
    student_id = Column(Integer, ForeignKey("student.student_id"), primary_key=True)
    class_id = Column(Integer, ForeignKey("class.class_id"), primary_key=True)

class TeacherClass(Base):
    __tablename__ = "teacher_class"
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"), primary_key=True)
    class_id = Column(Integer, ForeignKey("class.class_id"), primary_key=True)

class TeacherCourse(Base):
    __tablename__ = "teacher_course"
    teacher_id = Column(Integer, ForeignKey("teacher.teacher_id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("course.course_id"), primary_key=True)

class StudentCourse(Base):
    __tablename__ = "student_course"
    student_id = Column(Integer, ForeignKey("student.student_id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("course.course_id"), primary_key=True)
    grade = Column(Float)