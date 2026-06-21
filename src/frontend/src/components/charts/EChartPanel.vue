<template>
  <section class="panel">
    <div class="panel-head">
      <div>
        <h2>{{ title }}</h2>
        <p>{{ summary }}</p>
      </div>
      <slot />
    </div>
    <div ref="el" class="chart" :aria-label="summary"></div>
  </section>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps<{ title: string; summary: string; option: Record<string, unknown> }>();
const el = ref<HTMLElement>();
let chart: echarts.ECharts | undefined;

const draw = () => {
  if (!el.value) return;
  chart ||= echarts.init(el.value);
  chart.setOption(props.option);
};

onMounted(() => {
  draw();
  window.addEventListener("resize", draw);
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", draw);
  chart?.dispose();
});
watch(() => props.option, draw, { deep: true });
</script>
