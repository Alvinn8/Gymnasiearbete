<script setup lang="ts">
import type { Room, RoomCategory } from "@/types";
import { computed } from "vue";

const props = withDefaults(defineProps<{
    room: Room;
    roomCategories: RoomCategory[];
    showNavigateButton?: boolean;
}>(), {
    showNavigateButton: true // default value
});

const emit = defineEmits<{
    (e: "pathfind"): void;
}>();

const roomCategory = computed(() => props.roomCategories.find(
    roomCategory => roomCategory.id === props.room.categoryId
));

</script>

<template>
    <h4>{{ room.name }}</h4>
    <p v-if="roomCategory" class="category">{{ roomCategory.name }}</p>
    <button
        v-if="showNavigateButton"
        class="btn btn-primary"
        @click="emit('pathfind')"
    >Hitta hit</button>
</template>

<style scoped>
.category {
    color: #444;
}
</style>