import { defineStore } from "pinia";
import { computed, ref, type ComputedRef, type Ref } from "vue";

export type SelectionType = "point" | "wall" | "room";

export interface SelectionRef {
    type: SelectionType;
    id: number;
}

const useSelectionStore = defineStore("selection", () => {
    const selection = ref<SelectionRef | null>(null);

    const select = (id: number, type: SelectionType) => selection.value = { type, id };
    const deselect = () => selection.value = null;

    return { selection, select, deselect };
});

export interface GenericSelection {
    deselect(): void;
    select(id: number): void;
    selected: ComputedRef<number>;
}

export interface SelectionWithId {
    deselect(): void;
    select(): void;
    selected: ComputedRef<boolean>;
}

export function useSelection(type: SelectionType): GenericSelection;
export function useSelection(type: SelectionType, id: Ref<number>): SelectionWithId;
export function useSelection(type: SelectionType, id?: Ref<number>) {
    const selection = useSelectionStore();

    if (id) {
        return {
            deselect: selection.deselect,
            select: () => selection.select(id.value, type),
            selected: computed(() => selection.selection !== null
            && selection.selection.type === type
            && selection.selection.id === id.value)
        } as SelectionWithId;
    } else {
        return {
            deselect: selection.deselect,
            select: (id: number) => selection.select(id, type),
            // Get the currently selected id if the current selection is of this type.
            selected: computed(() =>
                (selection.selection === null || selection.selection.type !== type)
                    ? null : selection.selection.id)
        } as GenericSelection;
    }

}