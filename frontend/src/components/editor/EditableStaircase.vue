<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import { useMovementAndResize } from "@/composables/resize";
import { useKeybindInfo } from "@/stores/keybindsInfo";
import { useSelection } from "@/stores/selection";
import { useViewMode } from "@/stores/viewMode";
import type { Staircase } from "@/types";
import { inject, toRef, watch } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";

const props = defineProps<{
    id: number;
    x: number;
    y: number;
    width: number;
    height: number;
    rotationDeg: number;
    hasConnection: boolean;
}>();

const emit = defineEmits<{
    /**
     * Called when the staircase dimensions change.
     */
    (e: "change", property: keyof Staircase, value: number): void;

    /**
     * Called when the staircase is copied.
     */
    (e: "copy", staircase: Staircase): void;

    /**
     * Called when two staircases are connected.
     */
    (e: "connect", idA: number, idB: number): void;
}>();

const selection = useSelection("staircase", toRef(props, "id"));
const staircaseSelection = useSelection("staircase");
const viewMode = useViewMode();
const keybindInfo = useKeybindInfo();
const mapPartId = inject(mapPartIdKey);
const route = useRoute();

const movement = useMovementAndResize({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => copyStaircase(),
    customKeybinds: {
        "r": () => {
            const newRotation = (props.rotationDeg + 90) % 360;
            emit("change", "rotationDeg", newRotation);
        }
    }
});

async function copyStaircase() {
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/staircase/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const staircase: Staircase = {
        id: res.id,
        mapPartId: mapPartId!.value,
        x: props.x + 20,
        y: props.y + 20,
        width: props.width,
        height: props.height,
        connectsTo: null,
        rotationDeg: 0
    };

    emit("copy", staircase);

    staircaseSelection.select(staircase.id);
}
watch(selection.selected, (selected) => {
    if (selected) {
        keybindInfo.groups = [
            ...movement.description,
            keybindInfo.invert,
            keybindInfo.faster,
            {
                id: "rotate",
                keys: ["r"],
                description: "Rotera"
            }
        ];
    }
});

function mouseDown(e: MouseEvent) {
    movement.mousedown(e);
    if (typeof staircaseSelection.selected.value === "number" && staircaseSelection.selected.value !== props.id) {
        // A different staircase was selected and this one was clicked. We need to connect the two.
        emit("connect", staircaseSelection.selected.value, props.id);
        staircaseSelection.deselect();
        return;
    }
    selection.select();
}

</script>

<template>
    <div :style="{
            left: x + 'px',
            top: y + 'px',
            width: width + 'px',
            height: height + 'px',
            opacity: viewMode.opacity
        }"
        :class="{
            selected: selection.selected.value,
            noConnection: !hasConnection,
            ['rotate' + rotationDeg]: true
        }"
        @mousedown="mouseDown"
    >
    </div>
</template>

<style scoped>
div {
    --rotation-deg: 0deg;
    /** Repeating lines */
    background: repeating-linear-gradient(var(--rotation-deg), white, white 4px, black 4px, black 6px);
    position: absolute;
    z-index: 2;
    border: 1px solid black;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}
.rotate0 {
    border-bottom-width: 0;
    border-top-width: 2px;
    --rotation-deg: 0deg;
}
.rotate90 {
    border-right-width: 0;
    border-left-width: 2px;
    --rotation-deg: 90deg;
}
.rotate180 {
    border-top-width: 0;
    border-bottom-width: 2px;
    --rotation-deg: 180deg;
}
.rotate270 {
    border-left-width: 0;
    border-right-width: 2px;
    --rotation-deg: 270deg;
}
.noConnection {
    border-color: red;
}
.selected {
    background-color: rgba(128, 128, 128, 0.2);
}
span {
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 5px;
}
</style>