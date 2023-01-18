<script setup lang="ts">
import { apiGet, handleNetworkError } from "@/api/api";
import { useCounterStore } from "@/stores/counter";
import { ref } from "vue";

const counter = useCounterStore();

const data = ref<{ username: string, success: boolean } | null>(null);
const error = ref<string | null>(null);

async function fetchData() {
  data.value = await apiGet("account/info");
}
fetchData().catch(err => error.value = "Error: " + err);

function test() {
  apiGet("test")
    .then(json => alert("json = " + JSON.stringify(json)))
    .catch(handleNetworkError);
}
</script>

<template>
  <div>
    <p>Hello {{ counter.count }}</p>
    &nbsp;
    <button @click="counter.increment">Increment the counter</button>
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