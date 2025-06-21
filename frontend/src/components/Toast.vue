<script setup>
import { useToastStore } from '../store/toast';

const toastStore = useToastStore();
</script>

<template>
     <div
          v-if="toastStore.isVisible"
          class="fixed top-5 right-5 p-4 rounded-lg shadow-lg text-white z-50 transition-transform duration-300"
          :class="{
               'bg-green-500': toastStore.type === 'success',
               'bg-red-500': toastStore.type === 'error',
          }"
     >
          {{ toastStore.message }}
          <button @click="toastStore.hideToast()" class="ml-4 font-bold">X</button>
     </div>
</template>

<style scoped>
</style> 