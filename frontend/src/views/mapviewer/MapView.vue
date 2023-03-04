<script setup lang="ts">
import { apiGet, errorHandler } from "@/api/api";
import MapPart from "@/components/mapviewer/MapPart.vue";
import PanZoom from "@/components/PanZoom.vue";
import { useAuth } from "@/stores/auth";
import type { MapPart as MapPartType, Room } from "@/types";
import Swal from "sweetalert2";
import { computed, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import SearchBar from "@/components/mapviewer/SearchBar.vue";
import SearchSuggestions from "@/components/mapviewer/SearchSuggestions.vue";
import { useSelection } from "@/stores/selection";

interface Data {
    name: string;
    mapParts: MapPartType[];
}

const route = useRoute();
const auth = useAuth();

// Data
const data = reactive<Data>({
    name: "",
    mapParts: []
});

const floor = ref(1);

const visibleParts = computed(() => data.mapParts.filter(mapPart => mapPart.z === floor.value));

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

const rooms = ref<Room[]>([]);

// Search
const searchPrompt = ref("");
const showSearchSuggestions = ref(false);

// Selected room
const roomSelection = useSelection("room");

function selectRoomFromSuggestion(room: Room) {
    searchPrompt.value = room.name;
    roomSelection.select(room.id);
    showSearchSuggestions.value = false;
}

watch(searchPrompt, () => {
    const room = rooms.value.find(room => room.name === searchPrompt.value);
    if (room) {
        roomSelection.select(room.id);
    }
});

</script>

<template>
    <div class="panzoom">
        <PanZoom>
            <MapPart
                v-for="mapPart of visibleParts"
                :key="mapPart.id"
                :map-part-id="mapPart.id"
                :offset-x="mapPart.offsetX"
                :offset-y="mapPart.offsetY"
                :rotation-deg="mapPart.rotationDeg"
                @data="(data) => rooms.push(...data.rooms)"
            />
        </PanZoom>
    </div>
    <SearchBar
        v-model="searchPrompt"
        :show-back-arrow="showSearchSuggestions"
        @focus="showSearchSuggestions = true"
        @back="showSearchSuggestions = false"
    />
    <div class="search-suggestions"
        v-if="showSearchSuggestions"
    >
        <SearchSuggestions
            :rooms="rooms"
            :prompt="searchPrompt"
            @select="selectRoomFromSuggestion"
        />
    </div>
</template>

<style scoped>
.panzoom {
    width: 100%;
    height: 100%;
}
.search-suggestions {
    position: fixed;
    background-color: white;
    left: 0px;
    top: 0px;
    width: 100vw;
    height: 100vh;
    padding-top: 80px;
}
@media (min-width: 600px)  {
    .search-suggestions {
        width: 420px;
        border-right: 1px solid #bbb;
    }
}

</style>