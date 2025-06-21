import { defineStore } from 'pinia';

export const useToastStore = defineStore('toast', {
     state: () => ({
          message: '',
          type: 'success', // 'success' or 'error'
          isVisible: false,
     }),
     actions: {
          showToast(message, type = 'success') {
               this.message = message;
               this.type = type;
               this.isVisible = true;
               setTimeout(() => {
                    this.hideToast();
               }, 3000); // 3秒后自动隐藏
          },
          hideToast() {
               this.isVisible = false;
               this.message = '';
          },
     },
}); 