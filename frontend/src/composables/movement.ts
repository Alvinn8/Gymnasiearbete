import { panzoomKey } from "@/components/keys";
import type { SelectionWithId } from "@/stores/selection";
import type { Position } from "@/types";
import { inject, onUnmounted, watch, } from "vue";

export type UseMovementArguments = {
    /** An object containing the current position. */
    dimensions: Position;
    /** Called when a property changes. */
    onChange(property: keyof Position, value: number): void
    /** Called when the object is copied. */
    onCopy(): void;
    /** The selection to use. */
    selection: SelectionWithId;
    /** An object containing custom keybind logic. */
    customKeybinds?: {
        [key: string]: () => void;
    }
};

/**
 * A Vue.js composeable for sharing movement logic between components.
 */
export default function useMovement({
    dimensions, onChange, onCopy, customKeybinds, selection
}: UseMovementArguments) {

    // Drag to move

    const panzoom = inject(panzoomKey);

    const moveStart = {
        mouseX: 0,
        mouseY: 0,
        thisX: 0,
        thisY: 0
    };
    
    function mouseMove(e: MouseEvent) {
        if (!panzoom) return;
        const scale = panzoom.value.getTransform().scale;
        const diffX = (e.clientX - moveStart.mouseX) / scale;
        const diffY = (e.clientY - moveStart.mouseY) / scale;
        let newX = moveStart.thisX + diffX;
        let newY = moveStart.thisY + diffY;
        if (!e.shiftKey) {
            newX = Math.floor(newX / 1) * 1;
            newY = Math.floor(newY / 1) * 1;
        }
        onChange("x", newX);
        onChange("y", newY);
    }
    
    function mouseUp() {
        panzoom?.value.resume();
        document.body.removeEventListener("mousemove", mouseMove);
        document.body.removeEventListener("mouseup", mouseUp);
    }
    
    function mouseDown(e: MouseEvent) {
        e.preventDefault();
        panzoom?.value.pause();
        moveStart.mouseX = e.clientX;
        moveStart.mouseY = e.clientY;
        moveStart.thisX = dimensions.x;
        moveStart.thisY = dimensions.y;
        document.body.addEventListener("mousemove", mouseMove);
        document.body.addEventListener("mouseup", mouseUp);
    }

    // Keyboard shortcuts

    function handleKeyPress(e: KeyboardEvent) {
        e.preventDefault();
    
        let distance = 1;
        if (e.shiftKey) {
            distance = -distance;
        }

        switch (e.key.toLowerCase()) {
        // Moving the object
        case "w": onChange("y", dimensions.y - distance); break;
        case "a": onChange("x", dimensions.x - distance); break;
        case "s": onChange("y", dimensions.y + distance); break;
        case "d": onChange("x", dimensions.x + distance); break;

        // Copying the object
        case "c": onCopy(); break;
        }

        if (customKeybinds) {
            const handler = customKeybinds[e.key.toLowerCase()];
            if (handler) handler();
        }
    }

    watch(selection.selected, (newValue) => {
        if (newValue) {
            document.body.addEventListener("keypress", handleKeyPress);
        } else {
            document.body.removeEventListener("keypress", handleKeyPress);
        }
    });
    
    onUnmounted(() => {
        document.body.removeEventListener("keypress", handleKeyPress);
        document.body.removeEventListener("mousemove", mouseMove);
        document.body.removeEventListener("mouseup", mouseUp);
    });

    return {
        mousedown: mouseDown
    };
}