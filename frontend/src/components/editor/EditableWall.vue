<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import { useMovementAndResize } from "@/composables/resize";
import { useSelection } from "@/stores/selection";
import type { DimensionsProperty, Wall } from "@/types";
import { inject, toRef } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";

const props = defineProps<{
    id: number;
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

const selection = useSelection("wall", toRef(props, "id"));

const movement = useMovementAndResize({
    dimensions: props,
    selection: selection,
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
        :class="selection.selected.value ? 'hover' : null"
        @mousedown="movement.mousedown"
        @click="selection.select()"
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