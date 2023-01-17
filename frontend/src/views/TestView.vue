<script setup lang="ts">
import { apiGet } from "@/api/api";
import { useCounterStore } from "@/stores/counter";
import { ref } from "vue";

const counter = useCounterStore();

const data = ref<{ username: string } | null>(null);
const error = ref<string | null>(null);

async function fetchData() {
  data.value = await apiGet("account/info");
}
fetchData().catch(err => error.value = "Error: " + err);
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
  </div>
</template>