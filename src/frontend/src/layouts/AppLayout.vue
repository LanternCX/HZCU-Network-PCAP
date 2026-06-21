<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/" aria-label="Network Capture Analyzer dashboard">
        <span class="brand-mark">N</span>
        <span><strong>NCA</strong><small>Network Capture Analyzer</small></span>
      </RouterLink>
      <nav aria-label="Global">
        <RouterLink to="/" exact-active-class="active">Dashboard</RouterLink>
        <RouterLink to="/captures" active-class="active">Captures</RouterLink>
        <RouterLink to="/settings" active-class="active">Settings</RouterLink>
      </nav>
    </aside>
    <main>
      <RouterView />
    </main>
  </div>
</template>
