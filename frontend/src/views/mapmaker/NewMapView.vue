<script setup lang="ts">
import { apiPost, handleNetworkError } from "@/api/api";
import router from "@/router";
import { computed, ref } from "vue";

const name = ref<string>("");

const canSubmit = computed(() => {
    return name.value.length > 0;
});

async function submit() {
    const response = await apiPost("map/new", {
            name: name.value
        })
        .catch(handleNetworkError);
    router.push({
        name: "map",
        params: {
            map_id: response.id
        }
    });
}

</script>

<template>
    <div class="container">
        <h1>Skapa ny karta</h1>
        <div class="mb-3">
            <label for="name" class="form-label">Namn på kartan</label>
            <input id="name" v-model="name" class="form-control">
        </div>
        <button class="btn btn-success" :disabled="!canSubmit" @click="submit">Skapa karta</button>
    </div>
</template>

<style scoped>
.container {
    max-width: 600px;
}
</style>