<script setup lang="ts">
import { apiGet, errorHandler } from "@/api/api";
import MapPart from "@/components/mapviewer/MapPart.vue";
import PanZoom from "@/components/PanZoom.vue";
import { useAuth } from "@/stores/auth";
import type { MapPart as MapPartType, RoomWithZ } from "@/types";
import Swal from "sweetalert2";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import SearchBar from "@/components/mapviewer/SearchBar.vue";
import SearchSuggestions from "@/components/mapviewer/SearchSuggestions.vue";
import { useSelection } from "@/stores/selection";
import MobilePanel from "@/components/MobilePanel.vue";

interface Data {
    name: string;
    mapParts: MapPartType[];
    rooms: RoomWithZ[];
}

const route = useRoute();
const auth = useAuth();

// Data
const data = ref<Data | null>(null);

const floor = ref(1);

const visibleParts = computed(() => data.value?.mapParts.filter(mapPart => mapPart.z === floor.value));

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

        data.value = info.data;
    },
    { immediate: true }
);

// Search
const searchPrompt = ref("");
const showSearchSuggestions = ref(false);

// Selected room
const roomSelection = useSelection("room");

const selectedRoom = computed(() => data.value?.rooms.find(room => room.id === roomSelection.selected.value) ?? null);

function selectRoomFromSuggestion(room: RoomWithZ) {
    searchPrompt.value = room.name;
    roomSelection.select(room.id);
    showSearchSuggestions.value = false;
    
    // Change to the floor the room is at
    if (room.z !== floor.value) {
        floor.value = room.z;
    }
}

watch(searchPrompt, () => {
    const room = data.value?.rooms.find(room => room.name === searchPrompt.value);
    if (room) {
        roomSelection.select(room.id);
    }
});

const isLowestFloor = computed(() => {
    return !(data.value?.mapParts.find(mapPart => mapPart.z === floor.value - 1));
});
const isHighestFloor = computed(() => {
    return !(data.value?.mapParts.find(mapPart => mapPart.z === floor.value + 1));
});

</script>

<template>
    <div class="panzoom" v-if="visibleParts">
        <PanZoom>
            <MapPart
                v-for="mapPart of visibleParts"
                :key="mapPart.id"
                :map-part-id="mapPart.id"
                :offset-x="mapPart.offsetX"
                :offset-y="mapPart.offsetY"
                :rotation-deg="mapPart.rotationDeg"
                @data="(data) => data.rooms.push(...data.rooms)"
            />
        </PanZoom>
    </div>
    <div class="overlay">
        <div class="upper">
            <SearchBar
                v-model="searchPrompt"
                :show-back-arrow="showSearchSuggestions"
                @focus="showSearchSuggestions = true"
                @back="showSearchSuggestions = false"
            />
            <div class="search-suggestions"
                v-if="showSearchSuggestions && data"
            >
                <SearchSuggestions
                :rooms="data.rooms"
                :prompt="searchPrompt"
                @select="selectRoomFromSuggestion"
                />
            </div>
            <div class="floor-container">
                <button class="btn btn-secondary btn-sm" :disabled="isLowestFloor" @click="floor--">Ned</button>
                <span>Ändra våning</span>
                <button class="btn btn-secondary btn-sm" :disabled="isHighestFloor" @click="floor++">Upp</button>
            </div>
        </div>
        <MobilePanel :visible="selectedRoom != null" :sticky="true">
            <template
                v-if="selectedRoom"
            >
            <h5>{{ selectedRoom.name }}</h5>
            <button class="btn btn-primary">Hitta hit</button>
        </template>
        </MobilePanel>
    </div>
</template>

<style scoped>
.panzoom {
    width: 100%;
    height: 100%;
    overflow: hidden;
}
.overlay {
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
    grid-template-areas:
        "upper"
        "mobile-panel";
    position: fixed;
    width: 100%;
    height: 100%;
    top: 0px;
    pointer-events: none;
}
.overlay * {
    pointer-events: all;
}
.upper {
    position: relative;
    pointer-events: none;
    margin-bottom: 20px;
}
.search-suggestions {
    position: fixed;
    background-color: white;
    left: 0px;
    top: 0px;
    width: 100vw;
    height: 100vh;
    padding-top: 80px;
    z-index: 9;
}
.floor-container {
    position: absolute;
    bottom: 0px;
    right: 0px;
    background-color: white;
    box-shadow: 2px 2px 4px 1px;
    padding: 3px;
    border: 1px solid #bbb;
    border-radius: 5px;
}
.floor-container span {
    margin: 3px 5px;
}
@media (min-width: 600px)  {
    .search-suggestions {
        width: 420px;
        border-right: 1px solid #bbb;
    }
}

</style>