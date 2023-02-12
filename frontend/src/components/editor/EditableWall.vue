<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import { useMovementAndResize } from "@/composables/resize";
import type { DimensionsProperty, Wall } from "@/types";
import { inject } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";

const props = defineProps<{
    x: number;
    y: number;
    width: number;
    height: number;
}>();

const emit = defineEmits<{
    /**
     * Called when the wall dimensions change.
     */
    (e: "change", property: DimensionsProperty, value: number): void;
    
    /**
     * Called when the user presses a key to copy the wall.
     */
    (e: "copy", wall: Wall): void;
}>();

const mapPartId = inject(mapPartIdKey);
const route = useRoute();

const movement = useMovementAndResize({
    dimensions: props,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => copyWall()
});

async function copyWall() {
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/wall/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const wall = {
        id: res.id,
        x: props.x + 20,
        y: props.y + 20,
        width: props.width,
        height: props.height
    };

    emit("copy", wall);
}

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
        :class="movement.hovered.value ? 'hover' : null"
        @mouseover="movement.mouseover"
        @mouseout="movement.mouseout"
        @mousedown="movement.mousedown"
    ></div>
</template>

<style scoped>
div {
    background-color: black;
    position: absolute;
    z-index: 1;
}
.hover {
    background-color: gray;
}
</style>