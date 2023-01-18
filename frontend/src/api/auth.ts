import router from "@/router";
import { apiGet, handleNetworkError } from "./api";

const ITEM_KEY = "mapmaker.auth_token";

export function hasAuthToken() {
    return getAuthToken() != null;
}

export function getAuthToken() {
    return localStorage.getItem(ITEM_KEY);
}

export function setAuthToken(token: string) {
    localStorage.setItem(ITEM_KEY, token);
}

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
 */
export async function isLoggedIn() {
    if (!hasAuthToken()) return false;

    // Fetch the account info endpoint to check if logged in
    try {
        const json = await apiGet("account/info");
        return json.success as boolean;
    } catch {
        handleNetworkError();
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