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
    walls: Wall[] | null;
    background: string | null;
}

const route = useRoute();
const data = reactive<Data>({
    name: "",
    mapParts: []
});
const currentMapPartId = ref<number | null>(null);
const mapPartData = reactive<MapPartData>({
    walls: null,
    background: null
});
const fileInput = ref<HTMLInputElement | null>(null);

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
        .catch(err => console.error(err));
    if (!info) return;

    mapPartData.walls = info.walls;

    if (info.background) {
        mapPartData.background = info.background;
    }
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

async function changeBackground() {
    if (!fileInput.value?.files) return;

    const file = fileInput.value?.files[0];
    if (!file) return;

    const base64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = () => {
            const url = reader.result;
            if (typeof url !== "string") {
                reject();
                return;
            }
            resolve(url);
        };
    });

    await apiPost(`map/${route.params.map_id}/part/${currentMapPartId.value}/background`, {
        file: base64
    });

    mapPartData.background = base64;
}

async function newWall() {
    if (!mapPartData.walls) return;

    const res = await apiPost(`map/${route.params.map_id}/part/${currentMapPartId.value}/wall/new`, {})
        .catch(handleError);
    
    if (!res) return;
    
    const wall = {
        id: res.id,
        x: 0,
        y: 0,
        width: 10,
        height: 40
    };

    const wall0 = mapPartData.walls[0];
    if (wall0) {
        wall.x = wall0.x + 40;
        wall.y = wall0.y + 40;
        wall.width = wall0.width;
        wall.height = wall0.height;
    }

    mapPartData.walls.push(wall);
}

type Change = { id: number, property: string, value: number };
let pendingChanges: Change[] = [];
let pendingChangesId: number | null = null;

function appendChange(change: Change) {
    if (pendingChangesId) clearTimeout(pendingChangesId);
    pendingChanges.push(change);
    pendingChangesId = setTimeout(() => {
        apiPost(`map/${route.params.map_id}/part/${currentMapPartId.value}/wall/edit`, {
            changes: pendingChanges
        });
        pendingChanges = [];
    }, 2500);
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
                <button class="btn btn-success" @click="newWall">Ny vägg</button>
            </div>
            <div class="col">
                <p>Ändra bakgrundsbild.</p>
                <input type="file" ref="fileInput" class="form-control" accept=".png,.svg,.jpg,.webp"
                    @change="changeBackground">
            </div>
            <div class="col">
                <button class="btn btn-danger" @click="deleteMap">Radera karta</button>
            </div>
        </div>
    </div>
    <div class="container-fluid">
        <PanZoom>
            <div v-if="!mapPartData.walls">
                <p>Vänligen välj kartdel.</p>
            </div>
            <img v-if="mapPartData.background" :src="mapPartData.background" alt="Bakgrund">
            <div v-if="mapPartData.walls">
                <EditableWall v-for="wall of mapPartData.walls" :key="wall.id" :x="wall.x" :y="wall.y"
                    :width="wall.width" :height="wall.height"
                    :on-change="(property, value) => { wall[property] = value; appendChange({ id: wall.id, property, value }) }" />
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