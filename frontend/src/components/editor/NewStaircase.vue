<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import type { Staircase } from "@/types";
import { inject } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";

const emit = defineEmits<{
    (e: "new-staircase", staircase: Staircase): void
}>();

const route = useRoute();
const mapPartId = inject(mapPartIdKey);

async function newStaircase() {
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/staircase/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const staircase: Staircase = {
        id: res.id,
        mapPartId: mapPartId!.value,
        x: 0,
        y: 0,
        width: 40,
        height: 40,
        connectsTo: null,
        rotationDeg: 0
    };

    emit("new-staircase", staircase);
}

</script>

<template>
    <button class="btn btn-success mx-1" @click="newStaircase">Ny trappa</button>
</template>