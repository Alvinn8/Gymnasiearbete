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