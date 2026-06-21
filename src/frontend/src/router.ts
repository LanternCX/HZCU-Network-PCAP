import { createRouter, createWebHistory } from "vue-router";

import DashboardView from "./views/DashboardView.vue";
import CapturesView from "./views/CapturesView.vue";
import CaptureDetailView from "./views/CaptureDetailView.vue";
import SettingsView from "./views/SettingsView.vue";

export const routes = [
  { path: "/", component: DashboardView },
  { path: "/captures", component: CapturesView },
  { path: "/captures/:id", component: CaptureDetailView },
  { path: "/settings", component: SettingsView },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
