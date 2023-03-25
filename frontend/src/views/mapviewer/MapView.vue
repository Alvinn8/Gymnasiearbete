<script setup lang="ts">
import { apiGet, apiPost, errorHandler } from "@/api/api";
import MapPart from "@/components/mapviewer/MapPart.vue";
import PanZoom from "@/components/PanZoom.vue";
import { useAuth } from "@/stores/auth";
import type { MapPart as MapPartType, PointWithZ, RoomCategory, RoomWithZ } from "@/types";
import Swal from "sweetalert2";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import SearchBar from "@/components/mapviewer/SearchBar.vue";
import SearchSuggestions from "@/components/mapviewer/SearchSuggestions.vue";
import { useSelection } from "@/stores/selection";
import MobilePanel from "@/components/MobilePanel.vue";
import RoomInfo from "@/components/mapviewer/RoomInfo.vue";
import PointConnection from "@/components/editor/PointConnection.vue";
import { useHighlightedRoomCategory } from "@/stores/highlight";

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

const floor = ref(0);

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

type RoomCallback = {
    text: string;
    callback: (room: RoomWithZ) => void;
}

// Search
const searchPrompt = ref("");
const showSearchSuggestions = ref(false);
const selectRoomCallback = ref<RoomCallback | null>(null);

// Selected room
const roomSelection = useSelection("room");

const selectedRoom = computed(() => data.value?.rooms.find(room => room.id === roomSelection.selected.value) ?? null);

function selectRoomFromSuggestion(room: RoomWithZ) {
    showSearchSuggestions.value = false;
    if (selectRoomCallback.value) {
        selectRoomCallback.value.callback(room);
        selectRoomCallback.value = null;
        return;
    }
    searchPrompt.value = room.name ?? "";
    roomSelection.select(room.id);
    
    // Change to the floor the room is at
    if (room.z !== floor.value) {
        floor.value = room.z;
    }
}

watch([searchPrompt, selectRoomCallback], () => {
    // We only want to select rooms when we are searching.
    if (selectRoomCallback.value) return;
    if (searchPrompt.value.trim().length === 0) return;
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

const isPathfinding = ref<false | "pathfinding" | "finding_closest">(false);
const pathfindStart = ref<RoomWithZ | null>(null);
const pathfindPath = ref<PointWithZ[] | null>(null);
const pathfindCategory = ref<RoomCategory | null>(null);
const pathfindExclude = ref<number[]>([]);
const pathfindConnections = computed(() => {
    if (!pathfindPath.value) return null;
    const array: [PointWithZ, PointWithZ][] = [];
    for (let i = 1; i < pathfindPath.value.length; i++) {
        const current = pathfindPath.value[i];
        const previous = pathfindPath.value[i - 1];
        // Only points on the current floor should be visible
        if (current.z === floor.value && previous.z === floor.value) {
            // Map the array to an array of pairs
            array.push([previous, current]);
        }
    }
    return array;
});

watch([isPathfinding, pathfindStart, selectedRoom], async () => {
    if (isPathfinding.value === "pathfinding" && pathfindStart.value !== null && selectedRoom.value !== null) {
        const endPointId = selectedRoom.value.doorAtPointId;
        const startPointId = pathfindStart.value.doorAtPointId;

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
});

const highlightedRoomCategory = useHighlightedRoomCategory();

watch([isPathfinding, pathfindStart, pathfindCategory, pathfindExclude], async () => {
    if (isPathfinding.value === "finding_closest" && pathfindStart.value !== null && pathfindCategory.value !== null) {
        const startPointId = pathfindStart.value.doorAtPointId;
        const roomCategory = pathfindCategory.value;
        const input = {
            startPointId,
            endCategoryId: roomCategory.id,
            excludeRoomIds: pathfindExclude.value
        };
        const res = await apiPost("map/pathfinding/find_closest", input)
            .catch(errorHandler([
                [(json: any) => !json.success, () => Swal.fire({
                    title: "Kunde inte hitta något!",
                    text: "Vi gick vilse, vi kunde inte hittade närmaste " + roomCategory.name,
                    icon: "error"
                })]
            ]));
        if (!res) return;

        pathfindPath.value = res.path as PointWithZ[];

        // Get the end point
        const endPointId = pathfindPath.value[pathfindPath.value.length - 1].id;

        // Find the room assosiated with that point.
        const room = data.value?.rooms.find(room => room.doorAtPointId === endPointId);

        if (room) {
            // Go to that floor
            if (floor.value !== room.z) {
                floor.value = room.z;
            }

            // Select the room
            roomSelection.select(room.id);
        }
    }
});

watch([isPathfinding, pathfindCategory], () => {
    if (isPathfinding.value === "finding_closest" && pathfindCategory.value && highlightedRoomCategory.roomCategoryId !== pathfindCategory.value.id) {
        // Highlight all rooms in the category
        highlightedRoomCategory.roomCategoryId = pathfindCategory.value.id;
    }
    if (isPathfinding.value !== "finding_closest" && highlightedRoomCategory.roomCategoryId !== null) {
        // Stop highlighting if we are not finding the closest
        highlightedRoomCategory.roomCategoryId = null;
    }
});

async function findClosest(roomCategory: RoomCategory) {
    pathfindExclude.value = [];
    roomSelection.deselect();
    isPathfinding.value = "finding_closest";
    pathfindCategory.value = roomCategory;
    if (pathfindStart.value === null) {
        searchPrompt.value = "";
        selectRoomCallback.value = {
            text: "Från",
            callback: (room) => {
                pathfindStart.value = room;
                findClosest(roomCategory);
            }
        };
        showSearchSuggestions.value = true;
        return;
    } else {
        showSearchSuggestions.value = false;
    }
}

async function findNextClosest() {
    if (!selectedRoom.value) return;
    
    // Exclude the current room
    pathfindExclude.value = [...pathfindExclude.value, selectedRoom.value.id];
    
    // And search again (watch will trigger)
}

async function findNextClosestFromHere() {
    if (!selectedRoom.value) return;
    
    // Exclude the current room
    pathfindExclude.value = [...pathfindExclude.value, selectedRoom.value.id];
    
    // Set the current room as the start
    pathfindStart.value = selectedRoom.value;

    // And search again (watch will trigger)
}

function pathfindStartInputClick() {
    searchPrompt.value = "";
    selectRoomCallback.value = {
        text: "Från",
        callback: (room) => {
            pathfindStart.value = room;
        }
    };
    showSearchSuggestions.value = true;
}

function pathfindEndInputClick() {
    searchPrompt.value = "";
    selectRoomCallback.value = {
        text: "Till",
        callback: (room) => {
            roomSelection.select(room.id);
        }
    };
    showSearchSuggestions.value = true;
}

function stopPathfinding() {
    isPathfinding.value = false;
    pathfindCategory.value = null;
    selectRoomCallback.value = null;
    showSearchSuggestions.value = false;
}

function formatRoomName(room: RoomWithZ | null) {
    if (!room) return "";
    if (room.name) return room.name;
    const roomCategory = data.value?.roomCategories.find(roomCategory => roomCategory.id === room.categoryId);
    if (!roomCategory) return "Rum";
    return `${roomCategory.name} (specifik)`;
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
                :z="mapPart.z"
                @data="(data) => data.rooms.push(...data.rooms)"
                @change-floor="newFloor => floor = newFloor"
            />
            
            <template v-if="pathfindPath">
                <PointConnection
                    v-for="[pointA, pointB] in pathfindConnections"
                    :key="pointA.id"
                    :point_a="pointA"
                    :point_b="pointB"
                />
            </template>
        </PanZoom>
    </div>
    <div class="overlay">
        <div class="upper">
            <template v-if="isPathfinding && !selectRoomCallback">
                <SearchBar
                    :model-value="formatRoomName(pathfindStart)"
                    :show-back-arrow="true"
                    prefix="Från"
                    @focus="pathfindStartInputClick"
                    @back="stopPathfinding"
                />
                <SearchBar
                    v-if="isPathfinding === 'pathfinding'"
                    :model-value="formatRoomName(selectedRoom)"
                    :show-back-arrow="true"
                    prefix="Till"
                    @focus="pathfindEndInputClick"
                    @back="stopPathfinding"
                />
                <div
                    v-if="isPathfinding === 'finding_closest'"
                    class="closest-box"
                >
                    <div class="mb-2">
                        <span><strong>Till: </strong>Närmaste {{ pathfindCategory?.name }}</span>
                    </div>
                    <div>
                        <button class="btn btn-primary mx-1" @click="findNextClosest">Nästa</button>
                        <button class="btn btn-primary mx-1" @click="findNextClosestFromHere">Nästa härifrån</button>
                    </div>
                </div>
            </template>
            <template v-else>
                <SearchBar
                    v-model="searchPrompt"
                    :show-back-arrow="showSearchSuggestions"
                    :prefix="selectRoomCallback?.text"
                    @focus="showSearchSuggestions = true"
                    @back="stopPathfinding"
                />
            </template>
            <div class="search-suggestions"
                v-if="showSearchSuggestions && data"
            >
                <SearchSuggestions
                :rooms="data.rooms"
                :room-categories="data.roomCategories"
                :prompt="searchPrompt"
                :show-categories="selectRoomCallback === null"
                @select-room="selectRoomFromSuggestion"
                @select-room-category="findClosest"
                />
            </div>
            <div class="desktop-room-info-container">
                <RoomInfo
                    v-if="selectedRoom && data"
                    :room="selectedRoom"
                    :room-categories="data.roomCategories"
                    @pathfind="isPathfinding = 'pathfinding'"
                />
            </div>
            <div class="floor-container">
                <button class="btn btn-secondary btn-sm" :disabled="isLowestFloor" @click="floor--">Ned</button>
                <span>Ändra våning</span>
                <button class="btn btn-secondary btn-sm" :disabled="isHighestFloor" @click="floor++">Upp</button>
            </div>
        </div>
        <div class="mobile-panel-container">
            <MobilePanel :visible="selectedRoom != null" :sticky="true">
                <div v-if="selectedRoom && data" class="container">
                    <RoomInfo
                        :room="selectedRoom"
                        :room-categories="data.roomCategories"
                        @pathfind="isPathfinding = 'pathfinding'"
                    />
                </div>
            </MobilePanel>
        </div>
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
    overflow: auto;
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
.closest-box {
    width: calc(100vw - 20px);
    border-radius: 10px;
    border: 1px solid #bbb;
    box-shadow: 2px 2px 4px 1px;
    padding: 12px;
    margin: 10px;
    cursor: default;
    background-color: white;
}
.desktop-room-info-container {
    /* On mobile, only show the bottom sheet / mobile panel, and hide the
       desktop container. */
    display: none;

    /* CSS (desktop only) */
    z-index: 8;
    background-color: rgb(255, 255, 255, 0.75);
    border-right: 1px solid #bbb;
    border-bottom: 1px solid #bbb;
    width: 410px;
    padding: 20px;
    border-bottom-right-radius: 5px;
}
@media (min-width: 600px)  {
    .closest-box {
        max-width: 400px;
    }
}
@media (min-width: 700px)  {
    .search-suggestions {
        width: 420px;
        border-right: 1px solid #bbb;
    }
    .mobile-panel-container {
        /* Hide mobile panel on desktop. */
        display: none;
    }
    .desktop-room-info-container {
        /* And show the desktop container. */
        display: block;
    }
}

</style>