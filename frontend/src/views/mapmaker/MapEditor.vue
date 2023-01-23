<script setup lang="ts">
import { apiGet, errorHandler } from "@/api/api";
import { useRoute } from "vue-router";
import { ref, watch } from "vue";
import Swal from "sweetalert2";

const route = useRoute();
const name = ref<string>("");

watch(
    () => route.params.map_id,
    async mapId => {
        const info = await apiGet(`map/${mapId}/info`)
            .catch(errorHandler([
                [json => !json.success, (json: any) => Swal.fire({
                    title: json.error,
                    icon: "error"
                })]
            ]));
        if (info) {
            name.value = info.name;
        }
    },
    { immediate: true }
);

</script>

<template>
    <h1>{{ name }}</h1>
</template>