<script setup lang="ts">
import { apiPost, handleError } from "@/api/api";
import useMovement from "@/composables/movement";
import { useSelection } from "@/stores/selection";
import type { Point, Room } from "@/types";
import Swal from "sweetalert2";
import { inject, toRef } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";


const props = defineProps<{
    id: number;
    x: number;
    y: number;
}>();

const emit = defineEmits<{
    /**
     * Called when the point position changes.
     */
    (e: "change", property: "x" | "y", value: number): void;
    
    /**
     * Called when the user presses a key to copy the point.
     */
    (e: "copy", wall: Point): void;

    /** Called when the point is clicked. */
    (e: "click"): void;

    /** Called when the point is right clicked. */
    (e: "right-click", ev: MouseEvent): void;

    /** Called when a new room has been created for this point. */
    (e: "new-room", room: Room): void;
}>();

const selection = useSelection("point", toRef(props, "id"));

const movement = useMovement({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => copyPoint(),
    customKeybinds: {
        "r": async () => {
            const res = await Swal.fire({
                title: "Skapa nytt rum",
                text: "Namnge rummet",
                input: "text",
                showCancelButton: true,
                showLoaderOnConfirm: true,
                preConfirm: async (name) => {
                    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/room/new`, {
                        name: name,
                        doorAtPointId: props.id
                    }).catch(handleError);
                    return {
                        id: res.id,
                        name: name
                    };
                },
                allowOutsideClick: () => !Swal.isLoading()
            });
            if (!res.value) return;
            emit("new-room", {
                id: res.value.id,
                name: res.value.name,
                x: props.x - 10,
                y: props.y - 10,
                width: 20,
                height: 20
            });
        }
    }
});

const route = useRoute();
const mapPartId = inject(mapPartIdKey);

async function copyPoint() {
    const res = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/point/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const point = {
        id: res.id,
        x: props.x + 20,
        y: props.y + 20
    };

    emit("copy", point);
}

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;`"
        :class="selection.selected.value ? 'hover' : null"
        @mouseover="movement.mouseover"
        @mouseout="movement.mouseout"
        @mousedown="movement.mousedown"
        @click="() => { emit('click'); selection.select() }"
        @contextmenu.prevent="(e) => emit('right-click', e)"
    ></div>
</template>

<style scoped>
div {
    background-color: #57bee1;
    position: absolute;
    z-index: 4;
    border-radius: 50%;
    border: 1px solid #5785e1;
    width: 10px;
    height: 10px;
    transform: translate(-5px, -5px);
}
.hover {
    background-color: gray;
}
</style>