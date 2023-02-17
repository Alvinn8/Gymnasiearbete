<script setup lang="ts">
import { apiGet, errorHandler, apiPost, handleError } from "@/api/api";
import { useRoute } from "vue-router";
import { provide, reactive, ref, watch } from "vue";
import Swal from "sweetalert2";
import DeleteMap from "@/components/editor/DeleteMap.vue";
import MapPartEditor from "@/components/editor/MapPartEditor.vue";
import { mapPartIdKey } from "@/components/keys";
import MapRelationEditor from "@/components/editor/relation/MapRelationEditor.vue";

interface Data {
    name: string;
    mapParts: {
        id: number;
        name: string;
    }[];
}

const route = useRoute();
const data = reactive<Data>({
    name: "",
    mapParts: []
});
const currentMapPartId = ref<number | null>(null);

provide(mapPartIdKey, currentMapPartId);

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
        <div class="row">
            <div class="col">
                <h1>{{ data?.name }}</h1>
            </div>
            <div class="col">
                <button class="btn btn-primary m-1">Dela karta</button>
                <DeleteMap />
            </div>
            <div class="col part">
                <div v-if="data && data.mapParts.length > 0">
                    <select class="form-select" v-model="currentMapPartId">
                        <option value="null" disabled>Välj en kartdel</option>
                        <option v-for="mapPart of data.mapParts" :key="mapPart.id" :value="mapPart.id">
                            {{ mapPart.name }}
                        </option>
                    </select>
                </div>
                <button class="btn btn-success" @click="newPart">Skapa ny kartdel</button>
            </div>
        </div>
    </div>
    <MapPartEditor
        v-if="currentMapPartId"
    />
    <MapRelationEditor
        v-if="!currentMapPartId"
    />
</template>