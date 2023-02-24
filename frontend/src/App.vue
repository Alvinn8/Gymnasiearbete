<script setup lang="ts">
import { RouterView, useRoute } from "vue-router";
import AppHeader from "./components/AppHeader.vue";

const route = useRoute();

</script>

<template>
  <AppHeader
    v-if="route.name !== 'view-map'"
  />
  <RouterView />
</template>

<style>
html, body, #app {
  height: 100%;
}
</style>