<script setup lang="ts">
import type { Room, RoomWithZ } from "@/types";
import { computed } from "vue";

const props = defineProps<{
    rooms: RoomWithZ[];
    prompt: string;
}>();

const emit = defineEmits<{
    (e: "select", room: RoomWithZ): void;
}>();

const filteredRooms = computed(() => props.rooms
    .filter(room => room.name.toUpperCase().includes(
        props.prompt.trim().toUpperCase()
    ))
);

</script>

<template>
    <ul>
        <li
            v-for="room in filteredRooms"
            :key="room.id"
            @click="emit('select', room)"
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