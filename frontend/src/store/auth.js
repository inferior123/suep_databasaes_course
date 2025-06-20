import { defineStore } from "pinia";
import axios from "axios";

import { FASTAPI_BASE_URL } from "../constants";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user")) || null, // 当前用户信息
    isAuthenticated: !!localStorage.getItem("access_token"), // 认证状态
    role: localStorage.getItem("user_role") || null, // 用户角色（学生/教师）
  }),
  
  actions: {
    /**
     * 用户登录方法
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise<boolean>} 登录是否成功
     */
    async login(username, password) {
      try {
        // 准备符合 OAuth2 规范的请求数据
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);
        formData.append("grant_type", "password");
        
        // 发送登录请求到后端
        const response = await axios.post(
          `${FASTAPI_BASE_URL}/token`, // 注意这里使用 /token 而不是 /login/access_token
          formData,
          {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
              "Accept": "application/json"
            }
          }
        );

        // 处理登录成功
        const accessToken = response.data.access_token;
        const tokenType = response.data.token_type;
        
        // 保存认证信息到本地存储
        localStorage.setItem("access_token", accessToken);
        
        // 获取用户详细信息
        await this.fetchUserInfo(accessToken);
        
        this.isAuthenticated = true;
        return true;
        
      } catch (error) {
        // 处理登录失败
        this.logout();
        
        // 根据后端返回的错误信息提供更具体的反馈
        if (error.response) {
          const status = error.response.status;
          if (status === 401) {
            throw new Error("用户名或密码错误");
          } else if (status >= 500) {
            throw new Error("服务器错误，请稍后再试");
          }
        }
        
        throw new Error("登录失败，请检查网络连接");
      }
    },
    
    /**
     * 获取当前用户信息
     * @param {string} token - 访问令牌
     */
    async fetchUserInfo(token) {
      try {
        // 使用 token 获取用户信息
        const userResponse = await axios.get(
          `${FASTAPI_BASE_URL}/users/me`,
          {
            headers: {
              "Authorization": `Bearer ${token}`
            }
          }
        );
        
        // 保存用户信息
        const userData = userResponse.data;
        this.user = {
          username: userData.username,
          user_id: userData.user_id
        };
        
        // 确定用户角色并保存
        if (userData.is_student) {
          this.role = "student";
          localStorage.setItem("user_role", "student");
        } else if (userData.is_teacher) {
          this.role = "teacher";
          localStorage.setItem("user_role", "teacher");
        }
        
        localStorage.setItem("user", JSON.stringify(this.user));
        
      } catch (error) {
        console.error("获取用户信息失败:", error);
        this.logout();
        throw new Error("无法获取用户信息");
      }
    },
    
    /**
     * 用户注销方法
     */
    logout() {
      // 清除所有认证相关数据
      this.user = null;
      this.isAuthenticated = false;
      this.role = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      localStorage.removeItem("user_role");
    }
  }
});