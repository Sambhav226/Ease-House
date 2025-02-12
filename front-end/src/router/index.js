import { createRouter, createWebHistory } from "vue-router";
import AdminPage from "../views/AdminPage.vue";

import LandPage from "../views/LandPage.vue";
import RegisterPage from "../views/RegisterPage.vue";
import LoginPage from "../views/LoginPage.vue";
import ConsumerDashboard from "../views/ConsumerDashboard.vue";
import EditRequest from "../views/EditRequest.vue";
import EditProfile from "../views/EditProfile.vue";
import ServiceProviderDashboard from "../views/ServiceProviderDashboard.vue";
const routes = [
    {
      path: "/",
      name: "home",
      component: LandPage,
    },
    {
      path: "/register",
      name: "register",
      component: RegisterPage,
    },
    {
      path: "/login",
      name: "login",
      component: LoginPage,
    },
    {
      path: "/admin",
      name: "admin",
      component: AdminPage,
    },
    {
      path: "/consumer",
      name: "consumer",
      component: ConsumerDashboard,
    },
    {
      path: "/edit-request/:requestId",
      name: "EditRequest",
      component: EditRequest,
    },
    {
      path: "/service-provider",
      name: "service-provider",
      component: ServiceProviderDashboard,
    },
    {
      path: "/edit-profile",
      name: "edit-profile",
      component: EditProfile,
    }
  ];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
