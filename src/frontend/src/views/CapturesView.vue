<template>
  <section>
    <div class="page-head">
      <div>
        <h1>Captures</h1>
        <p>Manage uploaded PCAP and PCAPNG files.</p>
      </div>
      <div class="toolbar">
        <input v-model="q" placeholder="Search captures..." @input="load" />
        <select v-model="status" aria-label="Status filter" @change="load">
          <option value="">All Status</option><option>Uploaded</option><option>Analyzing</option><option>Completed</option><option>Failed</option>
        </select>
        <label class="btn primary">Upload Capture<input type="file" accept=".pcap,.pcapng" hidden @change="upload" /></label>
      </div>
    </div>

    <div v-if="error" class="empty">{{ error }}</div>
    <div v-else-if="!captures.length" class="empty">No captures yet. Upload a PCAP or PCAPNG file to start analysis.</div>
    <section v-else class="table-panel">
      <table>
        <thead>
          <tr><th>File Name</th><th>Type</th><th>Packets</th><th>Size</th><th>Duration</th><th>Uploaded At</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="capture in captures" :key="capture.id">
            <td>
              <RouterLink :to="`/captures/${capture.id}`">{{ capture.original_name }}</RouterLink>
              <p v-if="capture.error_message">{{ capture.error_message }}</p>
            </td>
            <td>{{ capture.file_type }}</td>
            <td class="mono">{{ capture.packet_count || "—" }}</td>
            <td>{{ size(capture.file_size) }}</td>
            <td>{{ duration(capture.duration_seconds) }}</td>
            <td>{{ capture.uploaded_at }}</td>
            <td><span class="status" :class="capture.status">{{ capture.status }}</span></td>
            <td class="toolbar">
              <RouterLink class="btn" :to="`/captures/${capture.id}`">Open</RouterLink>
              <RouterLink class="btn" :to="`/captures/${capture.id}?tab=ai`">AI Analysis</RouterLink>
              <a class="btn" :href="`/api/captures/${capture.id}/download`">Download</a>
              <button @click="retry(capture.id)">Retry Analysis</button>
              <button class="danger" @click="remove(capture.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { api } from "../api/client";

const captures = ref<any[]>([]);
const q = ref("");
const status = ref("");
const error = ref("");
let poll: number | undefined;

const load = async () => {
  error.value = "";
  try {
    const query = new URLSearchParams({ q: q.value, status: status.value }).toString();
    captures.value = await api.captures(`?${query}`);
    schedulePoll();
  } catch (exc: any) {
    error.value = exc.message;
  }
};
const schedulePoll = () => {
  window.clearTimeout(poll);
  if (captures.value.some((capture) => ["Uploaded", "Analyzing"].includes(capture.status))) {
    poll = window.setTimeout(load, 1500);
  }
};
const upload = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (file) await api.upload(file);
  await load();
};
const retry = async (id: number) => { await api.retry(id); await load(); };
const remove = async (id: number) => {
  if (confirm("Delete capture?")) {
    await api.remove(id);
    await load();
  }
};
const size = (bytes = 0) => `${(bytes / 1024 / 1024).toFixed(1)} MB`;
const duration = (seconds = 0) => seconds ? `${Number(seconds).toFixed(0)}s` : "—";
onMounted(load);
onBeforeUnmount(() => window.clearTimeout(poll));
</script>
