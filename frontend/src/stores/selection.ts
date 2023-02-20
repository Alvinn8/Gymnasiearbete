import { defineStore } from "pinia";
import { ref } from "vue";

export type SelectionType = "point" | "wall" | "room";

export interface Selection {
    type: SelectionType;
    id: number;
}

export const useSelection = defineStore("selection", () => {
    const selection = ref<Selection | null>(null);

    const select = (id: number, type: SelectionType) => selection.value = { type, id };
    const selectPoint = (id: number) => select(id, "point");
    const selectWall = (id: number) => select(id, "wall");
    const selectRoom = (id: number) => select(id, "room");
    const deselect = () => selection.value = null;

    return { selection, selectPoint, selectWall, selectRoom, deselect };
});