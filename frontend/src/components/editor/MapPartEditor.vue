<script setup lang="ts">
import { apiGet, handleError } from "@/api/api";
import type { Wall } from "@/types";
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import EditableWall from "./EditableWall.vue";

const props = defineProps<{
    mapPartId: number;
}>();

const walls = ref<Wall[] | null>(null);
const background = ref<string | null>(null);

const route = useRoute();

watch(props, async () => {
    const info = await apiGet(`map/${route.params.map_id}/part/${props.mapPartId}/info`)
        .catch(handleError);
    if (!info) return;

    walls.value = info.walls;
    background.value = info.background;
});


</script>

<template>
    <img v-if="background" :src="background" alt="Bakgrund">
    <div v-if="walls">
        <EditableWall
            v-for="wall of walls" :key="wall.id" :x="wall.x" :y="wall.y" :width="wall.width"
            :height="wall.height"
            :on-change="(property, value) => console.log(property, value)"
        />
    </div>
</template>