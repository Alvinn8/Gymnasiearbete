import { defineStore } from "pinia";
import { computed, onMounted, ref } from "vue";

export type ViewMode = "normal" | "transparent" | "background";

export const useViewMode = defineStore("view_mode", () => {
    const mode = ref<ViewMode>("normal");
    const opacity = computed(() => {
        switch (mode.value) {
        default: return 1;
        case "transparent": return 0.25;
        case "background": return 0;
        }
    });

    function keyDown(e: KeyboardEvent) {
        if (e.key === "z") {
            toggleMode();
            e.preventDefault();
        }
    }

    onMounted(() => window.addEventListener("keydown", keyDown));

    function setMode(newMode: ViewMode) {
        mode.value = newMode;
    }

    function toggleMode() {
        switch (mode.value) {
        case "normal": mode.value = "transparent"; break;
        case "transparent": mode.value = "background"; break;
        default: mode.value = "normal"; break;
        }
    }

    return {
        mode, opacity, setMode, toggleMode
    };
});