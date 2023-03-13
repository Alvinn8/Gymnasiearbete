<script setup lang="ts">
import { useMovementAndResize } from "@/composables/resize";
import { useKeybindInfo } from "@/stores/keybindsInfo";
import { useSelection } from "@/stores/selection";
import { useViewMode } from "@/stores/viewMode";
import type { DimensionsProperty, Position } from "@/types";
import { toRef, watch } from "vue";
import PointConnection from "./PointConnection.vue";


const props = defineProps<{
    id: number;
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
    point: Position;
}>();

const emit = defineEmits<{
    /**
     * Called when the wall dimensions change.
     */
    (e: "change", property: DimensionsProperty, value: number): void;
    /**
     * Called when the user wishes to change the category of the room.
     */
    (e: "change-category"): void;
}>();

const selection = useSelection("room", toRef(props, "id"));
const viewMode = useViewMode();
const keybindInfo = useKeybindInfo();

const movement = useMovementAndResize({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => {},
    customKeybinds: {
        "q": () => emit("change-category")
    }
});

watch(selection.selected, (selected) => {
    if (selected) {
        keybindInfo.groups = [
            ...movement.description,
            keybindInfo.invert,
            keybindInfo.faster,
            keybindInfo.copy,
            {
                id: "change_category",
                description: "Ändra rumkategori",
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
        @mousedown="(e) => { movement.mousedown(e); selection.select() }"
    >
        <span>{{ name }}</span>
    </div>
    <PointConnection
        v-if="selection.selected.value"
        :point_a="{ x: x + width / 2, y: y + height / 2 }"
        :point_b="point"
    />
</template>

<style scoped>
div {
    background-color: rgba(0, 0, 0, 0.15);
    position: absolute;
    z-index: 2;
    
    /* center text */
    display: flex;
    justify-content: center;
    align-items: center;
}
span {
    background: black;
    color: white;
    padding: 3px;
    border-radius: 5px;
    font-size: 12px;
}
.hover {
    background-color: rgba(0, 0, 0, 0.3);
}
</style>