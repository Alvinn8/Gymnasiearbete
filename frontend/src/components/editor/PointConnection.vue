<script setup lang="ts">
import type { Position } from "@/types";
import { computed } from "vue";


const props = defineProps<{
    point_a: Position,
    point_b: Position,
    color?: string;
}>();

const distance = computed(() => 
    // Pythagorean theorem (distance formula)
    Math.sqrt(
        Math.pow(props.point_a.x - props.point_b.x, 2) +
        Math.pow(props.point_a.y - props.point_b.y, 2)
    )
);

const angle = computed(() =>
    Math.atan2(
        props.point_b.y - props.point_a.y,
        props.point_b.x - props.point_a.x
    )
);

</script>

<template>
    <div :style="`left: ${point_a.x}px;
                 top: ${point_a.y}px;
                 width: ${distance}px;
                 transform: translate(0px, -1px) rotate(${angle}rad);`
                 + (color ? ('background-color: ' + color + ';') : '')"></div>
</template>

<style scoped>
div {
    position: absolute;
    background-color: #3d73e0;
    height: 2px;
    transform-origin: left;
    z-index: 3;
}
</style>