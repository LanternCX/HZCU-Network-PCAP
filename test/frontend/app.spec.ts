import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";

import App from "../../src/frontend/src/App.vue";
import { routes } from "../../src/frontend/src/router";

describe("Network Capture Analyzer shell", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (path: string) => {
        const body = path.includes("/packets")
          ? { items: [], total: 0 }
          : path.includes("/statistics")
            ? { summary: {}, protocols: [], traffic_trend: [], top_sources: [], top_destinations: [], top_ports: [], packet_sizes: [] }
            : path.includes("/ai/context")
              ? { protocols: [], top_sources: [], top_destinations: [], top_ports: [], packet_sample: [] }
              : path.match(/\/api\/captures\/\d+$/)
                ? { id: 1, original_name: "demo.pcapng", status: "Completed", packet_count: 1, file_size: 128, duration_seconds: 1, uploaded_at: "2026-06-21" }
                : [];
        return { ok: true, json: async () => body };
      }),
    );
  });

  it("keeps global navigation limited to dashboard, captures, and settings", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes,
    });
    await router.push("/");
    await router.isReady();

    const wrapper = mount(App, {
      global: { plugins: [router] },
    });

    expect(wrapper.text()).toContain("Dashboard");
    expect(wrapper.text()).toContain("Captures");
    expect(wrapper.text()).toContain("Settings");
    expect(wrapper.text()).not.toContain("Packets");
    expect(wrapper.text()).not.toContain("AI Analysis");
  });

  it("renders capture detail tabs inside the selected capture route", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes,
    });
    await router.push("/captures/1?tab=packets");
    await router.isReady();

    const wrapper = mount(App, {
      global: { plugins: [router] },
    });
    await flushPromises();

    expect(wrapper.text()).toContain("Overview");
    expect(wrapper.text()).toContain("Packets");
    expect(wrapper.text()).toContain("AI Analysis");
  });
});
