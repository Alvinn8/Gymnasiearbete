<script setup lang="ts">
import { onMounted, provide, ref } from "vue";
import type { PanZoom } from "panzoom";
import createPanZoom from "panzoom";
import { panzoomKey } from "./keys";

const panzoom = ref<PanZoom | null>(null);
const div = ref<HTMLDivElement | null>(null);

onMounted(() => {
    panzoom.value = createPanZoom(div.value!);
    // @ts-ignore
    window.panzoom = panzoom.value;
});

provide(panzoomKey, panzoom);
</script>

<template>
    <div ref="div">
        <slot />
    </div>
</template>