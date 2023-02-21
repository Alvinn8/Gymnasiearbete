// Locations

const LEFT_MODIFIER_KEYS = 1;
const RIGHT_MODIFIER_KEYS = 2;

// Keys
type Key = (e: KeyboardEvent) => boolean;

const allKeys: Key[] = [];

function key(func: Key) {
    allKeys.push(func);
    return func;
}

const LEFT_SHIFT = key((e) => e.key === "Shift" && e.location === LEFT_MODIFIER_KEYS);
const RIGHT_SHIFT = key((e) => e.key === "Shift" && e.location === RIGHT_MODIFIER_KEYS);

// Implementation

const pressedKeys: Set<Key> = new Set();

export function registerKeyboardListeners() {
    window.addEventListener("keydown", (e) => {
        for (const key of allKeys) {
            // If the key is being pressed...
            if (key(e)) {
                // Add it to the set of keys being pressed.
                pressedKeys.add(key);
            }
        }
    });

    window.addEventListener("keyup", (e) => {
        for (const key of allKeys) {
            // If the key is being released...
            if (key(e)) {
                // Remove it from the set of keys being pressed.
                pressedKeys.delete(key);
            }
        }
    });
}

// Provide the data

export namespace pressing {
    export const leftShift = () => pressedKeys.has(LEFT_SHIFT);
    export const rightShift = () => pressedKeys.has(RIGHT_SHIFT);
}

