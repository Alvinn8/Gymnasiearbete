<script setup lang="ts">
import { ref } from 'vue';

const username = ref<string>("");
const password = ref<string>("");
</script>

<template>
    <p>Hello</p>
    <input type="text" v-model="username">
    <input type="password" v-model="password">
</template>