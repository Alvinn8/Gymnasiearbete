import { apiPost } from "@/api/api";
import type { Point, PointConnection, Position } from "@/types";
import { defineStore } from "pinia";
import Swal from "sweetalert2";
import { onUnmounted, ref } from "vue";
import { useRoute } from "vue-router";
import { usePanzoom } from "./panzoom";

const useConnectionManagerStore = defineStore("connection_manager", () => {
    
    // The point where a connection is currently being formed from.
    const selectedPoint = ref<{
        point: Point;
        mapPartId: number;
    } | null>(null);

    const mousePosition = ref<Position | null>(null);
    const route = useRoute();
    const panzoom = usePanzoom();
    
    const moveStart = {
        mouseX: 0,
        mouseY: 0,
        thisX: 0,
        thisY: 0
    };

    const newConnectionListeners: ((connection: PointConnection) => void)[] = [];

    async function formNewConnection(pointB: Point, mapPartId: number) {
        document.body.removeEventListener("mousemove", mouseMove);
        const pointA = selectedPoint.value!.point;
        const isCrossMapPart = selectedPoint.value!.mapPartId !== mapPartId;
        mousePosition.value = null;
        selectedPoint.value = null;
        if (pointA === pointB) return;
        const res = await apiPost(`map/${route.params.map_id}/point_connection/new`, {
            point_a_id: pointA.id,
            point_b_id: pointB.id
        });
        const connectionId = res.id;
        const connection: PointConnection = {
            id: connectionId,
            point_a: pointA,
            point_b: pointB
        };
        if (isCrossMapPart) {
            Swal.fire({
                icon: "success",
                title: "En anslutning mellan kartdelar har skapats.",
                text: "En anslutning mellan två punkter som befinner sig på olika kartdelar "+
                "har skapats, och navegering mellan dessa kartdelar är nu möjligt."
            });
        } else {
            newConnectionListeners.forEach(func => func(connection));
        }
    }

    
    function clickPoint(point: Point, mapPartId: number) {
        if (selectedPoint.value) {
            formNewConnection(point, mapPartId);
        }
    }
    
    function rightClickPoint(e: MouseEvent, point: Point, mapPartId: number) {
        if (selectedPoint.value) {
            formNewConnection(point, mapPartId);
        } else {
            selectedPoint.value = {
                point, mapPartId
            };
            mousePosition.value = {
                x: point.x,
                y: point.y
            };
            moveStart.mouseX = e.clientX;
            moveStart.mouseY = e.clientY;
            moveStart.thisX = point.x;
            moveStart.thisY = point.y;
            document.body.addEventListener("mousemove", mouseMove);
        }
    }

    function mouseMove(e: MouseEvent) {
        const scale = panzoom.value?.getTransform().scale;
        if (!scale) return;
        const diffX = (e.clientX - moveStart.mouseX) / scale;
        const diffY = (e.clientY - moveStart.mouseY) / scale;
        mousePosition.value = {
            x: moveStart.thisX + diffX,
            y: moveStart.thisY + diffY
        };
    }

    onUnmounted(() => {
        document.body.removeEventListener("mousemove", mouseMove);
    });
    
    return {
        mousePosition,
        selectedPoint,
        clickPoint,
        rightClickPoint,
        newConnectionListeners
    };
});

export const useConnectionManager = (newConnectionListener?: (connection: PointConnection) => void) => {
    const store = useConnectionManagerStore();
    if (newConnectionListener) {
        // Add the listener
        store.newConnectionListeners.push(newConnectionListener);
        onUnmounted(() => {
            // Remove the listener
            const index = store.newConnectionListeners.indexOf(newConnectionListener);
            store.newConnectionListeners.splice(index, 1);
        });
    }
    return store;
};