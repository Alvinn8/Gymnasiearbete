import { onMounted, ref, watch } from "vue";
import { defineStore } from "pinia";
import { apiGet, handleError, HttpStatusError } from "@/api/api";

const ITEM_KEY = "mapmaker.auth_token";

export const useAuth = defineStore("auth_token", () => {
    const authToken = ref<string | null>(localStorage.getItem(ITEM_KEY));
    const isLoggedIn = ref<boolean | null>(null);
    const promises: ((isLoggedIn: boolean) => void)[] = [];

    onMounted(validateAuthToken);

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

    watch(isLoggedIn, () => {
        if (typeof isLoggedIn.value === "boolean") {
            for (const promiseCallback of promises) {
                promiseCallback(isLoggedIn.value);
            }
        }
    });

    /**
     * Safely check if the user is logged in or not, and wait until we know for sure
     * before returning.
     */
    function checkIfLoggedIn() {
        if (typeof isLoggedIn.value === "boolean") {
            return Promise.resolve(isLoggedIn.value);
        }
        return new Promise<boolean>((resolve) => {
            promises.push(resolve);
        });
    }
    
    async function validateAuthToken() {
        // Ping the account endpoint to check if logged in
        try {
            const json = await apiGet("account/ping");
            isLoggedIn.value = json.success;
        } catch (e) {
            if (!(e instanceof HttpStatusError) || e.response.status !== 401) {
                handleError(e);
            }
            isLoggedIn.value = false;
        }
    }

    return { authToken, isLoggedIn, validateAuthToken, checkIfLoggedIn };
});

/**
 * Get the page the user should end up at after a successful login.
 */
export function getSuccessfulLoginPage(returnUrl?: string | null) {
    const url = new URL(location.href);
    returnUrl = returnUrl ?? url.searchParams.get("returnUrl");
    if (typeof returnUrl !== "string") {
        // No return url, default to maps
        return { name: "maps" };
    }
    // A return url, let's redirect there
    return {
        path: returnUrl
    };
}