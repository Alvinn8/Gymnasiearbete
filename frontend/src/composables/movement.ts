import { panzoomKey } from "@/components/keys";
import type { Position } from "@/types";
import { inject, onUnmounted, ref } from "vue";

export type UseMovementArguments = {
    /** An object containing the current position. */
    dimensions: Position;
    /** Called when a property changes. */
    onChange(property: keyof Position, value: number): void
    /** Called when the object is copied. */
    onCopy(): void;
};

/**
 * A Vue.js composeable for sharing movement logic between components.
 */
export default function useMovement({
    dimensions, onChange, onCopy
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
            newX = Math.floor(newX / 10) * 10;
            newY = Math.floor(newY / 10) * 10;
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
    
        let distance = 10;
        if (e.shiftKey) {
            distance = -10;
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
    }

    const hovered = ref(false);

    function mouseOver() {
        hovered.value = true;
        document.body.addEventListener("keypress", handleKeyPress);
    }

    function mouseLeave() {
        hovered.value = false;
        document.body.removeEventListener("keypress", handleKeyPress);
    }

    
    onUnmounted(() => {
        document.body.removeEventListener("keypress", handleKeyPress);
        document.body.removeEventListener("mousemove", mouseMove);
        document.body.removeEventListener("mouseup", mouseUp);
    });

    return {
        mousedown: mouseDown,
        mouseover: mouseOver,
        mouseout: mouseLeave,
        hovered
    };
}