<script setup lang="ts">
import PanZoom from "../PanZoom.vue";
</script>

<template>
    <div class="container-fluid">
        <div class="grid">
            <div class="panzoom">
                <PanZoom>
                    <slot name="panzoom" />
                </PanZoom>
            </div>
            <aside class="p-3 overflow-auto">
                <slot name="aside" />
            </aside>
        </div>
    </div>
</template>

<style scoped>
.panzoom {
    overflow: hidden;
    border: 2px solid #ddd;
    height: calc(100vh - 150px);
}
.grid {
    display: grid;
    grid-template-columns: 1fr auto;
    width: 100%;
}
</style>