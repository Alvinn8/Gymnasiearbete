const ITEM_KEY = "authentication_token";

export function hasAuthToken() {
    return getAuthToken() != null;
}

export function getAuthToken() {
    return localStorage.getItem(ITEM_KEY);
}

export function setAuthToken(token: string) {
    localStorage.setItem(ITEM_KEY, token);
}