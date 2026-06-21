<template>
  <section v-if="capture">
    <RouterLink to="/captures">Back to Captures</RouterLink>
    <div class="page-head">
      <div>
        <h1>{{ capture.original_name }}</h1>
        <p class="mono">{{ capture.packet_count }} packets · {{ size(capture.file_size) }} · {{ duration(capture.duration_seconds) }} · {{ capture.uploaded_at }}</p>
      </div>
      <div class="toolbar">
        <span class="status" :class="capture.status">{{ capture.status }}</span>
        <a class="btn" :href="`/api/captures/${capture.id}/download`">Download</a>
        <button class="danger" @click="remove">Delete</button>
      </div>
    </div>
    <nav class="tabs" aria-label="Capture detail tabs">
      <RouterLink :to="tabLink('overview')" :class="{ active: tab === 'overview' }">Overview</RouterLink>
      <RouterLink :to="tabLink('packets')" :class="{ active: tab === 'packets' }">Packets</RouterLink>
      <RouterLink :to="tabLink('ai')" :class="{ active: tab === 'ai' }">AI Analysis</RouterLink>
    </nav>
    <OverviewTab v-if="tab === 'overview'" :capture="capture" />
    <PacketsTab v-if="tab === 'packets'" :capture-id="capture.id" />
    <AiTab v-if="tab === 'ai'" :capture="capture" />
  </section>
  <div v-else class="empty">Loading capture...</div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "../api/client";
import OverviewTab from "../components/captures/OverviewTab.vue";
import PacketsTab from "../components/packets/PacketsTab.vue";
import AiTab from "../components/ai/AiTab.vue";

const route = useRoute();
const router = useRouter();
const capture = ref<any>();
const tab = computed(() => String(route.query.tab || "overview"));
const load = async () => { capture.value = await api.capture(String(route.params.id)); };
const tabLink = (name: string) => `/captures/${route.params.id}?tab=${name}`;
const remove = async () => {
  if (capture.value && confirm("Delete capture?")) {
    await api.remove(capture.value.id);
    await router.push("/captures");
  }
};
const size = (bytes = 0) => `${(bytes / 1024 / 1024).toFixed(1)} MB`;
const duration = (seconds = 0) => seconds ? `${Number(seconds).toFixed(0)}s` : "—";
watch(() => route.params.id, load);
onMounted(load);
</script>
