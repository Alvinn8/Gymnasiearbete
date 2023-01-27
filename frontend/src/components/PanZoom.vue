<script setup lang="ts">
import { onMounted, ref } from "vue";
import panzoom from "panzoom";

const div = ref<HTMLDivElement | null>(null);

onMounted(() => {
    panzoom(div.value!);
});
</script>

<template>
    <div ref="div">
        <slot />
    </div>
</template>