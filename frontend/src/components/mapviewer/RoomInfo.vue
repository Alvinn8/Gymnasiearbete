<script setup lang="ts">
import { useAuth } from "@/stores/auth";
import { useFavoriteRooms } from "@/stores/favoriteRooms";
import type { Room, RoomCategory } from "@/types";
import { computed } from "vue";
import { useRouter } from "vue-router";
import StarIcon from "../StarIcon.vue";

const props = withDefaults(defineProps<{
    room: Room;
    roomCategories: RoomCategory[];
    showNavigateButton?: boolean;
}>(), {
    showNavigateButton: true // default value
});

const emit = defineEmits<{
    (e: "pathfind"): void;
    (e: "create-link"): void;
}>();

const roomCategory = computed(() => props.roomCategories.find(
    roomCategory => roomCategory.id === props.room.categoryId
));

const auth = useAuth();
const router = useRouter();
const favoriteRooms = useFavoriteRooms();
const isFavorite = computed(() => favoriteRooms.isFavorite(props.room));

function redirectToLogin() {
    router.push({
        name: "login",
        query: {
            returnUrl: router.currentRoute.value.fullPath
        }
    });
}

</script>

<template>
    <h4>{{ room.name }}</h4>
    <p v-if="roomCategory" class="category">{{ roomCategory.name }}</p>
    <p
        v-if="isFavorite"
    >
        <StarIcon :fill="true" />
        <span class="ms-2">Favorit</span>
    </p>
    <button
        v-if="showNavigateButton"
        class="btn btn-primary me-2"
        @click="emit('pathfind')"
    >Hitta hit</button>
    <template v-if="auth.isLoggedIn">
        <button
            v-if="!isFavorite"
            class="btn btn-success"
            @click="favoriteRooms.markAsFavorite(room)"
        >Favoritmarkera</button>
        <button
            v-else
            class="btn btn-secondary"
            @click="favoriteRooms.unmarkAsFavorite(room)"
        >Ta bort som favorit</button>
    </template>
    <template v-else>
        <div class="mb-3"></div>
        <button class="btn btn-secondary" @click="redirectToLogin">Logga in för att favoritmarkera</button>
    </template>
    <div class="mb-3"></div>
    <button
        class="btn btn-secondary"
        @click="emit('create-link')"
    >Skapa länk</button>
</template>

<style scoped>
.category {
    color: #444;
}
</style>