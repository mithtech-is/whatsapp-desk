<script setup>
import { FrappeUIProvider } from 'frappe-ui'
import AppShell from './components/AppShell.vue'
</script>

<template>
  <FrappeUIProvider>
    <AppShell>
      <RouterView />
    </AppShell>
  </FrappeUIProvider>
</template>
