import router from "@/router";
import { apiGet, handleError, HttpStatusError } from "./api";

const ITEM_KEY = "mapmaker.auth_token";

/** @deprecated */
export function hasAuthToken() {
    return getAuthToken() != null;
}

/** @deprecated */
export function getAuthToken() {
    return localStorage.getItem(ITEM_KEY);
}

/** @deprecated */
export function setAuthToken(token: string) {
    localStorage.setItem(ITEM_KEY, token);
}

/** @deprecated */
export function removeAuthToken() {
    localStorage.removeItem(ITEM_KEY);
}

/**
 * Check if the user is logged in.
 * 
 * Will perform an HTTP request, so this function should be called sparsely or
 * have its value cached.
 * 
 * @returns 
 * @deprecated
 */
export async function isLoggedIn() {
    if (!hasAuthToken()) return false;

    // Fetch the account info endpoint to check if logged in
    try {
        const json = await apiGet("account/info");
        return json.success as boolean;
    } catch (e) {
        if (!(e instanceof HttpStatusError) || e.response.status !== 401) {
            handleError(e);
        }
        return false;
    }

}

/**
 * Get the page the user should end up at after a successful login.
 */
export function getSuccessfulLoginPage() {
    const returnUrl = router.currentRoute.value.query["returnUrl"];
    if (typeof returnUrl !== "string") {
        // No return url, default to maps
        return { name: "maps" };
    }
    // A return url, let's redirect there
    return {
        path: returnUrl
    };
}