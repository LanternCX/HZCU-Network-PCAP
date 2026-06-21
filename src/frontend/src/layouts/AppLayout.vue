<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/" aria-label="Network Capture Analyzer dashboard">
        <span class="brand-mark">N</span>
        <span><strong>NCA</strong></span>
      </RouterLink>
      <nav aria-label="Global">
        <RouterLink to="/" exact-active-class="active">
          <span class="nav-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M4 13h6v7H4zM14 4h6v16h-6zM4 4h6v5H4z" /></svg>
          </span>
          Dashboard
        </RouterLink>
        <RouterLink to="/captures" active-class="active">
          <span class="nav-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M5 6h14v4H5zM5 14h14v4H5z" /></svg>
          </span>
          Captures
        </RouterLink>
        <RouterLink to="/settings" active-class="active">
          <span class="nav-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8Zm8 5.2v-2.4l-2.3-.6-.5-1.2 1.2-2-1.7-1.7-2 1.2-1.2-.5L12.8 4h-2.4l-.6 2.3-1.2.5-2-1.2-1.7 1.7 1.2 2-.5 1.2-2.3.6v2.4l2.3.6.5 1.2-1.2 2 1.7 1.7 2-1.2 1.2.5.6 2.3h2.4l.6-2.3 1.2-.5 2 1.2 1.7-1.7-1.2-2 .5-1.2 2.3-.6Z" /></svg>
          </span>
          Settings
        </RouterLink>
      </nav>
    </aside>
    <main>
      <RouterView />
    </main>
  </div>
</template>
