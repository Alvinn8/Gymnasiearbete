<script setup lang="ts">
import { apiGet, handleError } from "@/api/api";
import type { Point, Room, Wall } from "@/types";
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import MapRoom from "./MapRoom.vue";
import MapWall from "./MapWall.vue";

const props = defineProps<{
    mapPartId: number;
    offsetX: number;
    offsetY: number;
    rotationDeg: number;
}>();

const emit = defineEmits<{
    (e: "data", data: Data): void;
}>();

type Data = {
    walls: Wall[];
    points: Point[];
    rooms: Room[];
};

const data = ref<Data | null>(null);

const route = useRoute();

watch(
    () => props.mapPartId,
    async () => {
        const info = await apiGet(`map/${route.params.map_id}/part/${props.mapPartId}/brief_info`)
            .catch(handleError);
        if (!info) return;

        data.value = {
            walls: info.walls,
            points: info.points,
            rooms: info.rooms
        };
        emit("data", data.value);
    },
    { immediate: true }
);

</script>

<template>
    <div
        v-if="data"
        :style="`transform: rotate(${rotationDeg}deg);`"
    >
        <MapWall
            v-for="wall of data.walls"
            :key="wall.id"
            :x="wall.x + offsetX"
            :y="wall.y + offsetY"
            :width="wall.width"
            :height="wall.height"
        />

        <MapRoom
            v-for="room of data.rooms"
            :key="room.id"
            :id="room.id"
            :name="room.name"
            :x="room.x + offsetX"
            :y="room.y + offsetY"
            :width="room.width"
            :height="room.height"
        />
    </div>
</template>

<style scoped>
div {
    /* Avoid the image moving around weirdly when it is rotated. Overflow is
       enabled anyways, so the content is still visible. */
    width: 0px;
    height: 0px;
}
</style>