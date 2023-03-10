<script setup lang="ts">
import type { Room, RoomCategory } from "@/types";
import { computed } from "vue";

const props = defineProps<{
    room: Room;
    roomCategories: RoomCategory[];
}>();

const roomCategory = computed(() => props.roomCategories.find(
    roomCategory => roomCategory.id === props.room.categoryId
));

</script>

<template>
    <h4>{{ room.name }}</h4>
    <p v-if="roomCategory" class="category">{{ roomCategory.name }}</p>
    <button class="btn btn-primary">Hitta hit</button>
</template>

<style scoped>
.category {
    color: #444;
}
</style>