<script setup lang="ts">
import { ref, reactive } from "vue";

const pos = reactive({
    x: 0,
    y: 0
});
const size = reactive({
    width: 10,
    height: 100
});
const hovered = ref(false);

function mouseOver(e: MouseEvent) {
    hovered.value = true;
}

function mouseLeave(e: MouseEvent) {
    hovered.value = false;
}

</script>

<template>
    <div :style="`left: ${pos.x}px;
                  top: ${pos.y}px;
                  width: ${size.width}px;
                  height: ${size.height}px;`"
        :class="hovered ? 'hover' : null"
        @mouseover="mouseOver"
        @mouseout="mouseLeave"
    ></div>
</template>

<style scoped>
div {
    background-color: black;
}
.hover {
    background-color: gray;
}
</style>