import { FAST_MOVEMENT_MULTIPLIER, MOVEMENT_GRID_DISTANCE } from "@/constants";
import { pressing } from "@/keyboard";
import type { KeybindGroup } from "@/stores/keybindsInfo";
import type { SelectionWithId } from "@/stores/selection";
import type { Dimensions } from "@/types";
import { onUnmounted, watch } from "vue";
import type { UseMovementArguments } from "./movement";
import useMovement from "./movement";

const description: Readonly<KeybindGroup> = Object.freeze({
    id: "resize",
    description: "Ändra storlek",
    keys: ["i", "j", "k", "l"]
});

export type UseResizeArguments = {
    /** An object containing the current dimensions. */
    dimensions: Dimensions;
    /** The selection. */
    selection: SelectionWithId;
    /** Called when a property changes. */
    onChange(property: keyof Dimensions, value: number): void
};

/**
 * A Vue.js composeable for sharing resizing logic between components.
 */
export default function useResize({
    dimensions, onChange, selection
}: UseResizeArguments) {

    // Keyboard shortcuts

    function handleKeyDown(e: KeyboardEvent) {
        e.preventDefault();
    
        let distance = MOVEMENT_GRID_DISTANCE;
        if (pressing.leftShift()) {
            distance = -distance;
        }
        if (pressing.rightShift()) {
            distance *= FAST_MOVEMENT_MULTIPLIER;
        }

        switch (e.key.toLowerCase()) {

        // Resizing the object
        case "i": {
            if (dimensions.height + distance > 0) {
                onChange("y", dimensions.y - distance);
                onChange("height", dimensions.height + distance);
            }
            break;
        }
        case "j": {
            if (dimensions.width + distance > 0) {
                onChange("x", dimensions.x - distance);
                onChange("width", dimensions.width + distance);
            }
            break;
        }
        case "k": onChange("height", Math.max(1, dimensions.height + distance)); break;
        case "l": onChange("width", Math.max(1, dimensions.width + distance)); break;

        }
    }

    watch(selection.selected, (newValue) => {
        if (newValue) {
            document.body.addEventListener("keydown", handleKeyDown);
        } else {
            document.body.removeEventListener("keydown", handleKeyDown);
        }
    }, { immediate: true });

    onUnmounted(() => {
        document.body.removeEventListener("keydown", handleKeyDown);
    });

    return {
        description
    };
}

/**
 * Use both {@link useMovement} and {@link useResize}.
 */
export function useMovementAndResize(options: UseMovementArguments & UseResizeArguments) {
    const movement = useMovement(options);
    const resize = useResize(options);

    return {
        mousedown: movement.mousedown,
        description: [
            movement.description,
            resize.description
        ]
    };
}