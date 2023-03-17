<script setup lang="ts">
import { apiPost } from "@/api/api";
import { mapPartIdKey, panzoomKey } from "@/components/keys";
import type { Point, PointConnection as PointConnectionType, Position } from "@/types";
import { inject, onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import PointConnection from "./PointConnection.vue";

const emit = defineEmits<{
    (e: "new-connection", connection: PointConnectionType): void
    (e: "callbacks", clickPoint: (point: Point) => void, rightClickPount: (e: MouseEvent, point: Point) => void): void
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
    if (pointA === pointB) return;
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/point_connection/new`, {
        point_a_id: pointA.id,
        point_b_id: pointB.id
    });
    const connectionId = res.id;
    const connection: PointConnectionType = {
        id: connectionId,
        point_a: pointA,
        point_b: pointB
    };
    emit("new-connection", connection);
}

const moveStart = {
    mouseX: 0,
    mouseY: 0,
    thisX: 0,
    thisY: 0
};

function mouseMove(e: MouseEvent) {
    const scale = panzoom?.value.getTransform().scale;
    if (!scale) return;
    const diffX = (e.clientX - moveStart.mouseX) / scale;
    const diffY = (e.clientY - moveStart.mouseY) / scale;
    mousePosition.value = {
        x: moveStart.thisX + diffX,
        y: moveStart.thisY + diffY
    };
}

function clickPoint(point: Point) {
    if (selectedPoint.value) {
        formNewConnection(selectedPoint.value, point);
    }
}
    
function rightClickPoint(e: MouseEvent, point: Point) {
    if (selectedPoint.value) {
        formNewConnection(selectedPoint.value, point);
    } else {
        selectedPoint.value = point;
        mousePosition.value = {
            x: point.x,
            y: point.y
        };
        moveStart.mouseX = e.clientX;
        moveStart.mouseY = e.clientY;
        moveStart.thisX = point.x;
        moveStart.thisY = point.y;
        document.body.addEventListener("mousemove", mouseMove);
    }
}

emit("callbacks", clickPoint, rightClickPoint);

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