import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../view/HomeView.vue"
import NotFoundView from "../view/NotFoundView.vue"
import LoginView from "../view/LoginView.vue"
import StudentView from "../view/StudentView.vue"
import TeacherView from "../view/TeacherView.vue"
import SignupView from "../view/SignupView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: "/",
        name: "home",
        component: HomeView,
      },
      {
        path: "/Login",
        name: "login",
        component: LoginView
      },{
        path: "/Student",
        name: "student",
        component: StudentView
      },{
        path: "/Teacher",
        name: "teacher",
        component: TeacherView
      },{
        path: "/Signup",
        name: "signup",
        component: SignupView
      },
      {
        path: "/:pathMatch(.*)*",
        name: "not_found",
        component: NotFoundView,
      },
    ],
  });
  
  export default router;