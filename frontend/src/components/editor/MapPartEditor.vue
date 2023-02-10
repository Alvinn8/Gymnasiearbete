<script setup lang="ts">
import { apiGet, apiPost, handleError } from "@/api/api";
import type { DimensionsProperty, Wall } from "@/types";
import { inject, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";
import PanZoom from "../PanZoom.vue";
import ChangeBackground from "./ChangeBackground.vue";
import EditableWall from "./EditableWall.vue";
import NewWall from "./NewWall.vue";

const walls = ref<Wall[] | null>(null);
const background = ref<string | null>(null);
const backgroundScale = ref<number | null>(null);

const route = useRoute();
const mapPartId = inject(mapPartIdKey);

watch(mapPartId!, async () => {
    const info = await apiGet(`map/${route.params.map_id}/part/${mapPartId!.value}/info`)
        .catch(handleError);
    if (!info) return;

    walls.value = info.walls;
    background.value = info.background;
    backgroundScale.value = info.background_scale;
}, { immediate: true });

const changedWalls: Set<Wall> = new Set();
let pendingChangesId: number | null = null;

function updateWall(wallId: number, property: DimensionsProperty, value: number) {
    // Find the wall in question
    const wall = walls.value?.find(w => w.id === wallId);
    if (!wall) return;
    
    // Update the wall
    wall[property] = value;
    
    // Add the wall to the set of walls with changes
    
    changedWalls.add(wall);

    // Use debounce to only update when no changes are being made to avoid spamming
    // updates for every small movement.

    if (pendingChangesId) clearTimeout(pendingChangesId);
    pendingChangesId = setTimeout(() => {
        // Convert the changedWalls set into an array
        const changes = [...changedWalls.values()];

        // Write the changes to the database
        apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/wall/edit`, {
            changes: changes
        }).catch(handleError);

        // Clear the set of changed walls, they are now up-to-date
        changedWalls.clear();

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
    <div class="row">
        <div class="col">
            <NewWall
                @new-wall="(wall) => walls?.push(wall)"
            />
        </div>
        <div class="col">
            <ChangeBackground
                :scale="backgroundScale"
                @change-background="(newBackground) => background = newBackground"
                @change-scale="(scale) => backgroundScale = scale"
            />
        </div>
    </div>
    <div class="container-fluid">
        <PanZoom>
            <img
                v-if="background"
                :src="background"
                alt="Bakgrund"
                :style="`transform: scale(${backgroundScale});`"
            >
            <div v-if="walls">
                <EditableWall
                    v-for="wall of walls"
                    :key="wall.id"
                    :x="wall.x" :y="wall.y"
                    :width="wall.width" :height="wall.height"
                    @change="(property, value) => updateWall(wall.id, property, value)"
                    @copy="(wall) => walls?.push(wall)"
                />
            </div>
        </PanZoom>
    </div>
</template>

<style scoped>
.container-fluid {
    overflow: hidden;
    border: 2px solid #ddd;
    height: 85vh;
}

.part {
    max-width: 20em;
}
</style>