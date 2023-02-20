<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
}>();

const hovered = ref(false);

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
        :class="hovered ? 'hover' : null"
        @mouseover="() => hovered = true"
        @mouseout="() => hovered = false"
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
</style>