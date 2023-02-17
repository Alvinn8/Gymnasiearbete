<script setup lang="ts">
import { apiGet, handleError } from "@/api/api";
import MapPart from "@/components/mapviewer/MapPart.vue";
import PanZoom from "@/components/PanZoom.vue";
import { reactive, watch } from "vue";
import { useRoute } from "vue-router";

interface Data {
    name: string;
    mapParts: {
        id: number;
        name: string;
        offsetX: number;
        offsetY: number;
    }[];
}

const route = useRoute();
const data = reactive<Data>({
    name: "",
    mapParts: []
});

watch(
    () => route.params.map_id,
    async mapId => {
        const info = await apiGet(`map/${mapId}/view`)
            .catch(handleError);
        if (!info) return;

        data.name = info.data.name;
        data.mapParts = info.data.mapParts;
    },
    { immediate: true }
);

</script>

<template>
    <div class="row">
        <div class="panzoom_container col">
            <PanZoom>
                <MapPart
                    v-for="mapPart of data.mapParts"
                    :key="mapPart.id"
                    :map-part-id="mapPart.id"
                    :offset-x="mapPart.offsetX"
                    :offset-y="mapPart.offsetY"
                />
            </PanZoom>
        </div>
        <aside class="col" id="relation-side-editor">
            <div
                v-for="mapPart of data.mapParts"
                :key="mapPart.id"
            >
            <h3>{{ mapPart.name }}</h3>
            <input type="number" v-model="mapPart.offsetX">
            <input type="number" v-model="mapPart.offsetY">
        </div>
        </aside>
    </div>
</template>

<style scoped>
.panzoom_container {
    overflow: hidden;
    border: 2px solid #ddd;
    height: 85vh;
}
#relation-side-editor {
    width: 20vw;
}
</style>