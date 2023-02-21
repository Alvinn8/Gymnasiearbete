<script setup lang="ts">
import { useMovementAndResize } from "@/composables/resize";
import { useSelection } from "@/stores/selection";
import type { DimensionsProperty } from "@/types";
import { toRef } from "vue";


const props = defineProps<{
    id: number;
    name: string;
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
}>();

const selection = useSelection("room", toRef(props, "id"));

const movement = useMovementAndResize({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => {}
});

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
        :class="selection.selected.value ? 'hover' : null"
        @mousedown="movement.mousedown"
    >
        <span>{{ name }}</span>
    </div>
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