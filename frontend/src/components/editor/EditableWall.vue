<script setup lang="ts">
import type { DimensionsProperty } from "@/types";
import { onUnmounted, ref } from "vue";

const props = defineProps<{
    x: number;
    y: number;
    width: number;
    height: number;
}>();

const emit = defineEmits<{
    (e: "change", property: DimensionsProperty, value: number): void
}>();

const hovered = ref(false);

function handleKeyPress(e: KeyboardEvent) {
    e.preventDefault();
    
    let distance = 10;
    if (e.shiftKey) {
        distance = -10;
    }

    switch (e.key.toLowerCase()) {
    case "w": emit("change", "y", props.y - distance); break;
    case "a": emit("change", "x", props.x - distance); break;
    case "s": emit("change", "y", props.y + distance); break;
    case "d": emit("change", "x", props.x + distance); break;

    case "i":
        if (props.height > distance) {
            emit("change", "y", props.y - distance);
            emit("change", "height", props.height + distance);
        }
        break;
    case "j":
        if (props.width > distance) {
            emit("change", "x", props.x - distance);
            emit("change", "width", props.width + distance);
        }
        break;
    case "k": emit("change", "height", Math.max(10, props.height + distance)); break;
    case "l": emit("change", "width", Math.max(10, props.width + distance)); break;
    }
}

function mouseOver() {
    hovered.value = true;
    document.body.addEventListener("keypress", handleKeyPress);
}

function mouseLeave() {
    hovered.value = false;
    document.body.removeEventListener("keypress", handleKeyPress);
}

onUnmounted(() => {
    document.body.removeEventListener("keypress", handleKeyPress);
});

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
        :class="hovered ? 'hover' : null"
        @mouseover="mouseOver"
        @mouseout="mouseLeave"
    ></div>
</template>

<style scoped>
div {
    background-color: black;
    position: absolute;
}
.hover {
    background-color: gray;
}
</style>