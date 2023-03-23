<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import type { Point } from "@/types";
import { inject } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";

const emit = defineEmits<{
    (e: "new-point", point: Point): void
}>();

const route = useRoute();
const mapPartId = inject(mapPartIdKey);

async function newPoint() {
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/point/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const point = {
        id: res.id,
        x: 0,
        y: 0
    };

    emit("new-point", point);
}

</script>

<template>
    <button class="btn btn-success mx-1" @click="newPoint">Ny punkt</button>
</template>