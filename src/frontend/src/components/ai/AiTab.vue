<template>
  <div class="grid">
    <section class="panel span-4">
      <h2>Selected Capture</h2>
      <p>{{ capture.original_name }}</p>
      <p class="mono">{{ capture.packet_count }} packets · {{ capture.duration_seconds }}s</p>
      <span class="status" :class="capture.status">{{ capture.status }}</span>
    </section>
    <section class="panel span-8">
      <h2>Context Preview</h2>
      <p>Only analyzed statistics and a small representative packet sample are sent.</p>
      <p>Protocols: {{ context.protocols?.map((row: any[]) => `${row[0]} ${row[1]}`).join(", ") || "—" }}</p>
      <p>Top sources: {{ context.top_sources?.map((row: any[]) => row[0]).join(", ") || "—" }}</p>
      <p>Top destinations: {{ context.top_destinations?.map((row: any[]) => row[0]).join(", ") || "—" }}</p>
    </section>
    <section class="panel span-12 toolbar">
      <button class="primary" :disabled="state === 'Streaming'" @click="summarize">Summarize Capture</button>
      <button :disabled="state !== 'Streaming'" @click="stop">Stop</button>
      <button :disabled="!summary" @click="summarize">Regenerate Summary</button>
      <button :disabled="!summary" @click="copy">Copy Summary</button>
      <span class="status" :class="state === 'Failed' ? 'Failed' : 'Completed'">{{ state }}</span>
    </section>
    <section class="panel span-12 ai-report">
      <h2>Summary</h2>
      <div v-if="!summary" class="empty">{{ emptyMessage }}</div>
      <component v-else :is="Markstream" :content="summary" />
    </section>
  </div>
</template>

<script setup lang="ts">
import Markstream from "markstream-vue";
import { computed, onMounted, ref } from "vue";
import { api } from "../../api/client";

const props = defineProps<{ capture: any }>();
const context = ref<any>({});
const summary = ref("");
const state = ref("Not configured");
let controller: AbortController | undefined;
const emptyMessage = computed(() => {
  if (state.value === "Streaming") return "Waiting for DeepSeek response...";
  if (state.value === "Not configured") return "AI is not configured. Add API settings before starting analysis.";
  return "No summary yet. Summarize this capture to start analysis.";
});

const summarize = async () => {
  summary.value = "";
  state.value = "Streaming";
  controller = new AbortController();
  try {
    const response = await fetch(`/api/captures/${props.capture.id}/ai/summary`, { signal: controller.signal });
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    while (reader) {
      const { value, done } = await reader.read();
      if (done) break;
      summary.value += decoder.decode(value);
    }
    state.value = summary.value.startsWith("AI is not configured") ? "Not configured" : "Ready";
  } catch {
    state.value = "Failed";
  }
};
const stop = () => {
  controller?.abort();
  state.value = "Stopped";
};
const copy = () => navigator.clipboard.writeText(summary.value);
onMounted(async () => {
  context.value = await api.aiContext(props.capture.id);
  summary.value = context.value.saved_summary?.summary || "";
  const settings = await api.settings();
  state.value = settings.api_key_configured ? "Ready" : "Not configured";
});
</script>
