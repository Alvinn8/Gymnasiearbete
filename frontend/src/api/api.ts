/**
 * The base URL of the API. Ends with a slash.
 */
export const API_BASE = getApiBase();

function getApiBase() {
    return "http://localhost:8080/";
}

async function apiRequest(endpoint: string, options: RequestInit) {
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
        body: JSON.stringify(bodyJson)
    });
}