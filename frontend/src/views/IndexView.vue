<script setup lang="ts">
import { apiGet, handleError } from "@/api/api";
import { ref } from "vue";

type FeaturedMap = {
    id: number;
    name: string;
}

const featuredMap = ref<FeaturedMap | null>(null);

apiGet("map/get_featured_map")
    .then(json => featuredMap.value = json.map)
    .catch(handleError);

</script>

<template>
    <div class="container">
        <div class="row vh-100">
            <div class="col-lg align-self-center">
                <h1>Kartor för byggnader</h1>
                <RouterLink
                    v-if="featuredMap"
                    :to="{ name: 'view-map', params: { map_id: featuredMap.id } }"
                    class="btn btn-primary"
                >Hitta på {{ featuredMap.name }}</RouterLink>
            </div>
            <div class="col align-self-center">
                <RouterLink to="/register" class="btn btn-primary">Skapa egna kartor</RouterLink>
            </div>
        </div>
    </div>
</template>