import { defineStore } from "pinia";
import { ref } from "vue";

const faster: Readonly<KeybindGroup> = Object.freeze({
    id: "faster",
    description: "Snabbare",
    keys: ["Höger Shift"]
});

const invert: Readonly<KeybindGroup> = Object.freeze({
    id: "invert",
    description: "Invertera",
    keys: ["Vänster Shift"]
});

const copy: Readonly<KeybindGroup> = Object.freeze({
    id: "copy",
    description: "Kopiera",
    keys: ["c"]
});
export type KeybindGroup = {
    id: string;
    description: string;
    keys: string[];
}

export const useKeybindInfo = defineStore("keybind_info", () => {
    const groups = ref<KeybindGroup[] | null>(null);

    return {
        groups,
        faster,
        invert,
        copy
    };
});