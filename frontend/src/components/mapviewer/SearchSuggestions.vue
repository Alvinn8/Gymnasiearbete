<script setup lang="ts">
import { useFavoriteRooms } from "@/stores/favoriteRooms";
import type { RoomCategory, RoomWithZ } from "@/types";
import { computed } from "vue";
import StarIcon from "../StarIcon.vue";

const props = defineProps<{
    rooms: RoomWithZ[];
    roomCategories: RoomCategory[];
    showCategories: boolean;
    prompt: string;
}>();

const emit = defineEmits<{
    (e: "select-room", room: RoomWithZ): void;
    (e: "select-room-category", roomCategory: RoomCategory): void;
}>();

const favoriteRooms = useFavoriteRooms();

const filteredRooms = computed(() => props.rooms
    .filter(room => room.name && room.name.toUpperCase().includes(
        props.prompt.trim().toUpperCase()
    ))
    .sort((a, b) => {
        const aIsFavorite = favoriteRooms.isFavorite(a);
        const bIsFavorite = favoriteRooms.isFavorite(b);
        if (aIsFavorite && !bIsFavorite) {
            return -1;
        } else if (bIsFavorite && !aIsFavorite) {
            return 1;
        }
        if (a.name && b.name) {
            return a.name > b.name ? 1 : -1;
        }
        return 0;
    })
);

const filteredRoomCategories = computed(() => !props.showCategories ? [] : props.roomCategories
    .filter(roomCategory => roomCategory.name.toUpperCase().includes(
        props.prompt.trim().toUpperCase()
    )));

</script>

<template>
    <ul>
        <li
            v-for="roomCategory in filteredRoomCategories"
            :key="roomCategory.id"
            @click="emit('select-room-category', roomCategory)"
        >
            <div class="row">
                <div class="col-auto">
                    <!-- SVG from Bootstrap Icons https://icons.getbootstrap.com/icons/search/ -->
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                        <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                    </svg>
                </div>
                <div class="col">
                    <span>{{ roomCategory.name }}</span>
                    <small>Hitta närmaste</small>
                </div>
            </div>
        </li>
        <li
            v-for="room in filteredRooms"
            :key="room.id"
            @click="emit('select-room', room)"
        >
            <template v-if="favoriteRooms.isFavorite(room)">
                <StarIcon :fill="true" />
                <span class="me-2"></span>
            </template>
            <span>{{ room.name }}</span>
        </li>
    </ul>
</template>

<style scoped>
li {
    list-style-type: none;
    padding: 20px 0px;
    border-bottom: 1px solid #bbb;
}
small {
    display: block;
}
.bi-search {
    margin-top: 11px;
}
</style>