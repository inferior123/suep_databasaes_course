<script setup>
import { RouterLink, useRouter } from "vue-router";
import { computed } from "vue";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const AuthStore = useAuthStore();
const isAuthenticated = computed(() => AuthStore.isAuthenticated);
const user = computed(() => AuthStore.user);

const handleLogOut = () => {
  AuthStore.logout();
  router.push("/Login");
};
</script>

<template>
  <header class="bg-indigo-600 text-white shadow-lg">
    <div class="container mx-auto flex items-center justify-between p-3">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
          <svg class="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M12 14l9-5-9-5-9 5 9 5z" />
            <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-9.998 12.078 12.078 0 01.665-6.479L12 14z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-9.998 12.078 12.078 0 01.665-6.479L12 14z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold tracking-wider">作业管理系统</h1>
      </div>

      <div v-if="isAuthenticated && user" class="flex items-center space-x-4">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center text-indigo-600 font-bold text-xl">
            {{ user.username ? user.username.charAt(0).toUpperCase() : '' }}
          </div>
          <div class="text-left text-sm">
            <p class="font-semibold">{{ user.username }}</p>
            <p class="text-indigo-200">{{ user.details || (AuthStore.role === 'student' ? '学生' : '教师') }}</p>
          </div>
        </div>
        <button
          @click="handleLogOut"
          class="p-2 rounded-full hover:bg-indigo-700 transition-colors"
          title="注销"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
        </button>
      </div>
       <div v-else class="flex items-center space-x-2">
        <RouterLink
          to="/Login"
          class="px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          登录
        </RouterLink>
        <RouterLink
          to="/Register"
          class="px-4 py-2 rounded-md bg-white text-indigo-600 text-sm font-medium hover:bg-gray-200 transition-colors"
        >
          注册
        </RouterLink>
      </div>
    </div>
  </header>
</template>