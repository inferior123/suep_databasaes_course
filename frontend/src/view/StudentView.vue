<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';
import { FASTAPI_BASE_URL } from '../constants';
import Navbar from '../components/NavBar.vue';

const AuthStore = useAuthStore();
const studentInfo = ref(null);
const courses = ref([]);
const submissions = ref([]);
const error = ref('');
const activeTab = ref('info');

// 选课相关
const allCourses = ref([]);
const enrolling = ref(false);
const enrollMsg = ref('');

// 作业提交相关
const assignments = ref([]);
const uploading = ref(false);
const uploadMsg = ref('');
const selectedFile = ref(null);
const selectedAssignmentId = ref(null);

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

// 获取当前学生详细信息
const fetchStudentInfo = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const userInfo = await axios.get(`${FASTAPI_BASE_URL}/users/me`, { headers: { Authorization: `Bearer ${token}` } });
    const studentId = userInfo.data.student_id;
    if (studentId) {
      const res = await axios.get(`${FASTAPI_BASE_URL}/stu/students/${studentId}`, { headers: { Authorization: `Bearer ${token}` } });
      studentInfo.value = res.data;
      courses.value = res.data.courses || [];
    }
  } catch (e) {
    error.value = e.message || '获取学生信息失败';
  }
};

// 获取作业提交历史
const fetchSubmissions = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const res = await axios.get(`${FASTAPI_BASE_URL}/files/submissions/my`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    submissions.value = res.data;
  } catch (e) {
    error.value = e.message || '获取作业提交失败';
  }
};

// 获取所有课程
const fetchAllCourses = async () => {
  try {
    const res = await axios.get(`${FASTAPI_BASE_URL}/course/courses/`);
    allCourses.value = res.data;
  } catch (e) {
    enrollMsg.value = e.message || '获取课程失败';
  }
};

// 选课
const enrollCourse = async (courseId) => {
  enrolling.value = true;
  enrollMsg.value = '';
  try {
    const token = localStorage.getItem('access_token');
    await axios.post(`${FASTAPI_BASE_URL}/course/courses/${courseId}/enroll`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    enrollMsg.value = '选课成功！';
    fetchStudentInfo(); // 选课后刷新学生课程
  } catch (e) {
    enrollMsg.value = e.response?.data?.detail || e.message || '选课失败';
  } finally {
    enrolling.value = false;
  }
};

// 获取所有作业
const fetchAssignments = async () => {
  try {
    // 这里只获取所有课程的作业，实际可根据需求筛选
    const res = await axios.get(`${FASTAPI_BASE_URL}/assign/assignments/`);
    assignments.value = res.data;
  } catch (e) {
    uploadMsg.value = e.message || '获取作业失败';
  }
};

// 提交作业 - 修复后的版本
const submitAssignment = async () => {
  if (!selectedAssignmentId.value || !selectedFile.value) {
    uploadMsg.value = '请选择作业和文件';
    return;
  }
  uploading.value = true;
  uploadMsg.value = '';
  try {
    const token = localStorage.getItem('access_token');
    const formData = new FormData();
    formData.append('file', selectedFile.value);
    formData.append('assignment_id', selectedAssignmentId.value);
    
    // 使用正确的接口路径
    const res = await axios.post(
      `${FASTAPI_BASE_URL}/files/submissions/upload`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    uploadMsg.value = '提交成功！';
    // 清空表单
    selectedFile.value = null;
    selectedAssignmentId.value = null;
    fetchSubmissions(); // 提交后刷新提交历史
  } catch (e) {
    console.error('提交失败:', e);
    uploadMsg.value = e.response?.data?.detail || e.message || '提交失败';
  } finally {
    uploading.value = false;
  }
};

onMounted(() => {
  fetchStudentInfo();
  fetchSubmissions();
  fetchAllCourses();
  fetchAssignments();
});
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <Navbar />

    <main class="container mx-auto p-4 sm:p-6 lg:p-8">
      <div class="grid grid-cols-12 gap-6">
        
        <!-- Left Sidebar Card -->
        <div class="col-span-12 lg:col-span-3">
          <div class="bg-white rounded-lg shadow-md">
            <div class="p-4 border-b">
              <h2 class="text-lg font-semibold text-gray-800">学生中心</h2>
            </div>
            <nav class="p-2">
              <button
                @click="activeTab = 'info'"
                :class="[
                  'flex items-center w-full px-4 py-2.5 text-left text-sm font-medium rounded-lg transition-colors duration-200',
                  activeTab === 'info' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                  'relative'
                ]"
              >
                <span v-if="activeTab === 'info'" class="absolute left-0 top-0 bottom-0 w-1 bg-indigo-600 rounded-r-md"></span>
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                学生信息
              </button>
              <button
                @click="activeTab = 'course'"
                :class="[
                  'flex items-center w-full px-4 py-2.5 text-left text-sm font-medium rounded-lg transition-colors duration-200',
                  activeTab === 'course' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                  'relative'
                ]"
              >
                <span v-if="activeTab === 'course'" class="absolute left-0 top-0 bottom-0 w-1 bg-indigo-600 rounded-r-md"></span>
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v11.494m-9-5.747h18"></path></svg>
                选课管理
              </button>
              <button
                @click="activeTab = 'submit'"
                :class="[
                  'flex items-center w-full px-4 py-2.5 text-left text-sm font-medium rounded-lg transition-colors duration-200',
                  activeTab === 'submit' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                  'relative'
                ]"
              >
                <span v-if="activeTab === 'submit'" class="absolute left-0 top-0 bottom-0 w-1 bg-indigo-600 rounded-r-md"></span>
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                作业提交
              </button>
            </nav>
          </div>
        </div>

        <!-- Right Content Area -->
        <div class="col-span-12 lg:col-span-9">
          <!-- Student Info Section -->
          <div v-if="activeTab === 'info'" class="space-y-6">
            <div class="bg-white rounded-lg shadow-md">
              <div class="bg-indigo-600 text-white p-4 rounded-t-lg flex items-center space-x-3">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 012-2h2a2 2 0 012 2v1m-6 0h6"></path></svg>
                <h2 class="text-xl font-bold">学生信息中心</h2>
              </div>
              <div v-if="studentInfo" class="p-6">
                <div class="border-b pb-4 flex items-center space-x-2">
                  <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <h3 class="text-lg font-semibold text-gray-700">基本信息</h3>
                </div>
                <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-8 gap-y-6">
                  <div><p class="text-sm text-gray-500">学号</p><p class="text-lg font-semibold text-gray-800">{{ studentInfo.student_id }}</p></div>
                  <div><p class="text-sm text-gray-500">姓名</p><p class="text-lg font-semibold text-gray-800">{{ studentInfo.user?.username }}</p></div>
                  <div><p class="text-sm text-gray-500">年级</p><p class="text-lg font-semibold text-gray-800">{{ studentInfo.grade }}</p></div>
                  <div><p class="text-sm text-gray-500">专业</p><p class="text-lg font-semibold text-gray-800">{{ studentInfo.major }}</p></div>
                </div>
              </div>
               <div v-else class="text-center p-6 text-gray-500">正在加载学生信息...</div>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-4 border-b pb-2">课程与成绩</h3>
                <table class="w-full text-left text-sm">
                    <thead><tr class="bg-gray-50 text-gray-600"><th class="p-3">课程名</th><th class="p-3">学分</th><th class="p-3">成绩</th></tr></thead>
                    <tbody><tr v-for="course in courses" :key="course.course_id" class="border-b hover:bg-gray-50"><td class="p-3">{{ course.course_name }}</td><td class="p-3">{{ course.credit }}</td><td class="p-3 font-medium" :class="course.grade < 60 ? 'text-red-500' : 'text-green-600'">{{ course.grade ?? '未评分' }}</td></tr></tbody>
                </table>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-semibold text-gray-700 mb-4 border-b pb-2">作业提交历史</h3>
                <table class="w-full text-left text-sm">
                    <thead><tr class="bg-gray-50 text-gray-600"><th class="p-3">作业ID</th><th class="p-3">提交时间</th><th class="p-3">文件</th></tr></thead>
                    <tbody><tr v-for="sub in submissions" :key="sub.submission_id" class="border-b hover:bg-gray-50"><td class="p-3">{{ sub.assignment_id }}</td><td class="p-3">{{ sub.submit_time }}</td><td class="p-3"><a :href="`${FASTAPI_BASE_URL}/uploads/${sub.file_path}`" target="_blank" class="text-indigo-600 hover:underline">{{ sub.file_path }}</a></td></tr></tbody>
                </table>
            </div>
          </div>

          <!-- Course Enrollment Section -->
          <div v-if="activeTab === 'course'">
            <div class="bg-white rounded-lg shadow-md">
              <div class="p-4 border-b flex items-center space-x-3">
                 <h2 class="text-xl font-bold text-gray-800">选课管理</h2>
              </div>
              <div class="p-6">
                <div v-if="enrollMsg" class="mb-4 text-blue-600">{{ enrollMsg }}</div>
                <table class="w-full text-left">
                  <thead class="bg-gray-50 text-gray-600"><tr><th class="p-3">课程名</th><th class="p-3">学分</th><th class="p-3">操作</th></tr></thead>
                  <tbody><tr v-for="course in allCourses" :key="course.course_id" class="border-b hover:bg-gray-50"><td class="p-3">{{ course.course_name }}</td><td class="p-3">{{ course.credit }}</td><td class="p-3"><button class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400" :disabled="enrolling" @click="enrollCourse(course.course_id)">选课</button></td></tr></tbody>
                </table>
              </div>
            </div>
          </div>
          
          <!-- Assignment Submission Section -->
          <div v-if="activeTab === 'submit'">
            <div class="bg-white rounded-lg shadow-md">
                <div class="p-4 border-b flex items-center space-x-3">
                  <h2 class="text-xl font-bold text-gray-800">提交作业</h2>
                </div>
                <div class="p-6 max-w-lg mx-auto">
                    <div v-if="uploadMsg" class="mb-4 text-blue-600">{{ uploadMsg }}</div>
                    <form @submit.prevent="submitAssignment" class="space-y-6">
                        <div>
                            <label for="assignment-select" class="block text-sm font-medium text-gray-700 mb-1">选择作业</label>
                            <select id="assignment-select" v-model="selectedAssignmentId" class="w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"><option disabled value="">请选择一个作业</option><option v-for="a in assignments" :key="a.assignment_id" :value="a.assignment_id">ID: {{ a.assignment_id }} - {{ a.content }}</option></select>
                        </div>
                        <div>
                            <label for="file-upload" class="block text-sm font-medium text-gray-700 mb-1">上传文件</label>
                            <input id="file-upload" type="file" @change="handleFileChange" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"/>
                        </div>
                        <button type="submit" class="w-full px-4 py-2 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-gray-400" :disabled="uploading">{{ uploading ? '提交中...' : '确认提交' }}</button>
                    </form>
                </div>
            </div>
          </div>
        </div>
        
      </div>
    </main>
  </div>
</template>