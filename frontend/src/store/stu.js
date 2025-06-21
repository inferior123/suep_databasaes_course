// store/stu.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {FASTAPI_BASE_URL} from '../constants.js'
import axios from 'axios'

const api = axios.create({
  baseURL: FASTAPI_BASE_URL,
  withCredentials: true,
})

export const useStuStore = defineStore('student', () => {
  const currentStudentId = ref(null)
  
  // 获取学生信息
  const getStudentInfo = async () => {
    try {
      const response = await api.get(`/students/${currentStudentId.value}`)
      return response.data
    } catch (error) {
      throw new Error('获取学生信息失败')
    }
  }
  
  // 获取学生课程（从学生信息中提取课程数据）
  const getStudentCourses = async () => {
    try {
      const response = await api.get(`/students/${currentStudentId.value}`)
      return response.data.courses || []
    } catch (error) {
      throw new Error('获取学生课程失败')
    }
  }
  
  // 获取所有课程
  const getAllCourses = async () => {
    try {
      const response = await api.get('/courses')
      return response.data
    } catch (error) {
      throw new Error('获取所有课程失败')
    }
  }
  
  // 学生选课
  const enrollCourse = async (courseId) => {
    try {
      // 移除了URL中的学生ID，后端从token获取当前用户
      await api.post(`/courses/${courseId}/enroll`)
      return true
    } catch (error) {
      throw new Error(error.response?.data?.detail || '选课失败')
    }
  }
  
  // 获取学生作业（重构为符合后端API）
  const getStudentAssignments = async () => {
    try {
      // 1. 获取学生所有课程
      const courses = await getStudentCourses()
      
      // 2. 获取所有课程的作业
      const assignmentsRequests = courses.map(course => 
        api.get(`/courses/${course.course_id}/assignments`)
      )
      
      const assignmentsResponses = await Promise.all(assignmentsRequests)
      let allAssignments = []
      assignmentsResponses.forEach(response => {
        allAssignments = [...allAssignments, ...response.data]
      })
      
      // 3. 获取学生的所有提交记录
      const submissionsResponse = await api.get('/submissions/my')
      const submissions = submissionsResponse.data
      
      // 4. 处理作业状态
      const now = new Date()
      return allAssignments.map(assignment => {
        const dueDate = new Date(assignment.due_date)
        const submission = submissions.find(s => s.assignment_id === assignment.assignment_id)
        
        let status = '进行中'
        if (submission) {
          status = '已提交'
        } else if (now > dueDate) {
          status = '已逾期'
        }
        
        return {
          ...assignment,
          status,
          submitted: !!submission,
          submission_id: submission?.submission_id
        }
      })
    } catch (error) {
      throw new Error('获取作业失败: ' + error.message)
    }
  }
  
  // 获取学生成绩单
  const getStudentTranscript = async () => {
    try {
      const response = await api.get(`/students/${currentStudentId.value}/transcript`)
      return response.data
    } catch (error) {
      throw new Error('获取成绩单失败')
    }
  }
  
  // 提交作业
  const submitAssignment = async (assignmentId, file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post(
        `/assignments/${assignmentId}/submit`, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || '作业提交失败')
    }
  }
  
  // 获取学生提交记录
  const getStudentSubmissions = async () => {
    try {
      const response = await api.get('/submissions/my')
      return response.data
    } catch (error) {
      throw new Error('获取提交记录失败')
    }
  }
  
  // 下载作业文件
  const downloadSubmission = async (submissionId) => {
    try {
      const response = await api.get(`/submissions/download/${submissionId}`, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw new Error('下载作业失败')
    }
  }

  return {
    currentStudentId,
    getStudentInfo,
    getStudentCourses,
    getAllCourses,
    enrollCourse,
    getStudentAssignments,
    getStudentTranscript,
    submitAssignment,
    getStudentSubmissions,
    downloadSubmission
  }
})