import { getAuthToken, hasAuthToken } from "./auth";
import Swal from "sweetalert2";

/**
 * The base URL of the API. Ends with a slash.
 */
export const API_BASE = getApiBase();

function getApiBase() {
    return "http://localhost:8080/api/";
}

async function apiRequest(endpoint: string, options: RequestInit) {
    if (hasAuthToken()) {
        if (!options) options = {};
        if (!options.headers) options.headers = {};
        const headers = options.headers as Record<string, string>;
        // Set authorization to the auth token
        headers["Authorization"] = `Bearer ${getAuthToken()}`;
    }
    const response = await fetch(API_BASE + endpoint, options);
    return await response.json();
}

export async function apiGet(endpoint: string) {
    return await apiRequest(endpoint, {
        method: "GET"
    });
}

export async function apiPost(endpoint: string, bodyJson: object) {
    return await apiRequest(endpoint, {
        method: "POST",
        body: JSON.stringify(bodyJson),
        headers: {
            "Content-Type": "application/json"
        }
    });
}

export function handleNetworkError() {
    Swal.fire({
        title: "Nätverksfel",
        icon: "error"
    });
}