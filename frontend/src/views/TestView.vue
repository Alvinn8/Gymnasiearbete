<script setup lang="ts">
import { apiGet, handleError } from "@/api/api";
import { ref } from "vue";

const data = ref<{ username: string, success: boolean } | null>(null);
const error = ref<string | null>(null);

async function fetchData() {
    data.value = await apiGet("account/info");
}
fetchData().catch(err => error.value = "Error: " + err);

function test() {
    apiGet("test")
        .then(json => alert("json = " + JSON.stringify(json)))
        .catch(handleError);
}
</script>

<template>
  <div>
    <div v-if="data">
      <p>{{ data.username }}</p>
    </div>
    <p v-if="error">
      {{ error }}
    </p>
    <div v-if="data && !data.success">
      <p>{{ JSON.stringify(data) }}</p>
    </div>
    <button @click="test">Test</button>
  </div>
</template>