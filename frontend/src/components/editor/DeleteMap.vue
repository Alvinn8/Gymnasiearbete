<script setup lang="ts">
import { apiDelete } from "@/api/api";
import router from "@/router";
import Swal from "sweetalert2";
import { useRoute } from "vue-router";

const route = useRoute();

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
    <button class="btn btn-danger m-1" @click="deleteMap">Radera karta</button>
</template>