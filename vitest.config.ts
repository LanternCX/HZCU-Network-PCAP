import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

const rootNodeModules = fileURLToPath(new URL("./node_modules/", import.meta.url));

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      vue: `${rootNodeModules}vue/dist/vue.esm-bundler.js`,
      "vue-router": `${rootNodeModules}vue-router/dist/vue-router.mjs`,
    },
  },
  test: {
    environment: "jsdom",
    include: ["test/frontend/**/*.spec.ts"],
  },
});
