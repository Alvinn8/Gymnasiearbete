import { defineStore } from "pinia";
import { computed, ref } from "vue";

export type SelectionType = "point" | "wall" | "room";

export interface Selection {
    type: SelectionType;
    id: number;
}

const useSelectionStore = defineStore("selection", () => {
    const selection = ref<Selection | null>(null);

    const select = (id: number, type: SelectionType) => selection.value = { type, id };
    const deselect = () => selection.value = null;

    return { selection, select, deselect };
});

export const useSelection = (type: SelectionType) => {
    const selection = useSelectionStore();

    return {
        // Get the currently selected id if the current selection is of this type.
        selected: computed(() =>
            (selection.selection === null || selection.selection.type !== type)
                ? null : selection.selection.id),
        deselect: selection.deselect,
        select: (id: number) => selection.select(id, type)
    };

};