<script setup lang="ts">
import { apiPost } from "@/api/api";
import { mapPartIdKey, panzoomKey } from "@/components/keys";
import type { Point, PointConnection as PointConnectionType, Position } from "@/types";
import { inject, onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import PointConnection from "./PointConnection.vue";

const emit = defineEmits<{
    (e: "new-connection", connection: PointConnectionType): void
    (e: "callbacks", clickPoint: (point: Point) => void, rightClickPount: (point: Point) => void): void
}>();

const selectedPoint = ref<Point | null>(null);
const mousePosition = ref<Position | null>(null);
const route = useRoute();
    
const mapPartId = inject(mapPartIdKey);
const panzoom = inject(panzoomKey);

async function formNewConnection(pointA: Point, pointB: Point) {
    document.body.removeEventListener("mousemove", mouseMove);
    mousePosition.value = null;
    selectedPoint.value = null;
    const distance = Math.sqrt(
        Math.pow(pointA.x - pointB.x, 2) +
            Math.pow(pointA.y - pointB.y, 2)
    );
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/point_connection/new`, {
        point_a_id: pointA.id,
        point_b_id: pointB.id,
        weight: distance
    });
    const connectionId = res.id;
    const connection: PointConnectionType = {
        id: connectionId,
        point_a: pointA,
        point_b: pointB
    };
    emit("new-connection", connection);
}

function mouseMove(e: MouseEvent) {
    const scale = panzoom?.value.getTransform().scale;
    if (!scale) return;
    mousePosition.value = {
        x: e.clientX / scale,
        y: e.clientY / scale
    };
}

function clickPoint(point: Point) {
    if (selectedPoint.value) {
        formNewConnection(selectedPoint.value, point);
    }
}
    
function rightClickPount(point: Point) {
    if (selectedPoint.value) {
        formNewConnection(selectedPoint.value, point);
    } else {
        selectedPoint.value = point;
        document.body.addEventListener("mousemove", mouseMove);
    }
}

emit("callbacks", clickPoint, rightClickPount);

onUnmounted(() => {
    document.body.removeEventListener("mousemove", mouseMove);
});
</script>

<template>
    <PointConnection
        v-if="selectedPoint && mousePosition"
        :point_a="selectedPoint"
        :point_b="mousePosition"
    />
</template>