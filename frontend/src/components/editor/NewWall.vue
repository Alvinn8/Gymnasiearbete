<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import type { Wall } from "@/types";
import { useRoute } from "vue-router";

const props = defineProps<{
    currentMapPartId: number
}>();

const emit = defineEmits<{
    (e: "new-wall", wall: Wall): void
}>();

const route = useRoute();

async function newWall() {
    const res = await apiPost(`map/${route.params.map_id}/part/${props.currentMapPartId}/wall/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const wall = {
        id: res.id,
        x: 0,
        y: 0,
        width: 10,
        height: 40
    };

    emit("new-wall", wall);
}

</script>

<template>
    <button class="btn btn-success" @click="newWall">Ny vägg</button>
</template>