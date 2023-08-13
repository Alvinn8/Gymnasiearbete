<script setup lang="ts">
import { apiPost, errorHandler, handleError } from "@/api/api";
import useMovement from "@/composables/movement";
import { useKeybindInfo } from "@/stores/keybindsInfo";
import { useSelection } from "@/stores/selection";
import type { Point, Room } from "@/types";
import Swal from "sweetalert2";
import { inject, toRef, watch } from "vue";
import { useRoute } from "vue-router";
import { mapPartIdKey } from "../keys";


const props = defineProps<{
    id: number;
    x: number;
    y: number;
    isCrossMapPart: boolean;
    isRoomPoint: boolean;
}>();

const emit = defineEmits<{
    /**
     * Called when the point position changes.
     */
    (e: "change", property: "x" | "y", value: number): void;
    
    /**
     * Called when the user presses a key to copy the point.
     */
    (e: "copy", point: Point): void;

    /**
     * Called when the point is deleted.
     */
    (e: "delete"): void;

    /** Called when the point is clicked. */
    (e: "click"): void;

    /** Called when the point is right clicked. */
    (e: "right-click", ev: MouseEvent): void;

    /** Called when a new room has been created for this point. */
    (e: "new-room", room: Room): void;

    /** Called when connections are removed from the point.  */
    (e: "remove-connections", pointConnectionIds: number[]): void;

    /** Called when a new connection was formed due to an extrude operation.  */
    (e: "new-connection", connectionId: number, pointAId: number, pointBId: number): void;
}>();

const selection = useSelection("point", toRef(props, "id"));
const pointSelection = useSelection("point");
const keybindInfo = useKeybindInfo();

const movement = useMovement({
    dimensions: props,
    selection: selection,
    onChange: (property, value) => emit("change", property, value),
    onCopy: () => copyPoint(),
    onDelete: () => deletePoint(),
    customKeybinds: {
        "r": async () => {
            selection.deselect();
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
            const roomId = res.value.id as number;
            let roomName = res.value.name as string | null;
            if (roomName && roomName.length === 0) roomName = null;
            emit("new-room", {
                id: roomId,
                name: roomName,
                x: props.x - 10,
                y: props.y - 10,
                width: 20,
                height: 20,
                doorAtPointId: props.id
            });
            const roomSelection = useSelection("room");
            roomSelection.select(roomId);
        },
        "x": async () => {
            const res = await apiPost(`map/${route.params.map_id}/point_connection/remove_all_from_point`, { pointId: props.id });
            emit("remove-connections", res.ids.map((obj: { id: number }) => obj.id));
        },
        "e": () => extrudePoint()
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

    pointSelection.select(point.id);
}

async function extrudePoint() {
    const pointRes = await apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/point/new`, {})
        .catch(handleError);
    
    if (!pointRes) return;
    
    const point = {
        id: pointRes.id,
        x: props.x + 20,
        y: props.y + 20
    };

    const pointConnectionRes = await apiPost(`map/${route.params.map_id}/point_connection/new`, {
        point_a_id: props.id,
        point_b_id: point.id
    });

    const connectionId = pointConnectionRes.id;

    emit("copy", point);
    emit("new-connection", connectionId, props.id, point.id);

    pointSelection.select(point.id);
}

function deletePoint() {
    return apiPost(`map/${route.params.map_id}/part/${mapPartId!.value}/point/delete`, {
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

watch(selection.selected, (selected) => {
    if (selected) {
        keybindInfo.groups = [
            movement.description,
            keybindInfo.faster,
            keybindInfo.copy,
            {
                id: "new_room",
                description: "Skapa nytt rum",
                keys: ["r"]
            },
            {
                id: "remove_connections",
                description: "Ta bort anslutningar",
                keys: ["x"]
            },
            {
                id: "extrude",
                description: "Utvidga väg",
                keys: ["e"]
            },
            {
                id: "delete_point",
                description: "Radera punkt",
                keys: ["Backspace", "Delete"]
            }
        ];
    }
});

</script>

<template>
    <div :style="`left: ${x}px;
                  top: ${y}px;`"
        :class="{
            hover: selection.selected.value,
            crossMapPart: isCrossMapPart,
            roomPoint: isRoomPoint
        }"
        @mousedown="(e) => { movement.mousedown(e); selection.select() }"
        @click="emit('click')"
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
    --cross-map-part-color: #be5757;
    --room-point-color: #57be57;
}
.crossMapPart, .roomPoint {
    border-style: dashed;
}
.crossMapPart {
    background-color:  var(--cross-map-part-color);
}
.roomPoint {
    background-color:  var(--room-point-color);
}
.crossMapPart.roomPoint {
    background-image:
        linear-gradient(-45deg, var(--cross-map-part-color), var(--cross-map-part-color), var(--room-point-color), var(--room-point-color));
}
.hover {
    background-color: gray;
}
</style>