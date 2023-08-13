<script setup lang="ts">
import { useMovementAndResize } from "@/composables/resize";
import { useKeybindInfo } from "@/stores/keybindsInfo";
import { useSelection } from "@/stores/selection";
import { useViewMode } from "@/stores/viewMode";
import type { Position, Room } from "@/types";
import { inject, toRef, watch } from "vue";
import PointConnection from "./PointConnection.vue";
import Swal from "sweetalert2";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";
import { apiPost, errorHandler } from "@/api/api";

const props = defineProps<{
    id: number;
    name: string | null;
    x: number;
    y: number;
    width: number;
    height: number;
    point: Position;
    hasCategory: boolean;
}>();

const emit = defineEmits<{
    /**
     * Called when the room object changes.
     */
    <T extends keyof Room>(e: "change", property: T, value: Room[T]): void;
    /**
     * Called when the user wishes to change the category of the room.
     */
    (e: "change-category"): void;
    /**
     * Called when the room is deleted.
     */
    (e: "delete"): void;
}>();

const selection = useSelection("room", toRef(props, "id"));
const viewMode = useViewMode();
const keybindInfo = useKeybindInfo();
const route = useRoute();
const mapPartId = inject(mapPartIdKey);

const movement = useMovementAndResize({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => {},
    onDelete: deleteRoom,
    customKeybinds: {
        "r": rename,
        "q": () => emit("change-category")
    }
});

watch(selection.selected, (selected) => {
    if (selected) {
        keybindInfo.groups = [
            ...movement.description,
            keybindInfo.invert,
            keybindInfo.faster,
            keybindInfo.copy,
            {
                id: "rename_rool",
                description: "Ändra namn",
                keys: ["r"]
            },
            {
                id: "change_category",
                description: "Ändra rumkategori",
                keys: ["q"]
            },
            {
                id: "delete_room",
                description: "Radera rum",
                keys: ["Backspace", "Delete"]
            }
        ];
    }
});

async function rename() {
    selection.deselect();
    const result = await Swal.fire({
        title: "Ändra namn",
        text: "Skriv det nya namnet på rummet",
        input: "text",
        inputValue: props.name ?? "",
        showCancelButton: true
    });
    const name = result.value as string;
    if (name) {
        emit("change", "name", name);
    }
}

async function deleteRoom() {
    return apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/room/delete`, {
        id: props.id
    }).then(() => {
        selection.deselect();
        emit("delete");
    }).catch(errorHandler([
        [json => !json.success, (json: any) => Swal.fire({
            icon: "error",
            title: json.error
        })]
    ]));
}

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;
                  width: ${width}px;
                  height: ${height}px;
                  opacity: ${viewMode.opacity};`"
        :class="{
            hover: selection.selected.value,
            missingCategory: !hasCategory
        }"
        @mousedown="(e) => { movement.mousedown(e); selection.select() }"
    >
        <span v-if="name">{{ name }}</span>
    </div>
    <PointConnection
        v-if="selection.selected.value"
        :point_a="{ x: x + width / 2, y: y + height / 2 }"
        :point_b="point"
    />
</template>

<style scoped>
div {
    background-color: rgba(0, 0, 0, 0.15);
    position: absolute;
    z-index: 2;
    
    /* center text */
    display: flex;
    justify-content: center;
    align-items: center;
}
span {
    background: rgb(0, 0, 0, 0.5);
    color: white;
    padding: 3px;
    border-radius: 5px;
    font-size: 12px;
}
.hover {
    background-color: rgba(0, 0, 0, 0.3);
}
.hover span {
    background: rgb(0, 0, 0, 0.05);
    text-emphasis-color: rgb(0, 0, 0, 0.25);
}
.missingCategory {
    background-color: rgba(255, 0, 0, 0.15);
}
</style>