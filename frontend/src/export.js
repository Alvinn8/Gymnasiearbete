// Copy-paste this into the JavaScript console

/**
 * Export a map to a JSON file.
 * 
 * @param {string} apiBase The api base to use. Should end in slash.
 * @param {string} authToken The auth token to use.
 * @param {number} mapId The id of the map to export.
 */
async function exportMap(apiBase, authToken, mapId) {
    async function apiRequest(endpoint) {
        const response = await fetch(apiBase + endpoint, {
            headers: {
                Authorization: `Bearer ${authToken}`
            }
        });
        if (!response.ok) {
            throw new Error("HttpStatusError", response);
        }
        const json = await response.json();
        if (typeof json.success === "boolean" && json.success === false) {
            throw new Error("ApiResponseError", json);
        }

        return json;
    }

    const json = (await apiRequest(`map/${mapId}/info`)).data;
    json.id = mapId;
    json.exportInfo = {
        date: new Date(),
        apiBase
    };

    for (const index in json.mapParts) {
        const mapPartId = json.mapParts[index].id;
        const mapPartJson = await apiRequest(`map/${mapId}/part/${mapPartId}/info`);
        delete mapPartJson.success;
        json.mapParts[index] = mapPartJson;
    }

    const file = new File([JSON.stringify(json)], "map_" + mapId + ".json");
    const url = URL.createObjectURL(file);

    const element = document.createElement("a");
    element.setAttribute("download", file.name);
    element.setAttribute("href", url);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);

    return json;
}