<script setup lang="ts">
import { apiGet, apiDelete, errorHandler, apiPost, handleError } from "@/api/api";
import { useRoute } from "vue-router";
import { reactive, ref, watch } from "vue";
import Swal from "sweetalert2";
import router from "@/router";
import PanZoom from "@/components/PanZoom.vue";
import EditableWall from "@/components/editor/EditableWall.vue";

interface Data {
    name: string;
    mapParts: {
        id: number;
        name: string;
    }[];
}

interface Wall {
    id: number;
    x: number;
    y: number;
    width: number;
    height: number;
}

interface MapPartData {
    walls: Wall[];
}

const route = useRoute();
const data = reactive<Data>({
    name: "",
    mapParts: []
});
const currentMapPartId = ref<number | null>(null);
const mapPartData = reactive<MapPartData>({
    walls: []
});

watch(
    () => route.params.map_id,
    async mapId => {
        const info = await apiGet(`map/${mapId}/info`)
            .catch(errorHandler([
                [json => !json.success, (json: any) => Swal.fire({
                    title: json.error,
                    icon: "error"
                })]
            ]));
        if (!info) return;

        data.name = info.data.name;
        data.mapParts = info.data.mapParts;
    },
    { immediate: true }
);

watch(currentMapPartId, async () => {
    const info = await apiGet(`map/${route.params.map_id}/part/${currentMapPartId.value}/info`)
        .catch(handleError);
    if (!info) return;

    mapPartData.walls = info.walls;
});

async function deleteMap() {
    const result = await Swal.fire({
        title: "Är du säker?",
        showCancelButton: true,
        cancelButtonText: "Avbryt",
        confirmButtonText: "Radera",
        confirmButtonColor: "red"
    });
    if (!result.isConfirmed) {
        return;
    }
    const mapId = route.params.map_id;
    await apiDelete(`map/${mapId}`);
    router.push({
        name: "maps"
    });
}

async function newPart() {
    const res = await Swal.fire({
        title: "Skapa ny kartdel",
        input: "text",
        showCancelButton: true,
        showLoaderOnConfirm: true,
        preConfirm: async (name) => {
            const res = await apiPost(`map/${route.params.map_id}/part/new`, {
                name: name
            }).catch(handleError);
            return {
                id: res.id,
                name: name
            };
        },
        allowOutsideClick: () => !Swal.isLoading()
    });
    if (res.isConfirmed && res.value) {
        const { id, name } = res.value;
        data.mapParts.push({ id, name });
        currentMapPartId.value = id;
        Swal.fire({
            title: "Kartdelen har skapats",
            icon: "success"
        });
    }
}
</script>

<template>
    <div class="container">
        <h1>{{ data?.name }}</h1>
        <div class="row">
            <div class="col part">
                <div v-if="data && data.mapParts.length > 0">
                    <p>Nuvarande kartdel: {{ data.mapParts.find(part => part.id === currentMapPartId)?.name }}</p>
                    <select class="form-select" v-model="currentMapPartId">
                        <option v-for="mapPart of data.mapParts" :key="mapPart.id" :value="mapPart.id">
                            {{ mapPart.name }}
                        </option>
                    </select>
                </div>
                <button class="btn btn-success" @click="newPart">Skapa ny kartdel</button>
            </div>
            <div class="col">
                <button class="btn btn-danger" @click="deleteMap">Radera karta</button>
            </div>
        </div>
    </div>
    <div class="container-fluid">
        <PanZoom>
            <div v-if="!mapPartData">
                <p>Vänligen välj kartdel.</p>
            </div>
            <div v-if="mapPartData">

                <EditableWall />
            </div>
        </PanZoom>
    </div>
</template>

<style scoped>
.container-fluid {
    overflow: hidden;
    border: 2px solid #ddd;
    height: 85vh;
}

.part {
    max-width: 20em;
}
</style>