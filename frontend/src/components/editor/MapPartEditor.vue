<script setup lang="ts">
import { apiGet, apiPost, handleError } from "@/api/api";
import type { DimensionsProperty, Point, Position, Wall, PointConnection as PointConnectionType } from "@/types";
import { onMounted, onUnmounted, provide, ref, toRef, watch } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";
import ChangeBackground from "./ChangeBackground.vue";
import EditablePoint from "./EditablePoint.vue";
import EditableWall from "./EditableWall.vue";
import NewPoint from "./NewPoint.vue";
import NewWall from "./NewWall.vue";
import PointConnection from "./PointConnection.vue";
import ConnectLine from "./ConnectLine.vue";
import MapEditorBase from "./MapEditorBase.vue";

const props = defineProps<{
    mapPartId: number;
}>();

const emit = defineEmits<{
    (e: "back"): void;
}>();

const name = ref<string | null>(null);
const walls = ref<Wall[] | null>(null);
const points = ref<Point[] | null>(null);
const pointConnections  = ref<PointConnectionType[] | null>(null);
const background = ref<string | null>(null);
const backgroundScale = ref<number | null>(null);

const route = useRoute();

provide(mapPartIdKey, toRef(props, "mapPartId"));

const connectionCallbacks = {
    clickPoint: (point: Point) => {},
    rightClickPoint: (e: MouseEvent, point: Point) => {}
};

watch(props, async () => {
    const info = await apiGet(`map/${route.params.map_id}/part/${props.mapPartId}/info`)
        .catch(handleError);
    if (!info) return;

    name.value = info.name;
    walls.value = info.walls;
    points.value = info.points;
    background.value = info.background;
    backgroundScale.value = info.background_scale;
    pointConnections.value = info.point_connections.map((pointConnection: any) => {
        const pointA = points.value?.find(point => point.id === pointConnection.point_a_id);
        const pointB = points.value?.find(point => point.id === pointConnection.point_b_id);
        if (pointA && pointB) {
            return {
                id: pointConnection.id,
                point_a: pointA,
                point_b: pointB,
                weight: pointConnection.weight
            };
        }
        return null;
    }).filter((c: any) => !!c); // Remove any null items
}, { immediate: true });

const changedWalls: Set<Wall> = new Set();
const changedPoints: Set<Point> = new Set();
let pendingChangesId: number | null = null;

function updateWall(wallId: number, property: DimensionsProperty, value: number) {
    // Find the wall in question
    const wall = walls.value?.find(w => w.id === wallId);
    if (!wall) return;
    
    // Update the wall
    wall[property] = value;
    
    // Add the wall to the set of walls with changes
    changedWalls.add(wall);

    // And save when its time
    saveWithDebounce();
}

function updatePoint(pointId: number, property: keyof Position, value: number) {
    // Find the point in question
    const point = points.value?.find(p => p.id === pointId);
    if (!point) return;

    // Update the point
    point[property] = value;

    // Add to the set of changes
    changedPoints.add(point);

    // And save when its time
    saveWithDebounce();
}

function saveWithDebounce() {

    // Use debounce to only update when no changes are being made to avoid spamming
    // updates for every small movement.

    if (pendingChangesId) clearTimeout(pendingChangesId);
    pendingChangesId = setTimeout(async () => {
        
        // If walls have been changed
        if (changedWalls.size > 0) {
            // Write the changes to the database
            await apiPost(`map/${route.params.map_id}/part/${props.mapPartId}/wall/edit`, {
                // Convert the changedWalls set into an array
                changes: [...changedWalls.values()]
            }).catch(handleError);
            
            // Clear the set of changed walls, they are now up-to-date
            changedWalls.clear();
        }

        if (changedPoints.size > 0) {
            // Write the changes to the database
            await apiPost(`map/${route.params.map_id}/part/${props.mapPartId}/point/edit`, {
                // Convert the changedPoints set into an array
                changes: [...changedPoints.values()]
            }).catch(handleError);
            
            // Clear the set of changed points, they are now up-to-date
            changedPoints.clear();
        }

        // Log
        console.log("%c ✔ Saved", "color: green;");
    }, 5000);
}

function beforeUnload(e: BeforeUnloadEvent) {
    // If the user has walls that are changed but not saved yet, then prompt the
    // user to confirm if they want to leave the page.
    if (changedWalls.size > 0) {
        e.preventDefault();
        return e.returnValue = "";
    }
}

onMounted(() => {
    window.addEventListener("beforeunload", beforeUnload);
});
onUnmounted(() => {
    window.removeEventListener("beforeunload", beforeUnload);
});

</script>

<template>
    <MapEditorBase>
        <template #aside>
            <h2>{{ name }}</h2>
            <button class="btn btn-primary mx-1" @click="emit('back')">Tillbaka</button>
            <NewWall
                @new-wall="(wall) => walls?.push(wall)"
            />
            <NewPoint
                @new-point="(point) => points?.push(point)"
            />
            <ChangeBackground
                :scale="backgroundScale"
                @change-background="(newBackground) => background = newBackground"
                @change-scale="(scale) => backgroundScale = scale"
            />
        </template>
        <template #panzoom>
            <img
                v-if="background"
                :src="background"
                alt="Bakgrund"
                :style="`transform: scale(${backgroundScale});`"
            >
            <div v-if="walls">
                <!-- Render the walls. -->
                <EditableWall
                    v-for="wall of walls"
                    :key="wall.id"
                    :x="wall.x" :y="wall.y"
                    :width="wall.width" :height="wall.height"
                    @change="(property, value) => updateWall(wall.id, property, value)"
                    @copy="(wall) => walls?.push(wall)"
                />
                <!-- Render points. -->
                <EditablePoint
                    v-for="point of points"
                    :key="point.id"
                    :x="point.x"
                    :y="point.y"
                    @change="(property, value) => updatePoint(point.id, property, value)"
                    @copy="(point) => points?.push(point)"
                    @click="() => connectionCallbacks.clickPoint(point)"
                    @right-click="(e) => connectionCallbacks.rightClickPoint(e, point)"
                />
                <!-- Render connections between points. -->
                <PointConnection
                    v-for="pointConnection of pointConnections"
                    :key="pointConnection.id"
                    :point_a="pointConnection.point_a"
                    :point_b="pointConnection.point_b"
                />
                <!-- This component handles creating new connections. -->
                <ConnectLine
                    @callbacks="(clickPoint, rightClickPoint) => {
                        connectionCallbacks.clickPoint = clickPoint;
                        connectionCallbacks.rightClickPoint = rightClickPoint;
                    }"
                    @new-connection="(connection) => pointConnections?.push(connection)"
                />
            </div>
        </template>
    </MapEditorBase>
</template>