<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';
import { FASTAPI_BASE_URL } from '../constants';
import Navbar from "../components/NavBar.vue";

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
const downloadSubmission = (submissionId, filePath) => {
  window.open(`${FASTAPI_BASE_URL}/files/submissions/download/${submissionId}`, '_blank');
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

onMounted(() => {
  fetchTeacherInfo();
  fetchCourses();
  fetchAllAssignments();
  fetchAllSubmissions();
});
</script>

<template>
  <div>
    <Navbar />
  </div>
  <div class="flex max-w-5xl mx-auto p-6">
    <!-- 侧边栏 -->
    <aside class="w-48 mr-6 border-r pr-4">
      <nav class="flex flex-col gap-4">
        <button
          class="text-left py-2 px-3 rounded hover:bg-gray-100"
          :class="activeTab === 'info' ? 'bg-teal-100 font-bold' : ''"
          @click="activeTab = 'info'"
        >
          教师信息
        </button>
        <button
          class="text-left py-2 px-3 rounded hover:bg-gray-100"
          :class="activeTab === 'publish' ? 'bg-teal-100 font-bold' : ''"
          @click="activeTab = 'publish'"
        >
          发布作业
        </button>
        <button
          class="text-left py-2 px-3 rounded hover:bg-gray-100"
          :class="activeTab === 'download' ? 'bg-teal-100 font-bold' : ''"
          @click="activeTab = 'download'"
        >
          查看/下载学生作业
        </button>
        <button
          class="text-left py-2 px-3 rounded hover:bg-gray-100"
          :class="activeTab === 'grade' ? 'bg-teal-100 font-bold' : ''"
          @click="activeTab = 'grade'"
        >
          修改成绩
        </button>
        <button
          class="text-left py-2 px-3 rounded hover:bg-gray-100"
          :class="activeTab === 'createCourse' ? 'bg-teal-100 font-bold' : ''"
          @click="activeTab = 'createCourse'"
        >
          创建课程
        </button>
      </nav>
    </aside>

    <!-- 右侧内容区 -->
    <div class="flex-1">
      <h2 class="text-2xl font-bold mb-4">教师中心</h2>
      <div v-if="error" class="text-red-500 mb-4">{{ error }}</div>

      <!-- 教师信息 -->
      <div v-if="activeTab === 'info'">
        <div v-if="teacherInfo">
          <div class="mb-4 p-4 border rounded bg-gray-50">
            <h3 class="font-semibold">基本信息</h3>
            <p>工号：{{ teacherInfo.teacher_id }}</p>
            <p>姓名：{{ teacherInfo.user?.username }}</p>
            <p>职称：{{ teacherInfo.title }}</p>
            <p>院系：{{ teacherInfo.department }}</p>
            <p>邮箱：{{ teacherInfo.user?.email }}</p>
          </div>
        </div>
        <div v-else class="text-gray-500">正在加载教师信息...</div>
      </div>

      <!-- 发布作业 -->
      <div v-if="activeTab === 'publish'">
        <div class="p-4 border rounded bg-gray-50">
          <h3 class="font-semibold mb-2">发布作业</h3>
          <div v-if="publishMsg" class="mb-2 text-blue-600">{{ publishMsg }}</div>
          <form @submit.prevent="publishAssignment" class="flex flex-col gap-2">
            <label>
              作业内容：
              <input v-model="newAssignment.content" class="ml-2 border rounded px-2 py-1" />
            </label>
            <label>
              截止时间：
              <input v-model="newAssignment.deadline" type="datetime-local" class="ml-2 border rounded px-2 py-1" />
            </label>
            <label>
              状态：
              <select v-model="newAssignment.status" class="ml-2 border rounded px-2 py-1">
                <option value="open">开放</option>
                <option value="closed">关闭</option>
              </select>
            </label>
            <label>
              课程：
              <select v-model="newAssignment.course_id" class="ml-2 border rounded px-2 py-1">
                <option disabled value="">请选择</option>
                <option v-for="c in courses" :key="c.course_id" :value="c.course_id">
                  {{ c.course_name }}
                </option>
              </select>
            </label>
            <button
              type="submit"
              class="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600"
            >
              发布
            </button>
          </form>
        </div>
      </div>

      <!-- 查看/下载学生作业 -->
      <div v-if="activeTab === 'download'">
        <div class="p-4 border rounded bg-gray-50">
          <h3 class="font-semibold mb-2">学生作业列表</h3>
          <table class="min-w-full text-sm mb-2">
            <thead>
              <tr>
                <th class="px-2 py-1">作业ID</th>
                <th class="px-2 py-1">学生ID</th>
                <th class="px-2 py-1">提交时间</th>
                <th class="px-2 py-1">文件</th>
                <th class="px-2 py-1">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sub in allSubmissions" :key="sub.submission_id">
                <td class="px-2 py-1">{{ sub.assignment_id }}</td>
                <td class="px-2 py-1">{{ sub.student_id }}</td>
                <td class="px-2 py-1">{{ sub.submit_time }}</td>
                <td class="px-2 py-1">{{ sub.file_path }}</td>
                <td class="px-2 py-1">
                  <button @click="downloadSubmission(sub.submission_id, sub.file_path)" class="text-blue-600 hover:underline">
                    <svg class="inline w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 修改成绩 -->
      <div v-if="activeTab === 'grade'">
        <div class="p-4 border rounded bg-gray-50">
          <h3 class="font-semibold mb-2">修改学生成绩</h3>
          <div v-if="gradeMsg" class="mb-2 text-blue-600">{{ gradeMsg }}</div>
          <form @submit.prevent="updateGrade" class="flex flex-col gap-2">
            <label>
              选择提交：
              <select v-model="selectedSubmission" class="ml-2 border rounded px-2 py-1">
                <option disabled value="">请选择</option>
                <option v-for="sub in allSubmissions" :key="sub.submission_id" :value="sub">
                  作业ID:{{ sub.assignment_id }} 学生ID:{{ sub.student_id }}
                </option>
              </select>
            </label>
            <label>
              新成绩：
              <input v-model="newGrade" type="number" min="0" max="100" class="ml-2 border rounded px-2 py-1" />
            </label>
            <button
              type="submit"
              class="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600"
            >
              修改
            </button>
          </form>
        </div>
      </div>

      <!-- 创建课程 -->
      <div v-if="activeTab === 'createCourse'">
        <div class="p-4 border rounded bg-gray-50">
          <h3 class="font-semibold mb-2">创建课程</h3>
          <div v-if="createCourseMsg" class="mb-2 text-blue-600">{{ createCourseMsg }}</div>
          <form @submit.prevent="createCourse" class="flex flex-col gap-2">
            <label>
              课程名：
              <input v-model="newCourse.course_name" class="ml-2 border rounded px-2 py-1" />
            </label>
            <label>
              学分：
              <input v-model="newCourse.credit" type="number" min="1" class="ml-2 border rounded px-2 py-1" />
            </label>
            <button
              type="submit"
              class="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600"
            >
              创建
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
