import type { PanZoom } from "panzoom";
import { defineStore } from "pinia";
import { ref } from "vue";

export const usePanzoom = defineStore("panzoom", () => {
    const value = ref<PanZoom | null>(null);

    return {
        value
    };
});