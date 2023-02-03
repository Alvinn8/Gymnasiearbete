<script setup lang="ts">
import { onUnmounted, ref } from "vue";
const props = defineProps<{
    x: number;
    y: number;
    width: number;
    height: number;
    onChange?: (property: "x" | "y" | "width" | "height", value: number) => void;
}>();

const hovered = ref(false);

function handleKeyPress(e: KeyboardEvent) {
    if (!props.onChange) return;
    e.preventDefault();
    
    let distance = 10;
    if (e.shiftKey) {
        distance = -10;
    }

    switch (e.key.toLowerCase()) {
    case "w": props.onChange("y", props.y - distance); break;
    case "a": props.onChange("x", props.x - distance); break;
    case "s": props.onChange("y", props.y + distance); break;
    case "d": props.onChange("x", props.x + distance); break;

    case "i":
        if (props.height > distance) {
            props.onChange("y", props.y - distance);
            props.onChange("height", props.height + distance);
        }
        break;
    case "j":
        if (props.width > distance) {
            props.onChange("x", props.x - distance);
            props.onChange("width", props.width + distance);
        }
        break;
    case "k": props.onChange("height", Math.max(10, props.height + distance)); break;
    case "l": props.onChange("width", Math.max(10, props.width + distance)); break;
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