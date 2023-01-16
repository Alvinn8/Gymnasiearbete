<script setup lang="ts">
import { useCounterStore } from '@/stores/counter';

const counter = useCounterStore();
</script>

<template>
    <div>
        <p>Hello {{ counter.count }}</p>
        <button @click="counter.increment">Increment the counter</button>
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
