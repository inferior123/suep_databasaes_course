<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';
import { FASTAPI_BASE_URL } from '../constants';
import Navbar from '../components/NavBar.vue';

const AuthStore = useAuthStore();
const teacherInfo = ref(null);
const error = ref('');
const activeTab = ref('info'); // 默认显示教师信息

// 发布作业
const newAssignment = ref({ content: '', deadline: '', status: 'open' });
const publishMsg = ref('');
const courses = ref([]);

// 学生作业
const allAssignments = ref([]);
const allSubmissions = ref([]);
const downloadMsg = ref('');

// 修改成绩
const gradeMsg = ref('');
const selectedSubmission = ref(null);
const newGrade = ref('');

// 创建课程
const newCourse = ref({ course_name: '', credit: '' });
const createCourseMsg = ref('');

// 获取教师信息
const fetchTeacherInfo = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const userInfo = await axios.get(`${FASTAPI_BASE_URL}/users/me`, { headers: { Authorization: `Bearer ${token}` } });
    const teacherId = userInfo.data.teacher_id;
    if (teacherId) {
      const res = await axios.get(`${FASTAPI_BASE_URL}/tea/teachers/${teacherId}`, { headers: { Authorization: `Bearer ${token}` } });
      teacherInfo.value = Array.isArray(res.data) ? res.data[0] : res.data;
    }
  } catch (e) {
    error.value = e.message || '获取教师信息失败';
  }
  fetchAllSubmissions();
};

// 获取课程列表
const fetchCourses = async () => {
  try {
    const res = await axios.get(`${FASTAPI_BASE_URL}/course/courses/`);
    courses.value = res.data;
  } catch (e) {}
};

// 发布作业
const publishAssignment = async () => {
  publishMsg.value = '';
  try {
    const token = localStorage.getItem('access_token');
    if (!newAssignment.value.content || !newAssignment.value.deadline || !newAssignment.value.status || !newAssignment.value.course_id) {
      publishMsg.value = '请填写完整信息';
      return;
    }
    // teacher_id 由后端自动获取，无需前端传递
    await axios.post(`${FASTAPI_BASE_URL}/assign/assignments/`, {
      ...newAssignment.value,
      teacher_id: teacherInfo.value.teacher_id
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    publishMsg.value = '发布成功！';
    fetchAllAssignments();
  } catch (e) {
    publishMsg.value = e.response?.data?.detail || e.message || '发布失败';
  }
};

// 获取所有作业
const fetchAllAssignments = async () => {
  try {
    const res = await axios.get(`${FASTAPI_BASE_URL}/assign/assignments/`);
    allAssignments.value = res.data;
  } catch (e) {}
};

// 获取所有学生提交
const fetchAllSubmissions = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const res = await axios.get(`${FASTAPI_BASE_URL}/files/submissions/all`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    allSubmissions.value = res.data;
  } catch (e) {}
};

// 下载作业
const downloadSubmission = async (submissionId, filePath) => {
  downloadMsg.value = '';
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(
      `${FASTAPI_BASE_URL}/files/submissions/download/${submissionId}`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob', // 重要：指明响应类型为 blob
      }
    );

    // 从响应头中获取文件类型，或直接使用通用二进制流类型
    const contentType = response.headers['content-type'] || 'application/octet-stream';
    const blob = new Blob([response.data], { type: contentType });
    
    // 创建一个隐藏的 <a> 标签来触发下载
    const link = document.createElement('a');
    const url = window.URL.createObjectURL(blob);
    link.href = url;
    link.download = filePath; // 设置下载的文件名
    document.body.appendChild(link);
    link.click();

    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    downloadMsg.value = `文件 ${filePath} 下载成功!`;
  } catch (e) {
    console.error('下载失败:', e);
    // 尝试解析 blob 中的错误信息
    if (e.response && e.response.data instanceof Blob) {
      const errorText = await e.response.data.text();
      const errorJson = JSON.parse(errorText);
      downloadMsg.value = errorJson.detail || '下载失败';
    } else {
      downloadMsg.value = e.response?.data?.detail || e.message || '下载失败';
    }
  }
};

// 修改成绩
const updateGrade = async () => {
  gradeMsg.value = '';
  try {
    const token = localStorage.getItem('access_token');
    if (!selectedSubmission.value || !newGrade.value) {
      gradeMsg.value = '请选择提交和输入成绩';
      return;
    }
    await axios.put(
      `${FASTAPI_BASE_URL}/courses/${selectedSubmission.value.assignment_id}/grades/${selectedSubmission.value.student_id}`,
      { grade: parseFloat(newGrade.value) },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    gradeMsg.value = '成绩修改成功！';
    fetchAllSubmissions();
  } catch (e) {
    gradeMsg.value = e.response?.data?.detail || e.message || '成绩修改失败';
  }
};

// 创建课程
const createCourse = async () => {
  createCourseMsg.value = '';
  try {
    const token = localStorage.getItem('access_token');
    if (!newCourse.value.course_name || !newCourse.value.credit) {
      createCourseMsg.value = '请填写完整信息';
      return;
    }
    await axios.post(`${FASTAPI_BASE_URL}/course/courses/`, newCourse.value, {
      headers: { Authorization: `Bearer ${token}` }
    });
    createCourseMsg.value = '课程创建成功！';
    fetchCourses();
  } catch (e) {
    createCourseMsg.value = e.response?.data?.detail || e.message || '创建失败';
  }
};

const sidebarButtonClasses = (tabName) => {
  const baseClasses = 'flex items-center w-full px-4 py-2.5 text-left text-sm font-medium rounded-lg transition-colors duration-200 relative';
  if (activeTab.value === tabName) {
    return `${baseClasses} bg-indigo-50 text-indigo-700`;
  }
  return `${baseClasses} text-gray-600 hover:bg-gray-50 hover:text-gray-900`;
};

onMounted(() => {
  fetchTeacherInfo();
  fetchCourses();
  fetchAllAssignments();
  fetchAllSubmissions();
});
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <Navbar />

    <main class="container mx-auto p-4 sm:p-6 lg:p-8">
      <div class="grid grid-cols-12 gap-6">
        
        <!-- Left Sidebar -->
        <div class="col-span-12 lg:col-span-3">
          <div class="bg-white rounded-lg shadow-md">
            <div class="p-4 border-b">
              <h2 class="text-lg font-semibold text-gray-800">教师中心</h2>
            </div>
            <nav class="p-2">
              <button @click="activeTab = 'info'" :class="sidebarButtonClasses('info')">
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                教师信息
              </button>
              <button @click="activeTab = 'publish'" :class="sidebarButtonClasses('publish')">
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                发布作业
              </button>
              <button @click="activeTab = 'download'" :class="sidebarButtonClasses('download')">
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                学生作业
              </button>
              <button @click="activeTab = 'grade'" :class="sidebarButtonClasses('grade')">
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                修改成绩
              </button>
              <button @click="activeTab = 'createCourse'" :class="sidebarButtonClasses('createCourse')">
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v11.494m-9-5.747h18"></path></svg>
                创建课程
              </button>
            </nav>
          </div>
        </div>

        <!-- Right Content Area -->
        <div class="col-span-12 lg:col-span-9 space-y-6">
          
          <!-- Teacher Info -->
          <div v-if="activeTab === 'info'">
            <div class="bg-white rounded-lg shadow-md">
              <div class="bg-indigo-600 text-white p-4 rounded-t-lg flex items-center space-x-3">
                <h2 class="text-xl font-bold">教师信息中心</h2>
              </div>
              <div v-if="teacherInfo" class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-6">
                <div><p class="text-sm text-gray-500">工号</p><p class="text-lg font-semibold text-gray-800">{{ teacherInfo.teacher_id }}</p></div>
                <div><p class="text-sm text-gray-500">姓名</p><p class="text-lg font-semibold text-gray-800">{{ teacherInfo.user?.username }}</p></div>
                <div><p class="text-sm text-gray-500">职称</p><p class="text-lg font-semibold text-gray-800">{{ teacherInfo.title }}</p></div>
                <div><p class="text-sm text-gray-500">院系</p><p class="text-lg font-semibold text-gray-800">{{ teacherInfo.department }}</p></div>
              </div>
            </div>
          </div>

          <!-- Publish Assignment -->
          <div v-if="activeTab === 'publish'">
            <div class="bg-white rounded-lg shadow-md">
              <div class="p-4 border-b"><h2 class="text-xl font-bold text-gray-800">发布新作业</h2></div>
              <div class="p-6">
                <form @submit.prevent="publishAssignment" class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">作业内容</label>
                    <textarea v-model="newAssignment.content" rows="3" class="w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"></textarea>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">截止时间</label>
                      <input v-model="newAssignment.deadline" type="datetime-local" class="w-full border-gray-300 rounded-md shadow-sm"/>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">课程</label>
                      <select v-model="newAssignment.course_id" class="w-full border-gray-300 rounded-md shadow-sm">
                        <option disabled value="">请选择</option>
                        <option v-for="c in courses" :key="c.course_id" :value="c.course_id">{{ c.course_name }}</option>
                      </select>
                    </div>
                  </div>
                  <button type="submit" class="w-full px-4 py-2 bg-teal-500 text-white font-semibold rounded-md hover:bg-teal-600">发布</button>
                </form>
              </div>
            </div>
          </div>

          <!-- Student Submissions -->
          <div v-if="activeTab === 'download'">
            <div class="bg-white rounded-lg shadow-md">
              <div class="p-4 border-b"><h2 class="text-xl font-bold text-gray-800">学生作业列表</h2></div>
              <div class="p-6">
                <table class="w-full text-left text-sm">
                  <thead class="bg-gray-50 text-gray-600"><tr><th class="p-3">作业ID</th><th class="p-3">学生ID</th><th class="p-3">提交时间</th><th class="p-3">文件</th><th class="p-3 text-center">下载</th></tr></thead>
                  <tbody>
                    <tr v-for="sub in allSubmissions" :key="sub.submission_id" class="border-b hover:bg-gray-50">
                      <td class="p-3">{{ sub.assignment_id }}</td><td class="p-3">{{ sub.student_id }}</td><td class="p-3">{{ sub.submit_time }}</td><td class="p-3">{{ sub.file_path }}</td>
                      <td class="p-3 text-center"><button @click="downloadSubmission(sub.submission_id, sub.file_path)" class="text-indigo-600 hover:text-indigo-800"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg></button></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Update Grade -->
          <div v-if="activeTab === 'grade'">
            <div class="bg-white rounded-lg shadow-md">
              <div class="p-4 border-b"><h2 class="text-xl font-bold text-gray-800">修改学生成绩</h2></div>
              <div class="p-6 max-w-md mx-auto">
                <form @submit.prevent="updateGrade" class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">选择提交</label>
                    <select v-model="selectedSubmission" class="w-full border-gray-300 rounded-md shadow-sm">
                      <option disabled value="">请选择</option>
                      <option v-for="sub in allSubmissions" :key="sub.submission_id" :value="sub">{{ sub.assignment_id }} - {{ sub.student_id }} - {{ sub.submit_time }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">输入新成绩</label>
                    <input v-model="newGrade" type="text" class="w-full border-gray-300 rounded-md shadow-sm"/>
                  </div>
                  <button type="submit" class="w-full px-4 py-2 bg-teal-500 text-white font-semibold rounded-md hover:bg-teal-600">修改成绩</button>
                </form>
              </div>
            </div>
          </div>

          <!-- Create Course -->
          <div v-if="activeTab === 'createCourse'">
            <div class="bg-white rounded-lg shadow-md">
              <div class="p-4 border-b"><h2 class="text-xl font-bold text-gray-800">创建新课程</h2></div>
              <div class="p-6 max-w-md mx-auto">
                <form @submit.prevent="createCourse" class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">课程名称</label>
                    <input v-model="newCourse.course_name" type="text" class="w-full border-gray-300 rounded-md shadow-sm"/>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">学分</label>
                    <input v-model="newCourse.credit" type="text" class="w-full border-gray-300 rounded-md shadow-sm"/>
                  </div>
                  <button type="submit" class="w-full px-4 py-2 bg-teal-500 text-white font-semibold rounded-md hover:bg-teal-600">创建课程</button>
                </form>
              </div>
            </div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
</style>