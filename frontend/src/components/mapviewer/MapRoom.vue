<script setup lang="ts">
import { useSelection } from "@/stores/selection";
import { inject, ref, toRef, watch } from "vue";
import { panzoomKey } from "../keys";

const props = defineProps<{
    id: number;
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
}>();

const hovered = ref(false);
const selection = useSelection("room", toRef(props, "id"));

const divRef = ref<HTMLDivElement | null>(null);
const panzoom = inject(panzoomKey);

watch(selection.selected, (selected) => {
    if (selected && panzoom && divRef.value) {
        const box = divRef.value.getBoundingClientRect();
        const transform = panzoom.value.getTransform();
        // box.x -= window.innerWidth / 2;
        // box.y -= window.innerHeight / 2;
        panzoom.value.smoothZoomAbs(box.x, box.y, 1);
    }
});

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
        ref="divRef"
        :class="(hovered ? 'hover' : '') + ' ' + (selection.selected.value ? 'selected' : '')"
        @mouseover="() => hovered = true"
        @mouseout="() => hovered = false"
        @click="selection.select()"
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
    background-color: rgba(255, 255, 255, 0.5);
    color: black;
    padding: 3px;
    border-radius: 5px;
    font-size: 25px;
}
.hover {
    background-color: rgba(0, 0, 0, 0.3);
}
.selected {
    background-color: rgba(0, 255, 0, 0.3);
}
</style>