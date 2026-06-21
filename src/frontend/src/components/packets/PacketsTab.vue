<template>
  <section>
    <div class="panel toolbar">
      <input v-model="filters.q" placeholder="Search IP, port, or protocol" @input="load" />
      <input v-model="filters.src_ip" placeholder="Source IP" @input="load" />
      <input v-model="filters.dst_ip" placeholder="Destination IP" @input="load" />
      <input v-model="filters.port" placeholder="Port" @input="load" />
      <select v-model="filters.protocol" @change="load" aria-label="Protocol">
        <option value="">All protocols</option><option>TCP</option><option>UDP</option><option>DNS</option><option>HTTP</option><option>ICMP</option>
      </select>
      <select v-model="filters.page_size" @change="load" aria-label="Page size"><option>25</option><option>50</option><option>100</option></select>
      <button @click="reset">Reset</button>
    </div>

    <div v-if="loading" class="empty">Loading packets...</div>
    <div v-else-if="error" class="empty">{{ error }} <button @click="load">Retry</button></div>
    <div v-else-if="!packets.length" class="empty">No packets match these filters. Reset filters to view all packets.</div>
    <section v-else class="table-panel">
      <table>
        <thead>
          <tr>
            <th>No.</th><th @click="sort('timestamp')">Timestamp</th><th>Source IP</th><th>Source Port</th>
            <th>Destination IP</th><th>Destination Port</th><th>Protocol</th><th @click="sort('length')">Length</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="packet in packets" :key="packet.number" @click="open(packet.number)" @keydown.enter="open(packet.number)" @keydown.space.prevent="open(packet.number)" tabindex="0">
            <td class="mono">{{ packet.number }}</td><td class="mono">{{ packet.timestamp }}</td><td class="mono">{{ packet.src_ip }}</td>
            <td class="mono">{{ packet.src_port }}</td><td class="mono">{{ packet.dst_ip }}</td><td class="mono">{{ packet.dst_port }}</td>
            <td>{{ packet.protocol }}</td><td class="mono">{{ packet.length }}</td>
          </tr>
        </tbody>
      </table>
    </section>
    <div class="toolbar" style="margin-top:12px">
      <button :disabled="filters.page <= 1" @click="filters.page--; load()">Previous</button>
      <span>Page {{ filters.page }} · {{ total }} packets</span>
      <button :disabled="filters.page * filters.page_size >= total" @click="filters.page++; load()">Next</button>
    </div>
    <div v-if="selected" class="drawer-backdrop" @click.self="selected = null">
      <aside ref="drawer" class="drawer" role="dialog" aria-modal="true" aria-label="Packet details" tabindex="-1" @keydown.esc="selected = null" @keydown.tab="trapFocus">
        <div class="page-head"><h2>Packet {{ selected.number }}</h2><button @click="selected = null">Close</button></div>
        <section v-for="(fields, section) in selected.details" :key="section" class="panel" style="margin-bottom:12px">
          <h2>{{ section }}</h2>
          <p v-for="(value, key) in fields" :key="key" class="mono">{{ key }}: {{ value }}</p>
        </section>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from "vue";
import { api } from "../../api/client";

const props = defineProps<{ captureId: number }>();
const packets = ref<any[]>([]);
const selected = ref<any>(null);
const drawer = ref<HTMLElement>();
const total = ref(0);
const loading = ref(false);
const error = ref("");
const filters = reactive<any>({ q: "", protocol: "", src_ip: "", dst_ip: "", port: "", sort: "timestamp", direction: "asc", page: 1, page_size: 25 });

const load = async () => {
  loading.value = true;
  error.value = "";
  try {
    const body = await api.packets(props.captureId, `?${new URLSearchParams(filters).toString()}`);
    packets.value = body.items;
    total.value = body.total;
  } catch (exc: any) {
    error.value = exc.message || "Failed request.";
  } finally {
    loading.value = false;
  }
};
const reset = () => {
  Object.assign(filters, { q: "", protocol: "", src_ip: "", dst_ip: "", port: "", sort: "timestamp", direction: "asc", page: 1 });
  load();
};
const sort = (field: string) => {
  filters.direction = filters.sort === field && filters.direction === "asc" ? "desc" : "asc";
  filters.sort = field;
  load();
};
const open = async (number: number) => {
  selected.value = await api.packet(props.captureId, number);
  await nextTick();
  drawer.value?.focus();
};
const trapFocus = (event: KeyboardEvent) => {
  const buttons = drawer.value?.querySelectorAll<HTMLElement>("button, [href], [tabindex]:not([tabindex='-1'])");
  if (!buttons?.length) return;
  const first = buttons[0];
  const last = buttons[buttons.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
};
onMounted(load);
</script>
