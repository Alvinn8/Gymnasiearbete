import { defineStore } from "pinia";
import { ref } from "vue";

export const useHighlightedRoomCategory = defineStore("highlighted_room_category", () => {
    const roomCategoryId = ref<number | null>(null);

    return {
        roomCategoryId
    };
});