<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import useMovement from "@/composables/movement";
import type { Point } from "@/types";
import { inject } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";


const props = defineProps<{
    x: number;
    y: number;
}>();

const emit = defineEmits<{
    /**
     * Called when the point position changes.
     */
    (e: "change", property: "x" | "y", value: number): void;
    
    /**
     * Called when the user presses a key to copy the point.
     */
    (e: "copy", wall: Point): void;

    /** Called when the point is clicked. */
    (e: "click"): void;

    /** Called when the point is right clicked. */
    (e: "right-click", ev: MouseEvent): void;
}>();

const movement = useMovement({
    dimensions: props,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => copyPoint()
});
const route = useRoute();
const mapPartId = inject(mapPartIdKey);

async function copyPoint() {
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/point/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const point = {
        id: res.id,
        x: props.x + 20,
        y: props.y + 20
    };

    emit("copy", point);
}

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;`"
        :class="movement.hovered.value ? 'hover' : null"
        @mouseover="movement.mouseover"
        @mouseout="movement.mouseout"
        @mousedown="movement.mousedown"
        @click="emit('click')"
        @contextmenu.prevent="(e) => emit('right-click', e)"
    ></div>
</template>

<style scoped>
div {
    background-color: #57bee1;
    position: absolute;
    z-index: 3;
    border-radius: 50%;
    border: 1px solid #5785e1;
    width: 10px;
    height: 10px;
    transform: translate(-5px, -5px);
}
.hover {
    background-color: gray;
}
</style>