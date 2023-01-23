import { getAuthToken, hasAuthToken } from "./auth";
import Swal from "sweetalert2";

/**
 * The base URL of the API. Ends with a slash.
 */
export const API_BASE = getApiBase();

function getApiBase() {
    return "http://localhost:8080/api/";
}

/**
 * An error thrown by api methods when the HTTP request failed without reaching
 * the server, for example due to a lack of an internet connection or the server
 * being down.
 */
export class NetworkError extends Error {
    constructor(message?: string) {
        super(message);
        this.name = "NetworkError";
    }
}

/**
 * An error thrown by api methods when a non-successful HTTP status code is
 * received.
 */
export class HttpStatusError extends Error {
    readonly response: Response;

    constructor(response: Response) {
        super(response.status + ": " + response.statusText);
        this.name = "ApiError";
        this.response = response;
    }
}

/**
 * An error thrown by api methods when a non-successful JSON response is
 * recieved, but the HTTP status code is ok.
 */
export class ApiResponseError extends Error {
    readonly json: any;

    constructor(json: any) {
        super("Non-successful api response. (success = false)");
        this.name = "ApiResponseError";
        this.json = json;
    }
}

async function apiRequest(endpoint: string, options: RequestInit) {
    if (hasAuthToken()) {
        if (!options) options = {};
        if (!options.headers) options.headers = {};
        const headers = options.headers as Record<string, string>;
        // Set authorization to the auth token
        headers["Authorization"] = `Bearer ${getAuthToken()}`;
    }
    let response: Response;
    try {
        response = await fetch(API_BASE + endpoint, options);
    } catch (e) {
        throw new NetworkError((e as Error).message);
    }
    
    if (!response.ok) {
        throw new HttpStatusError(response);
    }

    const json = await response.json();
    if (typeof json.success === "boolean" && json.success === false) {
        throw new ApiResponseError(json);
    }

    return json;
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

/** @deprecated */
export function handleNetworkError() {
    Swal.fire({
        title: "Nätverksfel",
        icon: "error"
    });
}

export function handleError(error: unknown) {
    if (error instanceof NetworkError) {
        Swal.fire({
            title: "Nätverksfel",
            icon: "error"
        });
        return;
    }
    if (error instanceof HttpStatusError) {
        switch (error.response.status) {
        case 500:
            Swal.fire({
                title: "Internt serverfel",
                text: "Detta verkar vara en bugg.",
                icon: "error"
            });
            return;
        case 401:
            Swal.fire({
                title: "Du måste logga in.",
                text: "Du verkar ha landat på en sida som kräver inloggning, utan att behöva logga in. Detta verkar vara en bugg.",
                icon: "error"
            });
            return;
        case 403:
            Swal.fire({
                title: "Du har inte behörighet.",
                text: "Du verkar ha landat på en sida som du inte har behörighet. Detta verkar vara en bugg.",
                icon: "error"
            });
            return;
        }
    }
}

type HttpStatusErrorHandler = [statusCode: number, handler: (response: Response) => any];
type JsonErrorHandler = [predicate: (json: any) => boolean, handler: (json: any) => any];
type ErrorHandlerEntry = HttpStatusErrorHandler | JsonErrorHandler;

type ErrorHandlers = ErrorHandlerEntry[];

/**
 * Create a function to be passed to the {@code .catch(...)} method on a
 * {@link Promise}.
 * 
 * @example
 * ```javascript
 * .catch(errorHandler([
 *     [404, () => console.log("Not found")],
 *     [json => !json.success, () => console.log("Not successful!")]
 * ])
 * ```
 * 
 * @param errorHandlers The error handlers for different HTTP status codes.
 * @returns The error handling function.
 */
export function errorHandler(errorHandlers: ErrorHandlers) {
    return (error: unknown) => {
        if (error instanceof HttpStatusError) {
            const statusCode = error.response.status;
            for (const entry of errorHandlers) {
                if (typeof entry[0] === "number") {
                    const [handlerStatusCode, handler] = entry;
                    if (handlerStatusCode === statusCode) {
                        return handler(error.response);
                    }
                }
            }
        } else if (error instanceof ApiResponseError) {
            for (const entry of errorHandlers) {
                if (typeof entry[0] !== "number") {
                    const [predicate, handler] = entry;
                    if (predicate(error.json)) {
                        return handler(error.json);
                    }
                }
            }
        }
        
        // No specific error handler was called, call the generic handleError method.
        handleError(error);
    };
}