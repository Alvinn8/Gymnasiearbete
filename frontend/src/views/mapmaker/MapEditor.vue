<script setup lang="ts">
import { apiGet, apiDelete, errorHandler } from "@/api/api";
import { useRoute } from "vue-router";
import { ref, watch } from "vue";
import Swal from "sweetalert2";
import router from "@/router";
import PanZoom from "@/components/PanZoom.vue";
import EditableWall from "@/components/editor/EditableWall.vue";

const route = useRoute();
const name = ref<string>("");

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
        if (info) {
            name.value = info.name;
        }
    },
    { immediate: true }
);

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

</script>

<template>
    <h1>{{ name }}</h1>
    <button class="btn btn-danger" @click="deleteMap">Radera karta</button>
    <div class="container-fluid">
        <PanZoom>
            <p>Hello!</p>
            <EditableWall />
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