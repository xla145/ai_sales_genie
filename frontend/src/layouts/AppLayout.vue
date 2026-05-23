<template>
  <div class="page-shell">
    <main class="app-shell__main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-shell__main {
  min-height: 100vh;
}
</style>
