<script setup lang="ts">
import { useCounterStore } from '@/stores/counter';
import { ref } from 'vue';

const counter = useCounterStore();

const data = ref<{title: string, content: string}[] | null>(null);
const error = ref<string | null>(null);

async function fetchData() {
  const response = await fetch("http://localhost:8080/api/test");
  const json = await response.json();
  data.value = json.data;
}
fetchData().catch(err => error.value = "Error: " + err);
</script>

<template>
    <div>
        <p>Hello {{ counter.count }}</p>
        &nbsp;
        <button @click="counter.increment">Increment the counter</button>
        <div v-if="data">
          <div v-for="item in data" :key="item.title">
            <h3>{{ item.title }}</h3>
            <p>{{ item.content }}</p>
          </div>
        </div>
        <p v-if="error">
          {{ error }}
        </p>
    </div>
</template>

<style scoped>
@media (min-width: 1024px) {
  div {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
