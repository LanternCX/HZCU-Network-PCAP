const json = async (path: string, options?: RequestInit) => {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "Request failed");
  return body;
};

export const api = {
  captures: (query = "") => json(`/api/captures${query}`),
  capture: (id: string | number) => json(`/api/captures/${id}`),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return json("/api/captures", { method: "POST", body: form });
  },
  remove: (id: number) => json(`/api/captures/${id}`, { method: "DELETE" }),
  retry: (id: number) => json(`/api/captures/${id}/retry`, { method: "POST" }),
  packets: (id: string | number, query: string) => json(`/api/captures/${id}/packets${query}`),
  packet: (id: string | number, number: number) => json(`/api/captures/${id}/packets/${number}`),
  stats: (id?: string | number) => json(id ? `/api/statistics/captures/${id}` : "/api/statistics"),
  aiContext: (id: string | number) => json(`/api/captures/${id}/ai/context`),
  settings: () => json("/api/settings"),
  saveSettings: (body: unknown) =>
    json("/api/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  testSettings: () => json("/api/settings/test", { method: "POST" }),
};
