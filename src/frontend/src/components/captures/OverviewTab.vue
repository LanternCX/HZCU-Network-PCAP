<template>
  <div class="grid">
    <article class="card span-3"><p>Total Packets</p><strong class="mono">{{ capture.packet_count }}</strong></article>
    <article class="card span-3"><p>Capture Duration</p><strong>{{ capture.duration_seconds }}s</strong></article>
    <article class="card span-3"><p>Average Packets Per Second</p><strong>{{ pps }}</strong></article>
    <article class="card span-3"><p>Total Traffic Size</p><strong>{{ size(capture.total_bytes) }}</strong></article>
    <article class="card span-3"><p>Source IP Count</p><strong>{{ stats.summary.source_ip_count || 0 }}</strong></article>
    <article class="card span-3"><p>Destination IP Count</p><strong>{{ stats.summary.destination_ip_count || 0 }}</strong></article>
    <section class="panel span-6">
      <h2>Basic Information</h2>
      <p>Original filename: {{ capture.original_name }}</p>
      <p>File type: {{ capture.file_type }}</p>
      <p>File size: {{ size(capture.file_size) }}</p>
      <p>Capture start time: {{ capture.started_at || "—" }}</p>
      <p>Capture end time: {{ capture.ended_at || "—" }}</p>
      <p>Analysis time: {{ capture.analysis_time || "—" }}</p>
    </section>
    <section class="panel span-6">
      <h2>Top Protocols</h2>
      <p v-for="row in stats.protocols" :key="row[0]" class="mono">{{ row[0] }} · {{ row[1] }}</p>
      <h2 style="margin-top:16px">Top Destination Ports</h2>
      <p v-for="row in stats.top_ports" :key="row[0]" class="mono">{{ row[0] }} · {{ row[1] }}</p>
    </section>
    <section class="panel span-6">
      <h2>Top Source IPs</h2><p v-for="row in stats.top_sources" :key="row[0]" class="mono">{{ row[0] }} · {{ row[1] }}</p>
    </section>
    <section class="panel span-6">
      <h2>Top Destination IPs</h2><p v-for="row in stats.top_destinations" :key="row[0]" class="mono">{{ row[0] }} · {{ row[1] }}</p>
    </section>
    <EChartPanel class="span-6" title="Compact Protocol Distribution" :summary="`${stats.protocols.length} protocols in this capture.`" :option="protocolChart" />
    <EChartPanel class="span-6" title="Compact Traffic Trend" :summary="`${stats.traffic_trend.length} time buckets in this capture.`" :option="trendChart" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import EChartPanel from "../charts/EChartPanel.vue";
import { api } from "../../api/client";

const props = defineProps<{ capture: any }>();
const stats = ref<any>({ summary: {}, protocols: [], traffic_trend: [], top_sources: [], top_destinations: [], top_ports: [] });
const pps = computed(() => props.capture.duration_seconds ? (props.capture.packet_count / props.capture.duration_seconds).toFixed(2) : "—");
const size = (bytes = 0) => `${(bytes / 1024 / 1024).toFixed(1)} MB`;
const protocolChart = computed(() => ({ series: [{ type: "pie", data: stats.value.protocols.map(([name, value]: any[]) => ({ name, value })) }] }));
const trendChart = computed(() => ({
  xAxis: { type: "category", data: stats.value.traffic_trend.map(([name]: any[]) => name.slice(11, 19)) },
  yAxis: { type: "value" },
  series: [{ type: "line", data: stats.value.traffic_trend.map(([, value]: any[]) => value) }],
}));
onMounted(async () => { stats.value = await api.stats(props.capture.id); });
</script>
