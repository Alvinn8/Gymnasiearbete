import type { Dimensions } from "@/types";
import { onUnmounted } from "vue";
import type { UseMovementArguments } from "./movement";
import useMovement from "./movement";

export type UseResizeArguments = {
    /** An object containing the current dimensions. */
    dimensions: Dimensions;
    /** Called when a property changes. */
    onChange(property: keyof Dimensions, value: number): void
};

/**
 * A Vue.js composeable for sharing resizing logic between components.
 */
export default function useResize({
    dimensions, onChange
}: UseResizeArguments) {

    // Keyboard shortcuts

    function handleKeyPress(e: KeyboardEvent) {
        e.preventDefault();
    
        let distance = 10;
        if (e.shiftKey) {
            distance = -10;
        }

        switch (e.key.toLowerCase()) {

        // Resizing the object
        case "i": {
            if (dimensions.height > distance) {
                onChange("y", dimensions.y - distance);
                onChange("height", dimensions.height + distance);
            }
            break;
        }
        case "j": {
            if (dimensions.width > distance) {
                onChange("x", dimensions.x - distance);
                onChange("width", dimensions.width + distance);
            }
            break;
        }
        case "k": onChange("height", Math.max(10, dimensions.height + distance)); break;
        case "l": onChange("width", Math.max(10, dimensions.width + distance)); break;

        }
    }

    function mouseOver() {
        document.body.addEventListener("keypress", handleKeyPress);
    }

    function mouseLeave() {
        document.body.removeEventListener("keypress", handleKeyPress);
    }

    onUnmounted(() => {
        document.body.removeEventListener("keypress", handleKeyPress);
    });

    return {
        mouseover: mouseOver,
        mouseout: mouseLeave
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
        hovered: movement.hovered,
        // Merge the event listeners
        mouseover: () => { movement.mouseover(); resize.mouseover(); },
        mouseout: () => { movement.mouseout(); resize.mouseout(); }
    };
}