import { ref, watch } from "vue";
import { defineStore } from "pinia";
import { apiGet, handleError, HttpStatusError } from "@/api/api";

const ITEM_KEY = "mapmaker.auth_token";

export const useAuth = defineStore("auth_token", () => {
    const authToken = ref<string | null>(localStorage.getItem(ITEM_KEY));
    const isLoggedIn = ref(false);
    validateAuthToken();

    watch(
        authToken,
        async newAuthToken => {
            if (newAuthToken) {
                localStorage.setItem(ITEM_KEY, newAuthToken);
                await validateAuthToken();
            } else {
                localStorage.removeItem(ITEM_KEY);
                isLoggedIn.value = false;
            }
        }
    );
    
    async function validateAuthToken() {
    // Fetch the account info endpoint to check if logged in
        try {
            const json = await apiGet("account/info");
            isLoggedIn.value = json.success;
        } catch (e) {
            if (!(e instanceof HttpStatusError) || e.response.status !== 401) {
                handleError(e);
            }
            isLoggedIn.value = false;
        }
    }

    return { authToken, isLoggedIn };
});