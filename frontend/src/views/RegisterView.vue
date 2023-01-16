<script setup lang="ts">
import { ref } from "vue";
import { apiPost } from "../api/api";

const username = ref<string>("");
const password = ref<string>("");
const loading = ref<boolean>(false);

async function submit() {
    loading.value = true;
    const response = await apiPost("register", {
        username: username.value,
        password: password.value
    });
    loading.value = false;
}

</script>

<template>
    <h1>Skapa konto</h1>
    <input type="text" v-model="username">
    <input type="password" v-model="password">
    <button @click="submit" :disabled="loading">Skapa konto</button>
</template>