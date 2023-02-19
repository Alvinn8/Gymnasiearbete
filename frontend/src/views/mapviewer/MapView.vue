<script setup lang="ts">
import { apiGet, errorHandler } from "@/api/api";
import MapPart from "@/components/mapviewer/MapPart.vue";
import PanZoom from "@/components/PanZoom.vue";
import { useAuth } from "@/stores/auth";
import type { MapPart as MapPartType } from "@/types";
import Swal from "sweetalert2";
import { reactive, watch } from "vue";
import { useRoute } from "vue-router";

interface Data {
    name: string;
    mapParts: MapPartType[];
}

const route = useRoute();
const auth = useAuth();
const data = reactive<Data>({
    name: "",
    mapParts: []
});

watch(
    () => route.params.map_id,
    async mapId => {
        const info = await apiGet(`map/${mapId}/view`)
            .catch(errorHandler([
                [json => !json.success, (json: any) => Swal.fire({
                    title: json.error,
                    icon: "error"
                })],
                [403, () => Swal.fire({
                    title: "Du har inte behörighet.",
                    text: "Du har inte behörighet att se denna karta." + (!auth.isLoggedIn ? " Testa att logga in." : ""),
                    icon: "error"
                })]
            ]));
        if (!info) return;

        data.name = info.data.name;
        data.mapParts = info.data.mapParts;
    },
    { immediate: true }
);

</script>

<template>
    <p>hello</p>
    <p>{{ data.name }}</p>
    <p>{{ JSON.stringify(data.mapParts) }}</p>
    <div class="container-fluid">
        <PanZoom>
            <MapPart
                v-for="mapPart of data.mapParts"
                :key="mapPart.id"
                :map-part-id="mapPart.id"
                :offset-x="mapPart.offsetX"
                :offset-y="mapPart.offsetY"
                :rotation-deg="mapPart.rotationDeg"
            />
        </PanZoom>
    </div>
</template>

<style scoped>
.container-fluid {
    overflow: hidden;
    border: 2px solid #ddd;
    height: 85vh;
}
</style>