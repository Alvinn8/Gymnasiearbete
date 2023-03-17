<script setup lang="ts">
import { useSelection } from "@/stores/selection";
import { inject, ref, toRef, watch } from "vue";
import { panzoomKey } from "../keys";

const props = defineProps<{
    id: number;
    name: string | null;
    x: number;
    y: number;
    width: number;
    height: number;
}>();

const hovered = ref(false);
const selection = useSelection("room", toRef(props, "id"));

const divRef = ref<HTMLDivElement | null>(null);
const panzoom = inject(panzoomKey);

watch([selection.selected, panzoom, divRef], () => {
    if (selection.selected.value && panzoom && divRef.value) {
        const box = divRef.value.getBoundingClientRect();
        const transform = panzoom.value.getTransform();
        const x = (box.x - transform.x) / transform.scale;
        const y = (box.y - transform.y) / transform.scale;
        const width = box.width / transform.scale;
        const height = box.height / transform.scale;
        const newX = window.innerWidth / 2 - (x + width / 2) * transform.scale;
        const newY = window.innerHeight / 2 - (y + height / 2) * transform.scale;
        panzoom.value.smoothMoveTo(newX, newY);
    }
}, { immediate: true });

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
        ref="divRef"
        :class="{ selected: selection.selected.value, hovered: hovered }"
        @mouseover="() => hovered = true"
        @mouseout="() => hovered = false"
        @click="selection.select()"
        @touchend="selection.select()"
    >
        <span v-if="name">{{ name }}</span>
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