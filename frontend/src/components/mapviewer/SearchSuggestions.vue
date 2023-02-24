<script setup lang="ts">
import type { Room } from "@/types";
import { computed } from "vue";

const props = defineProps<{
    rooms: Room[];
    prompt: string;
}>();

const emit = defineEmits<{
    (e: "select", room: Room): void;
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