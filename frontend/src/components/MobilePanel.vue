<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

const props = defineProps<{
    sticky: boolean
    visible: boolean;
}>();

const height = ref(10);
const currentDragPosition = ref<number | null>(null);

/**
 * Get the y position from a touch event or a mouse event.
 * 
 * @param e The event.
 * @returns The y coordinate.
 */
function getPosition(e: TouchEvent | MouseEvent) {
    if ("touches" in e) {
        // The even is a TouchEvent. Grab the position from the touch object.
        const touch = e.touches[0];
        return touch.clientY;
    }
    // Otherwise, it is a MouseEvent. Grab the mouse position.
    return e.clientY;
}

function dragStart(e: TouchEvent | MouseEvent) {
    e.preventDefault();
    currentDragPosition.value = getPosition(e);
}

function dragMove(e: TouchEvent | MouseEvent) {
    if (!currentDragPosition.value) return;
    e.preventDefault();
    const newPosition = getPosition(e);
    const difference = currentDragPosition.value - newPosition;
    height.value += difference / window.innerHeight * 100;
    currentDragPosition.value = newPosition;
}

function dragEnd() {
    if (!currentDragPosition.value) return;
    currentDragPosition.value = null;
    if (height.value > 75) {
        height.value = 100;
    }
    if (height.value < 25) {
        if (props.sticky) {
            height.value = 10;
        } else {
            height.value = 0;
        }
    }
}

function click() {
    height.value = 50;
}

onMounted(() => {
    window.addEventListener("touchmove", dragMove);
    window.addEventListener("mousemove", dragMove);
    
    window.addEventListener("touchend", dragEnd);
    window.addEventListener("mouseup", dragEnd);
});

onUnmounted(() => {
    window.removeEventListener("touchmove", dragMove);
    window.removeEventListener("mousemove", dragMove);
    
    window.removeEventListener("touchend", dragEnd);
    window.removeEventListener("mouseup", dragEnd);
});

</script>

<template>
    <div
        class="mobile-panel"
        :class="{ transition: currentDragPosition === null, fullscreen: height === 100 }"
        :style="`height: ${height}vh;`"
    >
        <div class="handle-container"
            @touchstart="dragStart"
            @mousedown="dragStart"
            @click="click"
        >
            <div class="handle"></div>
        </div>
        <div class="body">
            <slot />
        </div>
    </div>
</template>

<style scoped>
.mobile-panel {
    bottom: 0px;
    background-color: white;
    box-shadow: 0px -1px 5px 0px;
    width: 100%;
    border-top-right-radius: 5px;
    border-top-left-radius: 5px;
}
.transition {
    transition: height 250ms;
}
.fullscreen {
    border-radius: 0px;
    padding-top: 50px;
}
.handle-container {
    width: 100%;
    display: inline-block;
    padding: 10px 0px;
}
.handle {
    width: 50px;
    height: 4px;
    border-radius: 5px;
    background-color: #ddd;
    margin: 5px auto;
}
</style>