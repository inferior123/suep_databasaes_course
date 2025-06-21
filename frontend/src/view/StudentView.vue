<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../store/auth';
import { FASTAPI_BASE_URL } from '../constants';
import Navbar from "../components/NavBar.vue";

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
    toastStore.showToast('选课成功', 'success');
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

// 提交作业
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
    // 注意：接口参数名为 file
    const res = await axios.post(
      `${FASTAPI_BASE_URL}/assign/assignments/${selectedAssignmentId.value}/submit`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    uploadMsg.value = '提交成功！';
    fetchSubmissions(); // 提交后刷新提交历史
  } catch (e) {
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
          学生信息
        </button>
        <button
          class="text-left py-2 px-3 rounded hover:bg-gray-100"
          :class="activeTab === 'course' ? 'bg-teal-100 font-bold' : ''"
          @click="activeTab = 'course'"
        >
          选课
        </button>
        <button
          class="text-left py-2 px-3 rounded hover:bg-gray-100"
          :class="activeTab === 'submit' ? 'bg-teal-100 font-bold' : ''"
          @click="activeTab = 'submit'"
        >
          提交作业
        </button>
      </nav>
    </aside>

    <!-- 右侧内容区 -->
    <div class="flex-1">
      <h2 class="text-2xl font-bold mb-4">学生中心</h2>
      <div v-if="error" class="text-red-500 mb-4">{{ error }}</div>

      <!-- 学生信息 -->
      <div v-if="activeTab === 'info'">
        <div v-if="studentInfo">
          <div class="mb-4 p-4 border rounded bg-gray-50">
            <h3 class="font-semibold">基本信息</h3>
            <p>学号：{{ studentInfo.student_id }}</p>
            <p>姓名：{{ studentInfo.user?.username }}</p>
            <p>年级：{{ studentInfo.grade }}</p>
            <p>专业：{{ studentInfo.major }}</p>
          </div>
          <div class="mb-4 p-4 border rounded bg-gray-50">
            <h3 class="font-semibold mb-2">课程与成绩</h3>
            <table class="min-w-full text-sm">
              <thead>
                <tr>
                  <th class="px-2 py-1">课程名</th>
                  <th class="px-2 py-1">学分</th>
                  <th class="px-2 py-1">成绩</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="course in courses" :key="course.course_id">
                  <td class="px-2 py-1">{{ course.course_name }}</td>
                  <td class="px-2 py-1">{{ course.credit }}</td>
                  <td class="px-2 py-1">{{ course.grade ?? '未评分' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mb-4 p-4 border rounded bg-gray-50">
            <h3 class="font-semibold mb-2">作业提交历史</h3>
            <table class="min-w-full text-sm">
              <thead>
                <tr>
                  <th class="px-2 py-1">作业ID</th>
                  <th class="px-2 py-1">提交时间</th>
                  <th class="px-2 py-1">文件</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sub in submissions" :key="sub.submission_id">
                  <td class="px-2 py-1">{{ sub.assignment_id }}</td>
                  <td class="px-2 py-1">{{ sub.submit_time }}</td>
                  <td class="px-2 py-1">
                    <a :href="`${FASTAPI_BASE_URL}/uploads/${sub.file_path}`" target="_blank" class="text-blue-600 underline">{{ sub.file_path }}</a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="text-gray-500">正在加载学生信息...</div>
      </div>

      <!-- 选课功能区 -->
      <div v-if="activeTab === 'course'">
        <div class="p-4 border rounded bg-gray-50">
          <h3 class="font-semibold mb-2">选课功能</h3>
          <div v-if="enrollMsg" class="mb-2 text-blue-600">{{ enrollMsg }}</div>
          <table class="min-w-full text-sm mb-2">
            <thead>
              <tr>
                <th class="px-2 py-1">课程名</th>
                <th class="px-2 py-1">学分</th>
                <th class="px-2 py-1">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in allCourses" :key="course.course_id">
                <td class="px-2 py-1">{{ course.course_name }}</td>
                <td class="px-2 py-1">{{ course.credit }}</td>
                <td class="px-2 py-1">
                  <button
                    class="px-2 py-1 bg-teal-500 text-white rounded hover:bg-teal-600"
                    :disabled="enrolling"
                    @click="enrollCourse(course.course_id)"
                  >
                    选课
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 提交作业功能区 -->
      <div v-if="activeTab === 'submit'">
        <div class="p-4 border rounded bg-gray-50">
          <h3 class="font-semibold mb-2">提交作业</h3>
          <div v-if="uploadMsg" class="mb-2 text-blue-600">{{ uploadMsg }}</div>
          <form @submit.prevent="submitAssignment" class="flex flex-col gap-2">
            <label>
              选择作业：
              <select v-model="selectedAssignmentId" class="ml-2 border rounded px-2 py-1">
                <option disabled value="">请选择</option>
                <option v-for="a in assignments" :key="a.assignment_id" :value="a.assignment_id">
                  {{ a.assignment_id }} - {{ a.content }}
                </option>
              </select>
            </label>
            <label>
              上传文件：
              <input type="file" @change="e => selectedFile.value = e.target.files[0]" class="ml-2" />
            </label>
            <button
              type="submit"
              class="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600"
              :disabled="uploading"
            >
              提交
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

