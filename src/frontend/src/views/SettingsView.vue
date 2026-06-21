<template>
  <section>
    <div class="page-head">
      <div>
        <h1>Settings</h1>
        <p>Configure AI Analysis connection settings.</p>
      </div>
    </div>
    <section class="panel" style="max-width:720px">
      <h2>AI Configuration</h2>
      <div class="grid" style="margin-top:16px">
        <label class="span-12">API base URL<br /><input v-model="settings.api_base" style="width:100%" /></label>
        <label class="span-12">API key<br /><input v-model="apiKey" placeholder="Stored by the backend" type="password" style="width:100%" /></label>
        <label class="span-12">Model name<br /><input v-model="settings.model" style="width:100%" /></label>
        <label class="span-12"><input v-model="streaming" type="checkbox" style="height:auto" /> Streaming responses</label>
      </div>
      <div class="toolbar" style="margin-top:16px">
        <button class="primary" @click="save">Save Settings</button>
        <button @click="test">Test Connection</button>
        <span>{{ message }}</span>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api } from "../api/client";

const settings = ref<any>({});
const apiKey = ref("");
const message = ref("");
const streaming = computed({
  get: () => settings.value.streaming === "true",
  set: (value) => { settings.value.streaming = value ? "true" : "false"; },
});
const save = async () => {
  settings.value = await api.saveSettings({ ...settings.value, api_key: apiKey.value });
  apiKey.value = "";
  message.value = "Settings saved.";
};
const test = async () => {
  const result = await api.testSettings();
  message.value = result.message;
};
onMounted(async () => { settings.value = await api.settings(); });
</script>
