<script setup lang="ts">
import { apiGet, handleError } from "@/api/api";
import type { Point, Wall } from "@/types";
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import MapWall from "./MapWall.vue";

const props = defineProps<{
    mapPartId: number;
}>();

const data = ref<{ walls: Wall[], points: Point[] } | null>(null);

const route = useRoute();

watch(
    () => props.mapPartId,
    async () => {
        const info = await apiGet(`map/${route.params.map_id}/part/${props.mapPartId}/brief_info`)
            .catch(handleError);
        if (!info) return;

        data.value = {
            walls: info.walls,
            points: info.points
        };
    },
    { immediate: true }
);

</script>

<template>
    <div
        v-if="data"
    >
        <MapWall
            v-for="wall of data.walls"
            :key="wall.id"
            :x="wall.x"
            :y="wall.y"
            :width="wall.width"
            :height="wall.height"
        />
    </div>
</template>