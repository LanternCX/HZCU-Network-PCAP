<template>
  <section class="dashboard-page">
    <div class="page-head">
      <div>
        <h1>Dashboard</h1>
        <p>System-wide capture health, trends, and hotspots.</p>
      </div>
      <label class="btn primary">
        Upload Capture
        <input type="file" accept=".pcap,.pcapng" hidden @change="upload" />
      </label>
    </div>

    <div v-if="!captures.length" class="empty">No captures yet. Upload a PCAP or PCAPNG file to start analysis.</div>
    <div class="dashboard-grid" v-else>
      <div class="metric-strip">
        <article class="card"><p>Total Captures</p><strong>{{ stats.summary.total_captures }}</strong></article>
        <article class="card"><p>Total Packets</p><strong class="mono">{{ stats.summary.total_packets }}</strong></article>
        <article class="card"><p>Total Size</p><strong>{{ size(stats.summary.total_size) }}</strong></article>
        <article class="card"><p>Completed</p><strong>{{ stats.summary.completed }}</strong></article>
        <article class="card"><p>Failed/Alerts</p><strong>{{ stats.summary.failed }}</strong></article>
      </div>

      <section class="table-panel recent-captures">
        <table>
          <thead><tr><th>Recent Captures</th><th>Uploaded At</th><th>Packets</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="capture in captures.slice(0, 6)" :key="capture.id">
              <td><RouterLink :to="`/captures/${capture.id}`">{{ capture.original_name }}</RouterLink></td>
              <td>{{ capture.uploaded_at }}</td>
              <td class="mono">{{ capture.packet_count }}</td>
              <td><span class="status" :class="capture.status">{{ capture.status }}</span></td>
              <td><RouterLink class="btn" :to="`/captures/${capture.id}`">Open</RouterLink></td>
            </tr>
          </tbody>
        </table>
      </section>

      <EChartPanel class="protocol-chart" title="Protocol Distribution" :summary="protocolSummary" :option="protocolChart" />
      <EChartPanel class="trend-chart" title="Traffic Trend" :summary="trendSummary" :option="trendChart">
        <select v-model="metric" aria-label="Metric"><option>Packets</option><option>Bytes</option></select>
        <select v-model="interval" aria-label="Interval"><option>1 second</option><option>10 seconds</option><option>1 minute</option></select>
        <select v-model="protocol" aria-label="Protocol filter"><option value="">All protocols</option><option v-for="row in stats.protocols" :key="row[0]">{{ row[0] }}</option></select>
      </EChartPanel>

      <section class="panel top-list"><h2>Top Source IPs</h2><p v-for="row in stats.top_sources" :key="row[0]" class="mono">{{ row[0] }} · {{ row[1] }}</p></section>
      <section class="panel top-list"><h2>Top Destination IPs</h2><p v-for="row in stats.top_destinations" :key="row[0]" class="mono">{{ row[0] }} · {{ row[1] }}</p></section>
      <section class="panel top-list"><h2>Top Destination Ports</h2><p v-for="row in stats.top_ports" :key="row[0]" class="mono">{{ row[0] }} · {{ row[1] }}</p></section>
      <EChartPanel class="size-chart" title="Packet Size Distribution" :summary="sizeSummary" :option="sizeChart" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import EChartPanel from "../components/charts/EChartPanel.vue";
import { api } from "../api/client";

const captures = ref<any[]>([]);
const stats = ref<any>({ summary: {}, protocols: [], traffic_trend: [], top_sources: [], top_destinations: [], top_ports: [], packet_sizes: [] });
const metric = ref("Packets");
const interval = ref("1 second");
const protocol = ref("");

const load = async () => {
  captures.value = await api.captures();
  stats.value = await api.stats();
};
const upload = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (file) await api.upload(file);
  await load();
};
const size = (bytes = 0) => `${(bytes / 1024 / 1024).toFixed(1)} MB`;
const protocolSummary = computed(() => `${stats.value.protocols.length} protocols found across completed captures.`);
const trendSummary = computed(() => `${trendRows.value.length} ${interval.value} buckets show ${metric.value.toLowerCase()} activity.`);
const sizeSummary = computed(() => `${stats.value.packet_sizes.length} packet size buckets are represented.`);
const protocolChart = computed(() => ({
  color: ["#006bff", "#00a6a6", "#f59e0b", "#64748b"],
  tooltip: {},
  series: [{ type: "pie", radius: ["48%", "76%"], data: stats.value.protocols.map(([name, value]: any[]) => ({ name, value })) }],
}));
const trendChart = computed(() => ({
  color: ["#006bff"],
  xAxis: { type: "category", data: trendRows.value.map(([name]: any[]) => name.slice(11, 19)) },
  yAxis: { type: "value" },
  series: [{ type: "line", smooth: true, areaStyle: {}, data: trendRows.value.map(([, value]: any[]) => value) }],
}));
const sizeChart = computed(() => ({
  color: ["#006bff"],
  xAxis: { type: "category", data: stats.value.packet_sizes.map(([name]: any[]) => name) },
  yAxis: { type: "value" },
  series: [{ type: "bar", data: stats.value.packet_sizes.map(([, value]: any[]) => value) }],
}));

const trendRows = computed(() => {
  const source = metric.value === "Bytes"
    ? (protocol.value ? stats.value.traffic_trend_bytes_by_protocol?.[protocol.value] : stats.value.traffic_trend_bytes)
    : (protocol.value ? stats.value.traffic_trend_by_protocol?.[protocol.value] : stats.value.traffic_trend);
  return groupTrend(source || [], interval.value);
});

const groupTrend = (rows: any[], selectedInterval: string) => {
  const seconds = selectedInterval === "1 minute" ? 60 : selectedInterval === "10 seconds" ? 10 : 1;
  const grouped = new Map<string, number>();
  for (const [timestamp, value] of rows) {
    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) {
      grouped.set(timestamp, (grouped.get(timestamp) || 0) + value);
      continue;
    }
    date.setUTCSeconds(Math.floor(date.getUTCSeconds() / seconds) * seconds, 0);
    const key = date.toISOString().slice(0, 19);
    grouped.set(key, (grouped.get(key) || 0) + value);
  }
  return [...grouped.entries()].sort();
};

onMounted(load);
</script>
