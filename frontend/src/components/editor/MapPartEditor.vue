<script setup lang="ts">
import { apiGet, apiPost, handleError } from "@/api/api";
import type { DimensionsProperty, Point, Position, Wall, PointConnection as PointConnectionType, Room } from "@/types";
import { onMounted, onUnmounted, provide, ref, toRef, watch } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";
import ChangeBackground from "./ChangeBackground.vue";
import EditablePoint from "./EditablePoint.vue";
import EditableWall from "./EditableWall.vue";
import EditableRoom from "./EditableRoom.vue";
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

const data = ref<null | {
    name: string;
    walls: Wall[];
    points: Point[];
    rooms: Room[];
    pointConnections: PointConnectionType[];
    background: string | null;
    backgroundScale: number;
}>();

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

    data.value = {
        name: info.name,
        walls: info.walls,
        points: info.points,
        rooms: info.rooms,
        background: info.background,
        backgroundScale: info.background_scale,
        pointConnections: info.point_connections.map((pointConnection: any) => {
            const pointA = info.points.find((point: Point) => point.id === pointConnection.point_a_id);
            const pointB = info.points.find((point: Point) => point.id === pointConnection.point_b_id);
            if (pointA && pointB) {
                return {
                    id: pointConnection.id,
                    point_a: pointA,
                    point_b: pointB,
                    weight: pointConnection.weight
                };
            }
            return null;
        }).filter((c: any) => !!c) // Remove any null items
    };
}, { immediate: true });

const changedWalls: Set<Wall> = new Set();
const changedPoints: Set<Point> = new Set();
const changedRooms: Set<Room> = new Set();
let pendingChangesId: number | null = null;

function updateWall(wallId: number, property: DimensionsProperty, value: number) {
    // Find the wall in question
    const wall = data.value?.walls.find(w => w.id === wallId);
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
    const point = data.value?.points.find(point => point.id === pointId);
    if (!point) return;

    // Update the point
    point[property] = value;

    // Add to the set of changes
    changedPoints.add(point);

    // And save when its time
    saveWithDebounce();
}

function updateRoom(roomId: number, property: DimensionsProperty, value: number) {
    // Find the room
    const room = data.value?.rooms.find(room => room.id === roomId);
    if (!room) return;

    // Update the point
    room[property] = value;

    // Add to the set of changes
    changedRooms.add(room);

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

        if (changedRooms.size > 0) {
            // Write to database
            await apiPost(`map/${route.params.map_id}/part/${props.mapPartId}/room/edit`, {
                // Convert the set into an array
                changes: [...changedRooms.values()]
            }).catch(handleError);

            // Clear the set of changes as they are now up-to-date
            changedRooms.clear();
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

function changeBackgroundScale(newScale: number) {
    if (!data.value) return;

    const oldScale = data.value.backgroundScale;
    const scaleFactor = newScale / oldScale;
    data.value.backgroundScale = newScale;
    data.value.walls.forEach(wall => {
        updateWall(wall.id, "x", wall.x * scaleFactor);
        updateWall(wall.id, "y", wall.y * scaleFactor);
        updateWall(wall.id, "width", wall.width * scaleFactor);
        updateWall(wall.id, "height", wall.height * scaleFactor);
    });
    data.value.points.forEach(point => {
        updatePoint(point.id, "x", point.x * scaleFactor);
        updatePoint(point.id, "y", point.y * scaleFactor);
    });
}

</script>

<template>
    <MapEditorBase>
        <template #aside>
            <h2>{{ data?.name }}</h2>
            <button class="btn btn-primary mx-1" @click="emit('back')">Tillbaka</button>
            <NewWall
                @new-wall="(wall) => data?.walls.push(wall)"
            />
            <NewPoint
                @new-point="(point) => data?.points.push(point)"
            />
            <ChangeBackground
                v-if="data"
                :scale="data.backgroundScale"
                @change-background="(newBackground) => data && (data.background = newBackground)"
                @change-scale="changeBackgroundScale"
            />
        </template>
        <template #panzoom>
            <img
                v-if="data && data.background"
                :src="data.background"
                alt="Bakgrund"
                :style="`transform: scale(${data.backgroundScale}); transform-origin: top left;`"
            >
            <div v-if="data">
                <!-- Render the walls. -->
                <EditableWall
                    v-for="wall of data.walls"
                    :key="wall.id"
                    :id="wall.id"
                    :x="wall.x" :y="wall.y"
                    :width="wall.width" :height="wall.height"
                    @change="(property, value) => updateWall(wall.id, property, value)"
                    @copy="(wall) => data && data.walls.push(wall)"
                />
                <!-- Render points. -->
                <EditablePoint
                    v-for="point of data.points"
                    :key="point.id"
                    :id="point.id"
                    :x="point.x"
                    :y="point.y"
                    @change="(property, value) => updatePoint(point.id, property, value)"
                    @copy="(point) => data && data.points.push(point)"
                    @click="() => connectionCallbacks.clickPoint(point)"
                    @right-click="(e) => connectionCallbacks.rightClickPoint(e, point)"
                    @new-room="(room) => data && data.rooms.push(room)"
                />
                <!-- Render connections between points. -->
                <PointConnection
                    v-for="pointConnection of data.pointConnections"
                    :key="pointConnection.id"
                    :point_a="pointConnection.point_a"
                    :point_b="pointConnection.point_b"
                />
                <!-- Render rooms -->
                <EditableRoom
                    v-for="room of data.rooms"
                    :key="room.id"
                    :id="room.id"
                    :name="room.name"
                    :x="room.x"
                    :y="room.y"
                    :width="room.width"
                    :height="room.height"
                    @change="(property, value) => updateRoom(room.id, property, value)"
                />
                <!-- This component handles creating new connections. -->
                <ConnectLine
                    @callbacks="(clickPoint, rightClickPoint) => {
                        connectionCallbacks.clickPoint = clickPoint;
                        connectionCallbacks.rightClickPoint = rightClickPoint;
                    }"
                    @new-connection="(connection) => data && data.pointConnections.push(connection)"
                />
            </div>
        </template>
    </MapEditorBase>
</template>