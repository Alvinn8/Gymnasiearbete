<script setup lang="ts">
import type { RoomCategory, RoomWithZ } from "@/types";
import { computed } from "vue";

const props = defineProps<{
    rooms: RoomWithZ[];
    roomCategories: RoomCategory[];
    prompt: string;
}>();

const emit = defineEmits<{
    (e: "select-room", room: RoomWithZ): void;
    (e: "select-room-category", roomCategory: RoomCategory): void;
}>();

const filteredRooms = computed(() => props.rooms
    .filter(room => room.name.toUpperCase().includes(
        props.prompt.trim().toUpperCase()
    ))
    .sort()
);

const filteredRoomCategories = computed(() => props.roomCategories
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
            <span>{{ roomCategory.name }}</span>
            <small>Hitta närmaste</small>
        </li>
        <li
            v-for="room in filteredRooms"
            :key="room.id"
            @click="emit('select-room', room)"
        >{{ room.name }}</li>
    </ul>
</template>

<style scoped>
li {
    list-style-type: none;
    padding: 20px 0px;
    border-bottom: 1px solid #bbb;
}
</style>