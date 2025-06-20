<script setup>
import { RouterLink } from "vue-router";
import Navbar from "../components/NavBar.vue";
</script>

<template>
    <Navbar />
    <section class="bg-white lg:grid lg:h-screen lg:place-content-center">
    <div class="mx-auto w-screen max-w-screen-xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8 lg:py-32">
        <div class="mx-auto max-w-prose text-center">
        <h1 class="text-4xl font-bold text-gray-900 sm:text-5xl">
            CS202 WEB开发实践
        </h1>

        <p class="mt-4 text-base text-pretty text-gray-700 sm:text-lg/relaxed">
            实现了一个作业开发系统，有用户认证、作业提交等核心功能模块，在实践之中学习现代Web开发技术栈。
        </p>

        <div class="mt-4 flex justify-center gap-4 sm:mt-6">
        <RouterLink
          to="/Login"
          class="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-colors"
        >
          开始使用
        </RouterLink>

        <RouterLink
          to="/Signup"
          class="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 transition-colors"
        >
          注册
        </RouterLink>
        </div>
        </div>
    </div>
    </section>
</template>

<style scoped></style>