<script setup lang="ts">
import { apiGet, handleNetworkError } from "@/api/api";
import { ref } from "vue";

interface Map {
    id: number;
    name: string;
}

const data = ref<Map[] | null>(null);

async function fetchData() {
    const data2 = await apiGet("map/list")
        .catch(handleNetworkError);
    data.value = data2.maps;
}
fetchData();
</script>

<template>
    <div class="container">
        <h1>Kartredigeraren</h1>
        <div class="my-3">
            <h2>Skapa ny karta</h2>
            <RouterLink :to="'/mapmaker/maps/new'">
                <button class="btn btn-success">Ny karta</button>
            </RouterLink>
        </div>
        <div class="my-3">
            <h2>Kartor</h2>
            <p v-if="!data">Laddar...</p>
            <div v-if="data">
                <div v-for="map of data" :key="map.id" class="card m-3 d-inline-block">
                    <div class="card-body">
                        <h5 class="card-title">{{ map.name }}</h5>
                        <RouterLink :to="`/mapmaker/map/${map.id}`">
                            <button class="btn btn-primary">Redigera</button>
                        </RouterLink>
                    </div>
                </div>
                <p v-if="data.length == 0">Du har inga kartor. Skapa en!</p>
            </div>
        </div>
    </div>
</template>