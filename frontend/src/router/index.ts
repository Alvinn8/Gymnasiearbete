import { isLoggedIn, getSuccessfulLoginPage } from "@/api/auth";
import { createRouter, createWebHistory, type NavigationGuard } from "vue-router";

const requireLogin: NavigationGuard = async function(to) {
  if (!(await isLoggedIn())) {
    // Redirect to login
    return {
      name: "login",
      query: {
        returnUrl: to.path
      }
    };
  }
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/about",
      name: "about",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/AboutView.vue")
    },
    {
      path: "/test",
      name: "test",
      component: () => import("../views/TestView.vue"),
      beforeEnter: [requireLogin]
    },
    {
      path: "/register",
      name: "register",
      component: () => import("../views/RegisterView.vue")
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginView.vue"),
      beforeEnter: async () => {
        if (await isLoggedIn()) {
          // The user is already logged in
          return getSuccessfulLoginPage();
        }
      }
    },
    {
      path: "/mapmaker/maps",
      name: "maps",
      component: () => import("../views/mapmaker/MapsView.vue"),
      beforeEnter: [requireLogin]
    }
  ]
});

export default router;
