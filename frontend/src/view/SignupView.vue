<script setup>
import { RouterLink } from "vue-router";
import { ref } from "vue";
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router"; 

// 基础表单字段
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const email = ref('');
const isTeacher = ref(false); 
const errorMessage = ref('');

// 老师专属字段
const teacherTitle = ref('');     // 职称
const teacherDepartment = ref('');// 院系

// 学生专属字段
const studentGrade = ref('');     // 年级
const studentMajor = ref('');     // 专业

// Pinia 状态管理 & 路由
const AuthStore = useAuthStore();
const router = useRouter();

console.log("AuthStore.signup", AuthStore.signup);

// 注册逻辑：传递所有字段到 Store
const handleSignup = async () => {
  try {
    const role = isTeacher.value ? 'teacher' : 'student';
    // 调用 Store 注册方法（需确保 store 内 signup 兼容所有参数）
    await AuthStore.signup(
      username.value, 
      password.value, 
      confirmPassword.value, 
      email.value, 
      role,
      teacherTitle.value,   // 老师职称
      teacherDepartment.value, // 老师院系
      studentGrade.value,   // 学生年级
      studentMajor.value    // 学生专业
    );
    // 注册成功后跳转登录页（可按需调整）
    router.push('/login');
  } catch (error) {
    errorMessage.value = error.message;
  }
};

// 切换注册身份（学生 ↔ 老师）
const toggleRole = () => {
  isTeacher.value = !isTeacher.value;
};
</script>

<template>
  <section class="bg-white">
    <div class="grid min-h-screen grid-cols-12">
      <!-- 右侧背景图（样式复用） -->
      <aside
        class="relative block h-16 lg:order-last lg:col-span-5 lg:h-full xl:col-span-6"
      >
        <img
          alt="注册页背景"
          src="../assets/premium_photo-1746420146082-4ae58de636e9(1).avif"
          class="absolute inset-0 h-full w-full object-cover"
        />
      </aside>

      <!-- 左侧表单区（样式复用） -->
      <main
        class="flex items-center justify-center px-8 py-8 lg:col-span-7 lg:px-16 lg:py-12 xl:col-span-6"
      >
        <div class="max-w-xl lg:max-w-3xl">
          <!-- 顶部 Logo/首页跳转（复用） -->
          <a class="block text-blue-600" href="#">
            <span class="sr-only">Home</span>
            <svg
              class="h-8 sm:h-10"
              viewBox="0 0 28 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M0.41 10.3847C1.14777 7.4194 2.85643 4.7861 5.2639 2.90424C7.6714 1.02234 10.6393 0 13.695 0C16.7507 0 19.7186 1.02234 22.1261 2.90424C24.5336 4.7861 26.2422 7.4194 26.98 10.3847H25.78C23.7557 10.3549 21.7729 10.9599 20.11 12.1147C20.014 12.1842 19.9138 12.2477 19.81 12.3047H19.67C19.5662 12.2477 19.466 12.1842 19.37 12.1147C17.6924 10.9866 15.7166 10.3841 13.695 10.3841C11.6734 10.3841 9.6976 10.9866 8.02 12.1147C7.924 12.1842 7.8238 12.2477 7.72 12.3047H7.58C7.4762 12.2477 7.376 12.1842 7.28 12.1147C5.6171 10.9599 3.6343 10.3549 1.61 10.3847H0.41ZM23.62 16.6547C24.236 16.175 24.9995 15.924 25.78 15.9447H27.39V12.7347H25.78C24.4052 12.7181 23.0619 13.146 21.95 13.9547C21.3243 14.416 20.5674 14.6649 19.79 14.6649C19.0126 14.6649 18.2557 14.416 17.63 13.9547C16.4899 13.9011 15.1341 13.4757 13.745 13.4757C12.3559 13.4757 11.0001 13.9011 9.86 13.9547C9.2343 14.416 8.4774 14.6649 7.7 14.6649C6.9226 14.6649 6.1657 14.416 5.54 13.9547C4.4144 13.1356 3.0518 12.7072 1.66 12.7347H0V15.9447H1.61C2.39051 15.924 3.154 16.175 3.77 16.6547C4.908 17.4489 6.2623 17.6147 7.65 17.6147C9.0377 17.6147 10.392 17.4489 11.53 16.6547C12.1468 16.1765 12.9097 15.9257 13.69 15.9447C14.4708 15.9223 15.2348 16.1735 15.85 16.6547C16.9901 17.4484 18.3459 17.6138 19.735 17.6138C21.1241 17.6138 22.4799 17.4484 23.62 16.6547ZM23.62 22.3947C24.236 21.915 24.9995 21.664 25.78 21.6847H27.39V18.4747H25.78C24.4052 18.4581 23.0619 18.886 21.95 19.6947C21.3243 20.156 20.5674 20.4049 19.79 20.4049C19.0126 20.4049 18.2557 20.156 17.63 19.6947C16.4899 18.9011 15.1341 18.4757 13.745 18.4757C12.3559 18.4757 11.0001 18.9011 9.86 19.6947C9.2343 20.156 8.4774 20.4049 7.7 20.4049C6.9226 20.4049 6.1657 20.156 5.54 19.6947C4.4144 18.8757 3.0518 18.4472 1.66 18.4747H0V21.6847H1.61C2.39051 21.664 3.154 21.915 3.77 22.3947C4.908 23.1889 6.2623 23.6147 7.65 23.6147C9.0377 23.6147 10.392 23.1889 11.53 22.3947C12.1468 21.9165 12.9097 21.6657 13.69 21.6847C14.4708 21.6623 15.2348 21.9135 15.85 22.3947C16.9901 23.1884 18.3459 23.6138 19.735 23.6138C21.1241 23.6138 22.4799 23.1884 23.62 22.3947Z"
                fill="currentColor"
              />
            </svg>
          </a>

       

          <!-- 标题：根据身份切换"学生/老师"文案 -->
          <h1 class="mt-6 text-2xl font-bold text-gray-900 sm:text-3xl md:text-4xl">
            欢迎注册{{ isTeacher ? '老师' : '学生' }}账号
          </h1>
          <p class="mt-4 leading-relaxed text-gray-500">
            填写信息完成{{ isTeacher ? '老师' : '学生' }}注册
          </p>

          <!-- 身份切换按钮：点击切换学生/老师 -->
          <button
            @click="toggleRole"
            class="mt-4 inline-block rounded-md border border-blue-600 bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-transparent hover:text-blue-600 focus:outline-none focus:ring active:text-blue-500"
          >
            切换为{{ isTeacher ? '学生' : '老师' }}注册
          </button>

          <!-- 表单区域：基础字段 + 身份专属字段 -->
          <div class="mt-8 grid grid-cols-6 gap-6">
            <!-- 用户名（复用） -->
            <div class="col-span-6">
              <label for="username" class="block text-sm font-medium text-gray-700">
                username
              </label>
              <input
                v-model="username"
                type="username"
                id="username"
                name="username"
                class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
              />
            </div>

            <!-- 邮箱（复用） -->
            <div class="col-span-6">
              <label for="email" class="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                v-model="email"
                type="email"
                id="email"
                name="email"
                class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
              />
            </div>

            <!-- 密码（复用） -->
            <div class="col-span-6">
              <label for="Password" class="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                v-model="password"
                type="password"
                id="Password"
                name="password"
                class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
              />
            </div>

            <!-- 确认密码（复用） -->
            <div class="col-span-6">
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <input
                v-model="confirmPassword"
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
              />
            </div>

            <!-- 身份专属字段：老师/学生切换渲染 -->
            <template v-if="isTeacher">
              <!-- 老师-职称 -->
              <div class="col-span-6">
                <label for="teacherTitle" class="block text-sm font-medium text-gray-700">
                  职称
                </label>
                <input
                  v-model="teacherTitle"
                  type="text"
                  id="teacherTitle"
                  name="teacherTitle"
                  class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
                />
              </div>
              <!-- 老师-院系 -->
              <div class="col-span-6">
                <label for="teacherDepartment" class="block text-sm font-medium text-gray-700">
                  院系
                </label>
                <input
                  v-model="teacherDepartment"
                  type="text"
                  id="teacherDepartment"
                  name="teacherDepartment"
                  class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
                />
              </div>
            </template>
            <template v-else>
              <!-- 学生-年级 -->
              <div class="col-span-6">
                <label for="studentGrade" class="block text-sm font-medium text-gray-700">
                  年级
                </label>
                <input
                  v-model="studentGrade"
                  type="text"
                  id="studentGrade"
                  name="studentGrade"
                  class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
                />
              </div>
              <!-- 学生-专业 -->
              <div class="col-span-6">
                <label for="studentMajor" class="block text-sm font-medium text-gray-700">
                  专业
                </label>
                <input
                  v-model="studentMajor"
                  type="text"
                  id="studentMajor"
                  name="studentMajor"
                  class="mt-1 w-full h-10 rounded-md border-2 border-gray-400 bg-white text-sm text-gray-700 shadow-sm"
                />
              </div>
            </template>

            <!-- 注册按钮 + 登录跳转（复用） -->
            <div class="col-span-6 sm:flex sm:items-center sm:gap-4">
              <button
                @click="handleSignup"
                class="inline-block shrink-0 rounded-md border border-blue-600 bg-blue-600 px-12 py-3 text-sm font-medium text-white transition hover:bg-transparent hover:text-blue-600 focus:outline-none focus:ring active:text-blue-500"
              >
                注册
              </button>

              <p class="mt-4 text-sm text-gray-500 sm:mt-0">
                已有账号？
                <RouterLink to="/login" class="text-gray-700 underline">登录</RouterLink>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  </section>
</template>

<style scoped></style>