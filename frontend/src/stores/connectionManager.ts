import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useConnectionManager = defineStore("cross_part_connection", () => {
    const pointId = ref<number | null>(null);
    // TODO

    const isConnecting = computed(() => pointId.value !== null);

    function select(id: number) {
        pointId.value = id;
    }

    return {
        pointId,
        isConnecting,
        select
    };
});