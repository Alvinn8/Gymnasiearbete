<script setup lang="ts">
import { onMounted, ref } from "vue";
import createPanZoom from "panzoom";
import { usePanzoom } from "@/stores/panzoom";

const panzoom = usePanzoom();
const div = ref<HTMLDivElement | null>(null);

onMounted(() => {
    panzoom.value = createPanZoom(div.value!);
});

</script>

<template>
    <div ref="div">
        <slot />
    </div>
</template>