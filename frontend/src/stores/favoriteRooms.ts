import { apiGet, apiPost, handleError } from "@/api/api";
import type { Room } from "@/types";
import { defineStore } from "pinia";
import { ref } from "vue";
import { useRoute } from "vue-router";
import { useAuth } from "./auth";

export const useFavoriteRooms = defineStore("favorite_rooms", () => {
    const favorites = ref<number[]>();

    const route = useRoute();
    useAuth().checkIfLoggedIn().then(async (isLoggedIn) => {
        if (isLoggedIn) {
            const res = await apiGet(`map/${route.params.map_id}/favorite_room/list`)
                .catch(handleError);
            if (!res) return;
            favorites.value = res.favorites;
        }
    });

    async function markAsFavorite(room: Room) {
        await apiPost(`map/${route.params.map_id}/favorite_room/add`, { roomId: room.id })
            .catch(handleError);
        favorites.value?.push(room.id);
    }

    async function unmarkAsFavorite(room: Room) {
        await apiPost(`map/${route.params.map_id}/favorite_room/remove`, { roomId: room.id })
            .catch(handleError);
        favorites.value = favorites.value?.filter(id => id !== room.id);
    }

    function isFavorite(room: Room) {
        if (!favorites.value) return false;
        return favorites.value.includes(room.id);
    }

    return {
        isFavorite, markAsFavorite, unmarkAsFavorite
    };
});