<script setup lang="ts">
import { apiGet } from "@/api/api";
import router from "@/router";
import { onMounted, ref } from "vue";

const invalid = ref(false);

onMounted(async () => {
    const url = new URL(location.href);
    const code = url.searchParams.get("code"); 
    const state = url.searchParams.get("state");
    if (!code || !state) {
        invalid.value = true;
        const result = await apiGet("login/google/callback");
        // TODO
    }
});
</script>

<template>
    <div class="container" v-if="invalid">
        <h1>Invalid state</h1>
        <p>Försök att logga med Google igen.</p>
    </div>
</template>