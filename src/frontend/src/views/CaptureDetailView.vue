<template>
  <section v-if="capture" class="fit-page">
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
    <div class="capture-workbench">
      <section class="pane overview-pane">
        <OverviewTab :capture="capture" />
      </section>
      <section class="pane packets-pane">
        <PacketsTab :capture-id="capture.id" />
      </section>
      <section class="pane ai-pane">
        <AiTab :capture="capture" />
      </section>
    </div>
  </section>
  <div v-else class="empty">Loading capture...</div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "../api/client";
import OverviewTab from "../components/captures/OverviewTab.vue";
import PacketsTab from "../components/packets/PacketsTab.vue";
import AiTab from "../components/ai/AiTab.vue";

const route = useRoute();
const router = useRouter();
const capture = ref<any>();
const load = async () => { capture.value = await api.capture(String(route.params.id)); };
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
