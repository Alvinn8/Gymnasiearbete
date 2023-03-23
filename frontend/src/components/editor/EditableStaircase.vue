<script setup lang="ts">
import { useMovementAndResize } from "@/composables/resize";
import { useKeybindInfo } from "@/stores/keybindsInfo";
import { useSelection } from "@/stores/selection";
import { useViewMode } from "@/stores/viewMode";
import type { DimensionsProperty } from "@/types";
import { toRef, watch } from "vue";

const props = defineProps<{
    id: number;
    x: number;
    y: number;
    width: number;
    height: number;
}>();

const emit = defineEmits<{
    /**
     * Called when the staircase dimensions change.
     */
    (e: "change", property: DimensionsProperty, value: number): void;
}>();

const selection = useSelection("staircase", toRef(props, "id"));
const viewMode = useViewMode();
const keybindInfo = useKeybindInfo();

const movement = useMovementAndResize({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => {}
});

watch(selection.selected, (selected) => {
    if (selected) {
        keybindInfo.groups = [
            ...movement.description,
            keybindInfo.invert,
            keybindInfo.faster
        ];
    }
});

</script>

<template>
    <div :style="{
            left: x + 'px',
            top: y + 'px',
            width: width + 'px',
            height: height + 'px',
            opacity: viewMode.opacity
        }"
        :class="{ hover: selection.selected.value }"
        @mousedown="(e) => { movement.mousedown(e); selection.select(); }"
    ></div>
</template>

<style scoped>
div {
    /** Repeating lines */
    background: repeating-linear-gradient(90deg, white, white 8px, black 8px, black 10px);
    position: absolute;
    z-index: 2;
    border: 1px solid black;
    border-right-width: 0;
}
.hover {
    background-color: rgba(128, 128, 128, 0.2);
}
</style>