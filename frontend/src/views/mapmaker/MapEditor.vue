<script setup lang="ts">
import { apiGet, handleNetworkError } from "@/api/api";
import { useRoute } from "vue-router";
import { ref, watch } from "vue";

const route = useRoute();
const name = ref<string>("");

watch(
    () => route.params.map_id,
    async mapId => {
        console.log("hello?!?!");
        const info = await apiGet(`map/${mapId}/info`)
            .catch(handleNetworkError);
        name.value = info.name;
    }
);

</script>

<template>
    <h1>{{ name }}</h1>
    <p>Hello</p>
</template>