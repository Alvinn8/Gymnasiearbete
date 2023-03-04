<script setup lang="ts">
import { apiGet, errorHandler, apiPost, handleError } from "@/api/api";
import { useRoute } from "vue-router";
import { computed, reactive, ref, watch } from "vue";
import Swal from "sweetalert2";
import DeleteMap from "@/components/editor/DeleteMap.vue";
import type { MapPart as MapPartType } from "@/types";
import MapPart from "@/components/mapviewer/MapPart.vue";
import MapPartEditor from "@/components/editor/MapPartEditor.vue";
import MapEditorBase from "@/components/editor/MapEditorBase.vue";

interface Data {
    name: string;
    public: boolean;
    mapParts: MapPartType[];
}

const route = useRoute();
const data = reactive<Data>({
    name: "",
    public: false,
    mapParts: []
});
const currentMapPartId = ref<number | null>(null);
const floor = ref(0);

const visibleParts = computed(() => data.mapParts.filter(mapPart => mapPart.z === floor.value));

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
        data.public = info.data.public;
        data.mapParts = info.data.mapParts;
    },
    { immediate: true }
);

async function newPart() {
    const res = await Swal.fire({
        title: "Skapa ny kartdel",
        input: "text",
        showCancelButton: true,
        showLoaderOnConfirm: true,
        preConfirm: async (name) => {
            const res = await apiPost(`map/${route.params.map_id}/part/new`, {
                name: name,
                z: floor.value
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
        data.mapParts.push({
            id, name,
            offsetX: 0,
            offsetY: 0,
            rotationDeg: 0,
            z: floor.value
        });
        currentMapPartId.value = id;
        Swal.fire({
            title: "Kartdelen har skapats",
            icon: "success"
        });
    }
}

function updateOffset(mapPart: MapPartType) {
    apiPost(`map/${route.params.map_id}/part/${mapPart.id}/update_offset`, {
        offsetX: mapPart.offsetX,
        offsetY: mapPart.offsetY,
        rotationDeg: mapPart.rotationDeg
    }).catch(handleError);
}

async function share() {
    const res = await Swal.fire({
        title: "Dela karta",
        text: "Ange användarnamn/e-post på användaren du vill dela kartan med.",
        input: "text",
        showCancelButton: true
    });
    if (res.isConfirmed) {
        const apiResponse = await apiPost(`map/${route.params.map_id}/share`, {
            username: res.value
        }).catch(handleError);
        if (apiResponse) {
            Swal.fire({
                title: "Kartan har delats.",
                icon: "success"
            });
        }
    }
}

async function changePublicStatus(isPublic: boolean) {
    const res = await Swal.fire({
        title: "Är du säker?",
        text: isPublic
            ? "Offentliga kartor kan ses av alla med länken."
            : "Privata kartor kan endast ses av användare med tillgång till den.",
        showCancelButton: true
    });
    if (res.isConfirmed) {
        const apiResponse = await apiPost(`map/${route.params.map_id}/change_public_status`, {
            public: isPublic
        }).catch(handleError);
        if (apiResponse) {
            Swal.fire({
                title: isPublic ? "Kartan är nu offentlig." : "Kartan är nu privat.",
                icon: "success"
            });
            data.public = isPublic;
        }
    }
}

</script>

<template>
    <div class="container">
        <div class="row">
            <div class="col">
                <h1>{{ data?.name }}</h1>
            </div>
            <div class="col">
                <button class="btn btn-primary m-1" @click="share">Dela karta</button>
                <button class="btn btn-warning m-1"
                    @click="() => changePublicStatus(true)"
                    v-if="!data.public"
                    >Gör till offentlig karta</button>
                <button class="btn btn-warning m-1"
                    @click="() => changePublicStatus(false)"
                    v-if="data.public"
                >Gör till privat karta</button>
                <DeleteMap />
            </div>
        </div>
    </div>

    <!-- No selected map part. -->
    <MapEditorBase v-if="!currentMapPartId">
        <template #panzoom>
            <MapPart
                v-for="mapPart of visibleParts"
                :key="mapPart.id"
                :map-part-id="mapPart.id"
                :offset-x="mapPart.offsetX"
                :offset-y="mapPart.offsetY"
                :rotation-deg="mapPart.rotationDeg"
            />
        </template>
        <template #aside>
            <div class="mb-3">
                <h3>Våning</h3>
                <input type="number" v-model="floor">
            </div>
            <div class="mb-3">
                <h2>Kartdelar</h2>
                <button class="btn btn-success" @click="newPart">Skapa ny kartdel</button>
            </div>
            <div
            v-for="mapPart of data.mapParts"
            :key="mapPart.id"
            class="mb-3"
            >
                <h3>{{ mapPart.name }}</h3>
                <button class="btn btn-primary" @click="currentMapPartId = mapPart.id">Redigera</button>
                <br>
                <input type="number" v-model="mapPart.offsetX">
                <input type="number" v-model="mapPart.offsetY">
                <input type="number" v-model="mapPart.rotationDeg">
                <button
                    class="btn btn-primary btn-sm"
                    @click="() => updateOffset(mapPart)"
                >Spara</button>
            </div>
        </template>
    </MapEditorBase>

    <!-- A selected map part. -->
    <MapPartEditor
        v-if="currentMapPartId"
        :map-part-id="currentMapPartId"
        @back="currentMapPartId = null"
    />
</template>

<style scoped>
input {
    max-width: 80px;
}
</style>