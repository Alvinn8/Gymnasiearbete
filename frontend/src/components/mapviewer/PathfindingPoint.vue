<script setup lang="ts">

defineProps<{
    x: number;
    y: number;
    color?: string;
}>();

</script>

<template>
    <div :style="{
            left: x + 'px',
            top: y + 'px',
            backgroundColor: color
        }"
    ></div>
</template>

<style scoped>
div {
    background-color: #57bee1;
    position: absolute;
    z-index: 4;
    border-radius: 50%;
    border: 1px solid #5785e1;
    width: 10px;
    height: 10px;
    transform: translate(-5px, -5px);
}
div:hover {
    background-color: gray;
}
</style>