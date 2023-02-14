<script setup lang="ts">

const props = defineProps<{
    x: number;
    y: number;
    width: number;
    height: number;
}>();

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;`"
    ></div>
</template>

<style scoped>
div {
    background-color: black;
    position: absolute;
    z-index: 1;
}
.hover {
    background-color: gray;
}
</style>