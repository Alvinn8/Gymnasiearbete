<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import type { DimensionsProperty, Wall } from "@/types";
import { inject, onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey, panzoomKey } from "../keys";

const props = defineProps<{
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

const hovered = ref(false);

function handleKeyPress(e: KeyboardEvent) {
    e.preventDefault();
    
    let distance = 10;
    if (e.shiftKey) {
        distance = -10;
    }

    switch (e.key.toLowerCase()) {
    // Moving the wall
    case "w": emit("change", "y", props.y - distance); break;
    case "a": emit("change", "x", props.x - distance); break;
    case "s": emit("change", "y", props.y + distance); break;
    case "d": emit("change", "x", props.x + distance); break;

    // Resizing the wall
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

    // Copying the wall
    case "c": copyWall(); break;
    }
}

async function copyWall() {
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId?.value}/wall/new`, {})
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

const panzoom = inject(panzoomKey);

function mouseOver() {
    hovered.value = true;
    document.body.addEventListener("keypress", handleKeyPress);
}

function mouseLeave() {
    hovered.value = false;
    document.body.removeEventListener("keypress", handleKeyPress);
}

const moveStart = {
    mouseX: 0,
    mouseY: 0,
    wallX: 0,
    wallY: 0
};

function mouseMove(e: MouseEvent) {
    if (!panzoom) return;
    const scale = panzoom.value.getTransform().scale;
    const diffX = (e.clientX - moveStart.mouseX) / scale;
    const diffY = (e.clientY - moveStart.mouseY) / scale;
    let newX = moveStart.wallX + diffX;
    let newY = moveStart.wallY + diffY;
    if (!e.shiftKey) {
        newX = Math.floor(newX / 10) * 10;
        newY = Math.floor(newY / 10) * 10;
    }
    emit("change", "x", newX);
    emit("change", "y", newY);
}

function mouseUp() {
    console.log("up");
    panzoom?.value.resume();
    document.body.removeEventListener("mousemove", mouseMove);
    document.body.removeEventListener("mouseup", mouseUp);
}

function mouseDown(e: MouseEvent) {
    e.preventDefault();
    panzoom?.value.pause();
    moveStart.mouseX = e.clientX;
    moveStart.mouseY = e.clientY;
    moveStart.wallX = props.x;
    moveStart.wallY = props.y;
    document.body.addEventListener("mousemove", mouseMove);
    document.body.addEventListener("mouseup", mouseUp);
}

onUnmounted(() => {
    document.body.removeEventListener("keypress", handleKeyPress);
    document.body.removeEventListener("mousemove", mouseMove);
    document.body.removeEventListener("mouseup", mouseUp);
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
        @mousedown="mouseDown"
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