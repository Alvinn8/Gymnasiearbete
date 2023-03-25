export const useTap = (onTap: () => void) => {
    const touches: Touch[] = [];

    function touchStart(e: TouchEvent) {
        touches.push(...e.changedTouches);
    }

    function touchEnd(e: TouchEvent) {
        for (const touch of e.changedTouches) {
            const originalTouch = touches.find(t => t.identifier === touch.identifier);
            if (originalTouch) {
                const deltaX = Math.abs(originalTouch.clientX - touch.clientX);
                const deltaY = Math.abs(originalTouch.clientY - touch.clientY);
                if (deltaX < 10 && deltaY < 10) {
                    // The user tapped.
                    // Call the callback.
                    onTap();
                }
            }
        }
    }

    return {
        touchStart, touchEnd
    };
};