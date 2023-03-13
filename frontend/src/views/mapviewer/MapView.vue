<script setup lang="ts">
import { apiGet, apiPost, errorHandler } from "@/api/api";
import MapPart from "@/components/mapviewer/MapPart.vue";
import PanZoom from "@/components/PanZoom.vue";
import { useAuth } from "@/stores/auth";
import type { MapPart as MapPartType, PointWithPosition, Room, RoomCategory, RoomWithZ } from "@/types";
import Swal from "sweetalert2";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import SearchBar from "@/components/mapviewer/SearchBar.vue";
import SearchSuggestions from "@/components/mapviewer/SearchSuggestions.vue";
import { useSelection } from "@/stores/selection";
import MobilePanel from "@/components/MobilePanel.vue";
import RoomInfo from "@/components/mapviewer/RoomInfo.vue";
import PointConnection from "@/components/editor/PointConnection.vue";

interface Data {
    name: string;
    mapParts: MapPartType[];
    rooms: RoomWithZ[];
    roomCategories: RoomCategory[];
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

const prevRoom = ref<Room | null>(null);
const pathfindPath = ref<PointWithPosition[] | null>(null);

async function pathfindToRoom(room: Room) {
    const endPointId = room.doorAtPointId;
    const startPointId = prevRoom.value?.doorAtPointId;
    prevRoom.value = room;
    if (!startPointId) {
        alert("no start point, plz select yes");
        return;
    }

    const res = await apiPost("map/pathfinding/find_path", { startPointId, endPointId })
        .catch(errorHandler([
            [(json: any) => !json.success, () => Swal.fire({
                title: "Kunde inte hitta en väg.",
                text: "Vi gick vilse, det verkar inte gå att gå sådär som du vill",
                icon: "error"
            })]
        ]));
    if (!res) return;

    pathfindPath.value = res.path;
}

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
            
            <template v-if="pathfindPath">
                <PointConnection
                    v-for="(current_point, index) in pathfindPath"
                    :key="index"
                    :point_a="current_point"
                    :point_b="pathfindPath[index - 1] ?? current_point"
                />
            </template>
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
                :room-categories="data.roomCategories"
                :prompt="searchPrompt"
                @select-room="selectRoomFromSuggestion"
                />
            </div>
            <div class="floor-container">
                <button class="btn btn-secondary btn-sm" :disabled="isLowestFloor" @click="floor--">Ned</button>
                <span>Ändra våning</span>
                <button class="btn btn-secondary btn-sm" :disabled="isHighestFloor" @click="floor++">Upp</button>
            </div>
        </div>
        <MobilePanel :visible="selectedRoom != null" :sticky="true">
            <div v-if="selectedRoom && data" class="container">
                <RoomInfo
                    :room="selectedRoom"
                    :room-categories="data.roomCategories"
                    @pathfind="() => selectedRoom && pathfindToRoom(selectedRoom)"
                />
            </div>
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