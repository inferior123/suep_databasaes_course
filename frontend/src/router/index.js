import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../view/HomeView.vue"
import NotFoundView from "../view/NotFoundView.vue"
import LoginView from "../view/LoginView.vue"

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
      },
      {
        path: "/:pathMatch(.*)*",
        name: "not_found",
        component: NotFoundView,
      },
    ],
  });
  
  export default router;