<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import { useMovementAndResize } from "@/composables/resize";
import { DEFAULT_WALL_WIDTH } from "@/constants";
import { useKeybindInfo } from "@/stores/keybindsInfo";
import { useSelection } from "@/stores/selection";
import { useViewMode } from "@/stores/viewMode";
import type { DimensionsProperty, Wall } from "@/types";
import { inject, toRef, watch } from "vue";
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
const viewMode = useViewMode();
const keybindInfo = useKeybindInfo();

const movement = useMovementAndResize({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => copyWall(),
    customKeybinds: {
        "q": () => {
            if (props.width <= props.height) {
                emit("change", "width", DEFAULT_WALL_WIDTH);
            }
            if (props.height <= props.width) {
                emit("change", "height", DEFAULT_WALL_WIDTH);
            }
        }
    }
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

watch(selection.selected, (selected) => {
    if (selected) {
        keybindInfo.groups = [
            ...movement.description,
            keybindInfo.invert,
            keybindInfo.faster,
            keybindInfo.copy,
            {
                id: "normalize_wall_size",
                description: "Normalisera väggstorlek",
                keys: ["q"]
            }
        ];
    }
});

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;
                  opacity: ${viewMode.opacity};`"
        :class="{ hover: selection.selected.value }"
        @mousedown="(e) => { movement.mousedown(e); selection.select(); }"
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